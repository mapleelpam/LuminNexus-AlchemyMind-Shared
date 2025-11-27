# 技術規格：HTML 屬性清理與錯誤處理強化

**文件版本**: 1.0
**建立日期**: 2025-11-27
**狀態**: 提案中 (Proposal)
**優先級**: High
**元件**: `luminnexus_alchemy_shared.html.markdown_converter`

---

## 📋 目錄

1. [問題描述](#問題描述)
2. [根本原因分析](#根本原因分析)
3. [解決方案設計](#解決方案設計)
4. [測試驅動開發計畫](#測試驅動開發計畫)
5. [實作計畫](#實作計畫)
6. [風險評估](#風險評估)
7. [成功指標](#成功指標)

---

## 問題描述

### 問題摘要

HTML to Markdown 轉換器在遇到格式錯誤的 HTML 屬性時會拋出例外，特別是表格儲存格中的 `colspan` 和 `rowspan` 屬性包含無效值時。

### 錯誤訊息

```
ValueError: invalid literal for int() with base 10: "27'height=colspan='3'"
```

### 受影響的資料

- **資料來源**: iHerb 產品資料（從 iherb.com 爬取）
- **資料庫**: `input/dsld_enriched.db`
- **資料表**: `IHerbProducts`
- **已知受影響產品**: iherb_id=1232 (HeartScience™, Multi-Nutrient Complex, 120 Tablets)
- **潛在範圍**: 未知（需要調查）

### 問題 HTML 範例

```html
<!-- 錯誤的 HTML -->
<td colspan="27'height=colspan='3'">
  <strong>Supplement Facts</strong>
</td>

<!-- 預期的 HTML -->
<td colspan="3">
  <strong>Supplement Facts</strong>
</td>
```

### 影響評估

| 面向 | 影響程度 | 說明 |
|-----|---------|------|
| 系統穩定性 | 低 | 有 fallback 機制，不會崩潰 |
| 資料完整性 | 中 | 文字內容保留，但表格結構遺失 |
| 使用者體驗 | 中 | 受影響產品的補充資訊以純文字顯示 |
| 資料品質 | 高 | 需要改善對錯誤資料的容錯能力 |

---

## 根本原因分析

### 技術原因

1. **型別轉換失敗**: 程式碼嘗試將非數字字串轉換為整數
   ```python
   colspan = int(cell.get('colspan'))  # ValueError if value is not numeric
   ```

2. **缺乏輸入驗證**: 沒有在轉換前驗證屬性值的有效性

3. **錯誤處理不足**: 沒有針對特定的屬性解析錯誤進行捕捉

### 資料品質問題

格式錯誤的 HTML 可能來自：

1. **爬蟲問題**: 網頁爬蟲可能錯誤解析 iHerb 的 HTML
2. **來源資料損壞**: iHerb 原始 HTML 本身就有格式錯誤
3. **字串串接錯誤**: 多個屬性在處理過程中被錯誤合併

### 錯誤模式分析

```
原始值: colspan="27'height=colspan='3'"
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
       |       |                    |
       |       |                    +-- 內部引號混亂
       |       +----------------------- 多個屬性被串接
       +------------------------------- 外層引號不匹配
```

---

## 解決方案設計

### 架構概覽

```
HTML Input
    ↓
[1. 屬性清理階段]
    ↓ sanitize_html_attributes()
    ↓ • 正規表達式清理
    ↓ • 提取有效數值
    ↓
[2. HTML 解析階段]
    ↓ BeautifulSoup parsing
    ↓
[3. 屬性提取階段]
    ↓ parse_table_cell()
    ↓ • try-except 包裝
    ↓ • 容錯降級
    ↓
[4. Markdown 轉換階段]
    ↓
Markdown Output
```

### 核心元件設計

#### 1. 屬性清理函式 (新增)

```python
def sanitize_html_attributes(html: str) -> str:
    """
    清理格式錯誤的 HTML 屬性。

    處理的問題類型：
    - 混合引號的屬性值
    - 串接的多個屬性
    - 包含非數字字元的數值屬性

    Args:
        html: 原始 HTML 字串

    Returns:
        清理後的 HTML 字串

    Examples:
        >>> sanitize_html_attributes('<td colspan="27\'height=colspan=\'3\'">Text</td>')
        '<td colspan="3">Text</td>'

        >>> sanitize_html_attributes('<td colspan="abc5xyz">Text</td>')
        '<td colspan="5">Text</td>'

        >>> sanitize_html_attributes('<td colspan="invalid">Text</td>')
        '<td colspan="1">Text</td>'
    """
    import re

    # 策略 1: 提取最右邊的有效數字（通常是最後被串接的正確值）
    def extract_numeric_value(match):
        attr_name = match.group(1)
        attr_value = match.group(2)

        # 找出所有數字
        numbers = re.findall(r'\d+', attr_value)

        if numbers:
            # 使用最後一個數字（最可能是正確值）
            numeric_value = numbers[-1]
        else:
            # 沒有數字則使用預設值
            numeric_value = "1"

        return f'{attr_name}="{numeric_value}"'

    # 清理 colspan 和 rowspan 屬性
    html = re.sub(
        r'(colspan|rowspan)="([^"]*)"',
        extract_numeric_value,
        html,
        flags=re.IGNORECASE
    )

    return html
```

#### 2. 增強的屬性解析 (修改現有程式碼)

```python
def _parse_colspan_rowspan(cell: Tag) -> tuple[int, int]:
    """
    安全地解析表格儲存格的 colspan 和 rowspan 屬性。

    Args:
        cell: BeautifulSoup Tag 物件

    Returns:
        (colspan, rowspan) 的元組，預設值為 (1, 1)
    """
    import logging
    logger = logging.getLogger(__name__)

    # 解析 colspan
    colspan = 1
    if cell.has_attr('colspan'):
        try:
            colspan = int(cell['colspan'])
            # 驗證範圍
            if colspan <= 0:
                logger.warning(f"Invalid colspan value {colspan}, using 1")
                colspan = 1
        except (ValueError, TypeError) as e:
            # 嘗試從字串中提取數字
            import re
            raw_value = str(cell.get('colspan', '1'))
            match = re.search(r'\d+', raw_value)

            if match:
                colspan = int(match.group())
                logger.warning(
                    f"Extracted colspan={colspan} from malformed value: {raw_value}"
                )
            else:
                logger.warning(
                    f"Could not parse colspan '{raw_value}': {e}. Using default value 1"
                )
                colspan = 1

    # 解析 rowspan（相同邏輯）
    rowspan = 1
    if cell.has_attr('rowspan'):
        try:
            rowspan = int(cell['rowspan'])
            if rowspan <= 0:
                logger.warning(f"Invalid rowspan value {rowspan}, using 1")
                rowspan = 1
        except (ValueError, TypeError) as e:
            import re
            raw_value = str(cell.get('rowspan', '1'))
            match = re.search(r'\d+', raw_value)

            if match:
                rowspan = int(match.group())
                logger.warning(
                    f"Extracted rowspan={rowspan} from malformed value: {raw_value}"
                )
            else:
                logger.warning(
                    f"Could not parse rowspan '{raw_value}': {e}. Using default value 1"
                )
                rowspan = 1

    return colspan, rowspan
```

#### 3. 改良的主要轉換函式 (修改現有程式碼)

```python
def convert_html_to_markdown(html: str, config: Optional[ConversionConfig] = None) -> str:
    """
    將 HTML 轉換為 Markdown，具備增強的錯誤處理能力。

    Args:
        html: 要轉換的 HTML 字串
        config: 可選的轉換設定

    Returns:
        Markdown 格式的字串

    Raises:
        不會拋出例外，所有錯誤都會優雅降級
    """
    if not html or not html.strip():
        return ""

    try:
        # 階段 1: 清理屬性
        sanitized_html = sanitize_html_attributes(html)

        # 階段 2: 解析和轉換
        soup = BeautifulSoup(sanitized_html, 'html.parser')
        converter = HTMLToMarkdownConverter(config or ConversionConfig())
        return converter.convert(soup)

    except Exception as e:
        logger.error(f"HTML to Markdown conversion failed: {e}")
        logger.debug(f"Problematic HTML (first 200 chars): {html[:200]}")

        # Fallback: 至少提取純文字
        return _strip_html_tags(html)
```

### 日誌記錄改善

```python
# 結構化日誌記錄
logger.warning(
    "Sanitized malformed HTML attribute",
    extra={
        'attribute_name': 'colspan',
        'original_value': "27'height=colspan='3'",
        'sanitized_value': '3',
        'html_snippet': html[:100],
    }
)
```

---

## 測試驅動開發計畫

### TDD 流程

```
1. Red   → 撰寫失敗的測試
2. Green → 實作最小可行程式碼讓測試通過
3. Refactor → 重構程式碼改善品質
```

### 測試優先順序矩陣

| 優先級 | 測試類別 | 測試數量 | 執行順序 |
|-------|---------|---------|---------|
| P0 (Critical) | 核心錯誤案例 | 5 | 1 |
| P1 (High) | 邊界條件 | 8 | 2 |
| P1 (High) | 回歸測試 | 6 | 3 |
| P2 (Medium) | 整合測試 | 3 | 4 |
| P2 (Medium) | 效能測試 | 3 | 5 |

### 測試案例分類

#### 階段 1: 紅燈測試 (Red Phase) - P0 關鍵測試

這些測試目前會失敗，是驅動實作的核心：

**TC1.1: 混合引號的 Colspan (原始 Bug)**
```python
def test_malformed_colspan_mixed_quotes():
    """
    測試案例：iherb_id=1232 的實際錯誤 HTML

    給定：包含混合引號和串接屬性的 colspan
    當：轉換 HTML 到 Markdown
    則：應該成功轉換不拋出例外
    並且：應該保留文字內容 "Supplement Facts"
    """
    html = '<td colspan="27\'height=colspan=\'3\'"><strong>Supplement Facts</strong></td>'

    # 當前行為：會拋出 ValueError ❌
    # 預期行為：成功轉換 ✅
    result = convert_html_to_markdown(html)

    assert isinstance(result, str)
    assert "Supplement Facts" in result
    assert len(result) > 0
```

**TC1.2: 純垃圾值的 Colspan**
```python
def test_malformed_colspan_garbage_value():
    """
    測試案例：完全無效的 colspan 值

    給定：colspan 值為純文字 "abc123"
    當：轉換 HTML 到 Markdown
    則：應該降級為 colspan=1
    並且：成功提取內容
    """
    html = '<td colspan="abc123">Content</td>'
    result = convert_html_to_markdown(html)

    assert "Content" in result
```

**TC1.3: 部分數字的 Colspan**
```python
@pytest.mark.parametrize("html,description", [
    ('<td colspan="5abc">Content</td>', "數字在開頭"),
    ('<td colspan="abc5">Content</td>', "數字在結尾"),
    ('<td colspan="a5b">Content</td>', "數字在中間"),
    ('<td colspan="5.5">Content</td>', "浮點數而非整數"),
])
def test_malformed_colspan_partial_number(html, description):
    """
    測試案例：數字嵌入在垃圾字元中

    給定：各種包含數字的無效 colspan 值
    當：轉換 HTML 到 Markdown
    則：應該嘗試提取數字部分
    或：降級為預設值 1
    """
    result = convert_html_to_markdown(html)
    assert "Content" in result, f"失敗案例: {description}"
```

**TC1.4: Rowspan 相同問題**
```python
def test_malformed_rowspan_mixed_quotes():
    """
    測試案例：rowspan 有相同的格式錯誤

    給定：rowspan 包含混合引號
    當：轉換包含 rowspan 的表格
    則：應該成功轉換
    並且：保留所有儲存格內容
    """
    html = '''
    <table>
      <tr>
        <td rowspan="27'height=rowspan='3'">Content A</td>
        <td>Content B</td>
      </tr>
      <tr>
        <td>Content C</td>
      </tr>
    </table>
    '''
    result = convert_html_to_markdown(html)

    assert "Content A" in result
    assert "Content B" in result
    assert "Content C" in result
```

**TC1.5: 真實資料整合測試**
```python
@pytest.mark.integration
@pytest.mark.skipif(not os.path.exists('input/dsld_enriched.db'),
                    reason="Test database not available")
def test_iherb_product_1232_real_data():
    """
    測試案例：使用實際資料庫中的 iherb_id=1232

    給定：真實的 iHerb 產品資料
    當：轉換 supplement_facts 欄位
    則：應該成功轉換
    並且：包含關鍵內容（Supplement Facts, Serving Size, Vitamin）
    """
    import sqlite3

    conn = sqlite3.connect('input/dsld_enriched.db')
    cursor = conn.execute(
        "SELECT supplement_facts FROM IHerbProducts WHERE iherb_id = 1232"
    )
    row = cursor.fetchone()

    assert row is not None, "Product 1232 not found in database"
    html = row[0]

    # 這個測試目前會失敗 ❌
    result = convert_html_to_markdown(html)

    assert isinstance(result, str)
    assert len(result) > 100
    assert "Supplement Facts" in result
    assert "Serving Size" in result
```

#### 階段 2: 綠燈測試 (Green Phase) - P1 高優先測試

這些測試用於確保基本功能正確：

**TC2.1: 空值或缺失的屬性**
```python
@pytest.mark.parametrize("html,description", [
    ('<td colspan="">Content</td>', "空字串"),
    ('<td colspan>Content</td>', "只有屬性名稱無值"),
    ('<td colspan=" ">Content</td>', "只有空白"),
    ('<td colspan="0">Content</td>', "零值"),
    ('<td colspan="-1">Content</td>', "負值"),
])
def test_colspan_edge_cases(html, description):
    """
    測試案例：Colspan 屬性的邊界條件

    預期行為：
    - 空值/缺失 → 預設為 1
    - 零 → 預設為 1
    - 負數 → 預設為 1
    """
    result = convert_html_to_markdown(html)
    assert "Content" in result, f"失敗: {description}"
```

**TC2.2: 同時有 Colspan 和 Rowspan 錯誤**
```python
def test_malformed_both_colspan_and_rowspan():
    """
    測試案例：單一儲存格同時有兩個錯誤屬性

    給定：同一個 td 有錯誤的 colspan 和 rowspan
    當：轉換該 HTML
    則：應該清理兩個屬性
    並且：成功提取內容
    """
    html = '<td colspan="2\'foo=\'3\'" rowspan="4\'bar=\'5\'">Complex Cell</td>'
    result = convert_html_to_markdown(html)

    assert "Complex Cell" in result
```

**TC2.3: 深度巢狀的錯誤屬性**
```python
def test_deeply_nested_malformed_attributes():
    """
    測試案例：巢狀表格中的錯誤屬性

    給定：多層巢狀表格，每層都有錯誤屬性
    當：轉換整個結構
    則：應該清理所有層級的屬性
    並且：保留深層內容
    """
    html = '''
    <table>
      <tr>
        <td>
          <table>
            <tr>
              <td colspan="1'x">
                <table>
                  <tr>
                    <td colspan="2'y">Deep content</td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    '''
    result = convert_html_to_markdown(html)
    assert "Deep content" in result
```

**TC2.4: 同一表格中混合有效和無效屬性**
```python
def test_mixed_valid_invalid_in_same_table():
    """
    測試案例：表格中部分儲存格正常，部分儲存格錯誤

    給定：表格包含有效和無效的 colspan 值
    當：轉換表格
    則：有效的 colspan 應該正確解析
    並且：無效的 colspan 應該被清理
    並且：所有內容都應該保留
    """
    html = '''
    <table>
      <tr>
        <td colspan="2">Valid 1</td>
        <td>Normal</td>
      </tr>
      <tr>
        <td colspan="3'bad">Invalid</td>
      </tr>
      <tr>
        <td colspan="4">Valid 2</td>
      </tr>
    </table>
    '''
    result = convert_html_to_markdown(html)

    assert "Valid 1" in result
    assert "Normal" in result
    assert "Invalid" in result
    assert "Valid 2" in result
```

#### 階段 3: 回歸測試 (Regression Tests) - P1 高優先

確保修復不會破壞現有功能：

**TC3.1: 有效的 Colspan 值**
```python
@pytest.mark.parametrize("colspan_value", ["1", "2", "3", "10", "100"])
def test_valid_colspan_values(colspan_value):
    """
    回歸測試：確保有效的 colspan 仍然正確運作

    給定：標準的有效 colspan 值
    當：轉換 HTML
    則：應該正確解析（不被清理邏輯誤判）
    """
    html = f'<td colspan="{colspan_value}">Test Content</td>'
    result = convert_html_to_markdown(html)

    assert "Test Content" in result
```

**TC3.2: 複雜的有效表格**
```python
def test_valid_complex_table():
    """
    回歸測試：標準 HTML 表格應該正常運作

    給定：符合標準的複雜表格結構
    當：轉換表格
    則：所有內容應該保留
    並且：應該產生 Markdown 表格結構
    """
    html = '''
    <table border="1" cellpadding="3" cellspacing="0">
      <thead>
        <tr>
          <th>Header 1</th>
          <th colspan="2">Header 2-3</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Cell 1</td>
          <td>Cell 2</td>
          <td>Cell 3</td>
        </tr>
        <tr>
          <td colspan="3">Merged Cell</td>
        </tr>
      </tbody>
    </table>
    '''
    result = convert_html_to_markdown(html)

    assert "Header 1" in result
    assert "Header 2-3" in result
    assert "Cell 1" in result
    assert "Merged Cell" in result
```

**TC3.3: 巢狀表格**
```python
def test_nested_tables():
    """
    回歸測試：巢狀表格（常見於補充資訊表格）

    給定：表格內包含表格
    當：轉換巢狀結構
    則：外層和內層內容都應該保留
    """
    html = '''
    <table>
      <tr>
        <td>
          Outer content
          <table>
            <tr>
              <td>Inner content</td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    '''
    result = convert_html_to_markdown(html)

    assert "Outer content" in result
    assert "Inner content" in result
```

#### 階段 4: 整合測試 (Integration Tests) - P2 中優先

**TC4.1: 批次測試所有有 Colspan 問題的 iHerb 產品**
```python
@pytest.mark.integration
@pytest.mark.slow
def test_all_iherb_products_with_colspan_issues():
    """
    整合測試：掃描資料庫找出所有潛在問題

    給定：資料庫中所有可能有 colspan 問題的產品
    當：批次轉換所有產品
    則：不應該有任何轉換失敗
    並且：記錄清理統計資料
    """
    import sqlite3

    conn = sqlite3.connect('input/dsld_enriched.db')
    cursor = conn.execute("""
        SELECT iherb_id, title, supplement_facts
        FROM IHerbProducts
        WHERE supplement_facts LIKE '%colspan="%''%'
           OR supplement_facts LIKE '%colspan=''%"%'
        LIMIT 100
    """)

    issues = []
    sanitized_count = 0

    for iherb_id, title, html in cursor.fetchall():
        try:
            result = convert_html_to_markdown(html)
            assert isinstance(result, str)
            assert len(result) > 0

            # 檢查是否有清理發生（透過日誌）
            # 實際實作中應該有機制追蹤這個

        except Exception as e:
            issues.append({
                'iherb_id': iherb_id,
                'title': title,
                'error': str(e)
            })

    # 報告統計
    print(f"\n清理統計:")
    print(f"  測試產品數: {cursor.rowcount}")
    print(f"  轉換失敗數: {len(issues)}")

    assert len(issues) == 0, f"{len(issues)} 個產品轉換失敗"
```

#### 階段 5: 效能與可觀察性測試 (Performance & Observability) - P2 中優先

**TC5.1: 清理的效能開銷**
```python
import time
import statistics

def test_sanitization_performance_overhead():
    """
    效能測試：清理邏輯的效能影響

    給定：大型有效表格（1000 行）
    當：執行 100 次轉換
    則：平均轉換時間應該 < 100ms
    並且：標準差應該 < 20ms（穩定性）
    """
    html = '<table>' + '\n'.join([
        f'<tr><td colspan="2">Row {i}</td><td>Data {i}</td></tr>'
        for i in range(1000)
    ]) + '</table>'

    times = []
    for _ in range(100):
        start = time.perf_counter()
        result = convert_html_to_markdown(html)
        times.append(time.perf_counter() - start)

    avg_time = statistics.mean(times)
    std_dev = statistics.stdev(times)

    print(f"\n效能統計:")
    print(f"  平均時間: {avg_time*1000:.2f}ms")
    print(f"  標準差: {std_dev*1000:.2f}ms")
    print(f"  最小值: {min(times)*1000:.2f}ms")
    print(f"  最大值: {max(times)*1000:.2f}ms")

    assert avg_time < 0.1, f"轉換太慢: {avg_time*1000:.2f}ms"
    assert std_dev < 0.02, f"效能不穩定: {std_dev*1000:.2f}ms"
```

**TC5.2: 日誌記錄驗證**
```python
import logging
from io import StringIO

def test_logging_for_malformed_attributes():
    """
    可觀察性測試：確保錯誤被正確記錄

    給定：包含錯誤屬性的 HTML
    當：轉換 HTML
    則：應該記錄警告訊息
    並且：日誌應該包含有用的除錯資訊
    """
    # 設定日誌捕捉
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.WARNING)

    logger = logging.getLogger('luminnexus_alchemy_shared.html')
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)

    try:
        html = '<td colspan="invalid123">Content</td>'
        result = convert_html_to_markdown(html)

        log_output = log_stream.getvalue()

        # 驗證日誌內容
        assert log_output, "應該有日誌輸出"
        assert "colspan" in log_output.lower(), "日誌應該提到 colspan"
        assert "invalid123" in log_output or "malformed" in log_output.lower(), \
            "日誌應該包含原始值或錯誤描述"

    finally:
        logger.removeHandler(handler)
```

**TC5.3: Fallback 行為驗證**
```python
def test_fallback_to_text_extraction():
    """
    容錯測試：完全無法解析時的 fallback 行為

    給定：嚴重損壞的 HTML
    當：所有清理和解析都失敗
    則：應該 fallback 到純文字提取
    並且：至少保留文字內容
    並且：HTML 標籤應該被移除
    """
    html = '<table><tr><td colspan="!!!"><strong>Important</strong></td></tr></table>'

    result = convert_html_to_markdown(html)

    # 應該有內容
    assert "Important" in result
    # HTML 標籤應該被移除
    assert "<strong>" not in result
    assert "<td>" not in result
```

### 測試執行策略

```bash
# 階段 1: 執行 P0 關鍵測試（應該全部失敗 - Red）
pytest tests/test_html_sanitization.py -k "test_malformed" -v --tb=short

# 階段 2: 實作清理邏輯後執行 P0+P1 測試（應該通過 - Green）
pytest tests/test_html_sanitization.py -k "test_malformed or test_edge_case" -v

# 階段 3: 執行回歸測試（確保沒有破壞現有功能）
pytest tests/test_html_sanitization.py -k "test_valid" -v

# 階段 4: 執行整合測試（需要資料庫）
pytest tests/test_html_sanitization.py -k "integration" -v

# 階段 5: 執行效能測試
pytest tests/test_html_sanitization.py -k "performance" -v --durations=10

# 完整測試套件
pytest tests/test_html_sanitization.py -v --cov=luminnexus_alchemy_shared.html --cov-report=html
```

---

## 實作計畫

### 實作步驟（TDD 循環）

#### 迭代 1: 核心清理功能

```
1. 撰寫 TC1.1 測試（混合引號 colspan）→ Red ❌
2. 實作 sanitize_html_attributes() 最小版本
3. 執行測試 → Green ✅
4. 重構：改善正規表達式可讀性
5. 再次執行測試 → Green ✅
```

#### 迭代 2: 增強屬性解析

```
1. 撰寫 TC1.2-TC1.4 測試（各種錯誤情況）→ Red ❌
2. 實作 _parse_colspan_rowspan()
3. 執行測試 → Green ✅
4. 重構：提取共用邏輯
5. 再次執行測試 → Green ✅
```

#### 迭代 3: 整合與日誌

```
1. 撰寫 TC5.2 測試（日誌記錄）→ Red ❌
2. 加入結構化日誌
3. 執行測試 → Green ✅
4. 重構：改善日誌格式
```

#### 迭代 4: 回歸與整合

```
1. 執行所有回歸測試（應該全部通過）
2. 執行整合測試（TC4.1 真實資料）
3. 修復任何發現的問題
```

#### 迭代 5: 效能優化

```
1. 執行效能測試（TC5.1）
2. 如果效能不符預期，優化實作
3. 再次執行測試確保效能目標達成
```

### 檔案修改清單

| 檔案 | 變更類型 | 說明 |
|-----|---------|------|
| `src/luminnexus_alchemy_shared/html/markdown_converter.py` | 修改 + 新增 | 新增 `sanitize_html_attributes()`<br>修改 `convert_html_to_markdown()`<br>新增 `_parse_colspan_rowspan()` |
| `tests/test_html_sanitization.py` | 新增 | 完整的測試套件 |
| `tests/test_markdown_converter.py` | 修改 | 新增回歸測試 |
| `tests/fixtures/` | 新增 | 測試資料檔案 |
| `docs/html_conversion.md` | 修改 | 更新文件說明限制 |

### 程式碼審查檢查清單

- [ ] 所有 P0 測試通過
- [ ] 所有 P1 測試通過
- [ ] 回歸測試通過（現有功能未受影響）
- [ ] 測試覆蓋率 > 95%
- [ ] 日誌訊息清晰且可操作
- [ ] 效能測試達標（< 100ms）
- [ ] 程式碼符合 ruff 規範
- [ ] 文件已更新

---

## 風險評估

### 技術風險

| 風險 | 可能性 | 影響 | 緩解措施 |
|-----|-------|------|---------|
| 正規表達式過度清理有效 HTML | 中 | 高 | 完整回歸測試套件；保守的清理策略 |
| 效能開銷影響大型文件轉換 | 低 | 中 | 效能測試；快取編譯的正規表達式 |
| 無法處理未知的錯誤模式 | 中 | 中 | 多層 fallback 機制；詳細日誌記錄 |
| BeautifulSoup 解析行為改變 | 低 | 中 | 在清理階段處理，不依賴解析器容錯 |

### 資料風險

| 風險 | 可能性 | 影響 | 緩解措施 |
|-----|-------|------|---------|
| 資料庫中有更多未知錯誤案例 | 高 | 中 | 整合測試掃描所有資料；監控日誌 |
| 清理邏輯改變資料語意 | 低 | 高 | 保守清理策略；只處理明確錯誤 |
| 爬蟲持續產生新的錯誤模式 | 中 | 中 | 可觀察性設計；定期審查日誌 |

### 營運風險

| 風險 | 可能性 | 影響 | 緩解措施 |
|-----|-------|------|---------|
| 部署後發現未測試到的邊界案例 | 中 | 低 | 分階段部署；監控錯誤率 |
| 影響使用此函式庫的其他專案 | 低 | 高 | 向後相容設計；充分測試 |

---

## 成功指標

### 功能指標

- ✅ iherb_id=1232 成功轉換（無例外）
- ✅ 所有 P0+P1 測試通過
- ✅ 測試覆蓋率 ≥ 95%
- ✅ 零回歸問題（所有現有測試通過）

### 品質指標

- ✅ 資料庫批次測試成功率 100%
- ✅ 平均轉換時間 < 100ms
- ✅ 記憶體使用量 < 100MB (大型文件)
- ✅ 程式碼符合 ruff 檢查

### 營運指標

- ✅ 部署後 7 天內零崩潰
- ✅ 清理日誌頻率 < 1%（大部分資料是乾淨的）
- ✅ TheWeaver 專案整合成功

### 驗收測試

```python
def test_acceptance_criteria():
    """
    驗收測試：所有成功指標的最終驗證

    這個測試代表專案交付的最低標準。
    """
    # 1. 原始 bug 已修復
    html_1232 = '<td colspan="27\'height=colspan=\'3\'">Supplement Facts</td>'
    result = convert_html_to_markdown(html_1232)
    assert "Supplement Facts" in result

    # 2. 有效 HTML 仍然正常運作
    valid_html = '<td colspan="3">Valid</td>'
    result = convert_html_to_markdown(valid_html)
    assert "Valid" in result

    # 3. 完全無效的輸入有 fallback
    garbage_html = '<td colspan="!@#$%">Content</td>'
    result = convert_html_to_markdown(garbage_html)
    assert "Content" in result

    # 4. 效能可接受
    large_html = '<table>' + ('<tr><td>X</td></tr>' * 1000) + '</table>'
    start = time.perf_counter()
    result = convert_html_to_markdown(large_html)
    elapsed = time.perf_counter() - start
    assert elapsed < 0.1

    print("\n🎉 所有驗收標準已達成！")
```

---

## 附錄

### A. 參考文件

- [Bug Report](/tmp/html_parser_bug_report_20251127.md)
- [Test Cases](/tmp/html_to_markdown_test_cases.md)
- [TheWeaver Repository](https://github.com/LuminNexus/LuminNexus-AlchemyMind-TheWeaver)
- [HTML5 Specification](https://html.spec.whatwg.org/)

### B. 相關議題

- Issue #TBD: HTML Attribute Sanitization Implementation
- Issue #TBD: Improve Data Quality Monitoring

### C. 決策記錄

| 日期 | 決策 | 理由 |
|-----|------|------|
| 2025-11-27 | 採用雙層防禦策略（清理 + 錯誤處理） | 最大化穩健性 |
| 2025-11-27 | 優先提取最右邊的數字 | 根據錯誤模式分析，最右邊最可能是正確值 |
| 2025-11-27 | 無效值預設為 1 而非拋出例外 | 符合函式庫的容錯設計哲學 |

### D. 審查記錄

| 日期 | 審查者 | 狀態 | 意見 |
|-----|-------|------|------|
| 2025-11-27 | - | 待審查 | - |

---

**文件狀態**: 待審查
**下一步**: 與團隊討論測試計畫，確認後開始實作
