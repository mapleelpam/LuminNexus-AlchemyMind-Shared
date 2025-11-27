"""
測試套件：HTML 屬性清理與錯誤處理

這個測試套件遵循 TDD 原則，目前大部分測試會失敗（Red Phase）。
實作清理邏輯後，這些測試應該通過（Green Phase）。

測試分類：
- P0 (Critical): 核心錯誤案例，必須修復
- P1 (High): 邊界條件和回歸測試
- P2 (Medium): 整合測試和效能測試

執行方式：
    pytest tests/test_html_sanitization.py -v
    pytest tests/test_html_sanitization.py -k "P0" -v  # 只執行 P0 測試
"""

import os
import time
import logging
import statistics
from io import StringIO

import pytest

from luminnexus_alchemy_shared.html.markdown_converter import convert_html_to_markdown


# ============================================================================
# P0 測試：核心錯誤案例（Critical）
# ============================================================================

class TestP0CriticalCases:
    """P0 優先級：這些是驅動實作的核心測試，目前應該失敗"""

    def test_malformed_colspan_mixed_quotes(self):
        """
        TC1.1: 測試混合引號和串接屬性的 colspan

        這是原始 bug (iherb_id=1232) 的核心問題。

        給定：包含混合引號的 colspan 屬性
        當：轉換 HTML 到 Markdown
        則：應該成功轉換，不拋出 ValueError
        並且：文字內容 "Supplement Facts" 應該保留
        """
        html = '''
        <table>
          <tr>
            <td colspan="27'height=colspan='3'">
              <strong>Supplement Facts</strong>
            </td>
          </tr>
        </table>
        '''

        # 當前行為：會拋出 ValueError ❌
        # 預期行為：成功轉換 ✅
        result = convert_html_to_markdown(html)

        assert isinstance(result, str), "應該回傳字串"
        assert "Supplement Facts" in result, "應該保留文字內容"
        assert len(result) > 0, "不應該回傳空字串"

    def test_malformed_colspan_garbage_value(self):
        """
        TC1.2: 測試完全無效的 colspan 值

        給定：colspan 值為純文字 "abc123"
        當：轉換 HTML 到 Markdown
        則：應該降級為 colspan=1（預設值）
        並且：成功提取內容
        """
        html = '<td colspan="abc123">Content</td>'
        result = convert_html_to_markdown(html)

        assert isinstance(result, str)
        assert "Content" in result

    @pytest.mark.parametrize("html,description", [
        ('<td colspan="5abc">Content</td>', "數字在開頭"),
        ('<td colspan="abc5">Content</td>', "數字在結尾"),
        ('<td colspan="a5b">Content</td>', "數字在中間"),
        ('<td colspan="5.5">Content</td>', "浮點數而非整數"),
    ])
    def test_malformed_colspan_partial_number(self, html, description):
        """
        TC1.3: 測試數字嵌入在垃圾字元中

        給定：各種包含數字的無效 colspan 值
        當：轉換 HTML 到 Markdown
        則：應該嘗試提取數字部分或降級為預設值
        """
        result = convert_html_to_markdown(html)
        assert "Content" in result, f"失敗案例: {description}"

    def test_malformed_rowspan_mixed_quotes(self):
        """
        TC1.4: 測試 rowspan 有相同的格式錯誤

        給定：rowspan 包含混合引號
        當：轉換包含 rowspan 的表格
        則：應該成功轉換並保留所有儲存格內容
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

    @pytest.mark.integration
    @pytest.mark.skipif(
        not os.path.exists('input/dsld_enriched.db'),
        reason="測試資料庫不存在"
    )
    def test_iherb_product_1232_real_data(self):
        """
        TC1.5: 使用實際資料庫中的 iherb_id=1232

        給定：真實的 iHerb 產品資料
        當：轉換 supplement_facts 欄位
        則：應該成功轉換並包含關鍵內容
        """
        import sqlite3

        conn = sqlite3.connect('input/dsld_enriched.db')
        cursor = conn.execute(
            "SELECT supplement_facts FROM IHerbProducts WHERE iherb_id = 1232"
        )
        row = cursor.fetchone()

        assert row is not None, "資料庫中找不到 Product 1232"
        html = row[0]

        # 這個測試目前會失敗 ❌
        result = convert_html_to_markdown(html)

        assert isinstance(result, str)
        assert len(result) > 100, "應該有實質內容"
        assert "Supplement Facts" in result
        assert "Serving Size" in result


# ============================================================================
# P1 測試：邊界條件和回歸測試（High Priority）
# ============================================================================

class TestP1EdgeCasesAndRegression:
    """P1 優先級：邊界條件處理和回歸測試"""

    @pytest.mark.parametrize("html,description", [
        ('<td colspan="">Content</td>', "空字串"),
        ('<td colspan>Content</td>', "只有屬性名稱無值"),
        ('<td colspan=" ">Content</td>', "只有空白"),
        ('<td colspan="0">Content</td>', "零值"),
        ('<td colspan="-1">Content</td>', "負值"),
    ])
    def test_colspan_edge_cases(self, html, description):
        """
        TC2.1: Colspan 屬性的邊界條件

        預期行為：
        - 空值/缺失 → 預設為 1
        - 零 → 預設為 1
        - 負數 → 預設為 1
        """
        result = convert_html_to_markdown(html)
        assert "Content" in result, f"失敗: {description}"

    def test_malformed_both_colspan_and_rowspan(self):
        """
        TC2.2: 同一儲存格同時有兩個錯誤屬性

        給定：同一個 td 有錯誤的 colspan 和 rowspan
        當：轉換該 HTML
        則：應該清理兩個屬性並成功提取內容
        """
        html = '<td colspan="2\'foo=\'3\'" rowspan="4\'bar=\'5\'">Complex Cell</td>'
        result = convert_html_to_markdown(html)

        assert "Complex Cell" in result

    def test_deeply_nested_malformed_attributes(self):
        """
        TC2.3: 巢狀表格中的錯誤屬性

        給定：多層巢狀表格，每層都有錯誤屬性
        當：轉換整個結構
        則：應該清理所有層級的屬性並保留深層內容
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

    def test_mixed_valid_invalid_in_same_table(self):
        """
        TC2.4: 表格中混合有效和無效屬性

        給定：表格包含有效和無效的 colspan 值
        當：轉換表格
        則：所有內容都應該保留
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

    # 回歸測試
    @pytest.mark.parametrize("colspan_value", ["1", "2", "3", "10", "100"])
    def test_valid_colspan_values(self, colspan_value):
        """
        TC3.1: 回歸測試 - 確保有效的 colspan 仍然正確運作

        給定：標準的有效 colspan 值
        當：轉換 HTML
        則：應該正確解析（不被清理邏輯誤判）
        """
        html = f'<td colspan="{colspan_value}">Test Content</td>'
        result = convert_html_to_markdown(html)

        assert "Test Content" in result

    def test_valid_complex_table(self):
        """
        TC3.2: 回歸測試 - 標準 HTML 表格應該正常運作

        給定：符合標準的複雜表格結構
        當：轉換表格
        則：所有內容應該保留
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

    def test_nested_tables(self):
        """
        TC3.3: 回歸測試 - 巢狀表格（常見於補充資訊表格）

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


# ============================================================================
# P2 測試：整合測試和效能測試（Medium Priority）
# ============================================================================

class TestP2IntegrationAndPerformance:
    """P2 優先級：整合測試、效能測試、可觀察性測試"""

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.skipif(
        not os.path.exists('input/dsld_enriched.db'),
        reason="測試資料庫不存在"
    )
    def test_all_iherb_products_with_colspan_issues(self):
        """
        TC4.1: 批次測試所有有 Colspan 問題的 iHerb 產品

        給定：資料庫中所有可能有 colspan 問題的產品
        當：批次轉換所有產品
        則：不應該有任何轉換失敗
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
        total_count = 0

        for iherb_id, title, html in cursor.fetchall():
            total_count += 1
            try:
                result = convert_html_to_markdown(html)
                assert isinstance(result, str)
                assert len(result) > 0
            except Exception as e:
                issues.append({
                    'iherb_id': iherb_id,
                    'title': title,
                    'error': str(e)
                })

        # 報告統計
        if issues:
            print(f"\n清理統計:")
            print(f"  測試產品數: {total_count}")
            print(f"  轉換失敗數: {len(issues)}")
            for issue in issues[:5]:  # 只顯示前 5 個
                print(f"  - {issue['iherb_id']}: {issue['title'][:50]}")
                print(f"    錯誤: {issue['error']}")

        assert len(issues) == 0, f"{len(issues)} 個產品轉換失敗"

    @pytest.mark.performance
    def test_sanitization_performance_overhead(self):
        """
        TC5.1: 清理邏輯的效能影響

        給定：大型有效表格（1000 行）
        當：執行 100 次轉換
        則：平均轉換時間應該 < 100ms
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

    @pytest.mark.performance
    def test_large_document_performance(self):
        """
        TC5.2: 大型文件效能測試

        給定：非常大的 HTML 文件（10000 行）
        當：轉換文件
        則：應該在合理時間內完成（< 5 秒）
        """
        large_html = '<table>' + ('<tr><td>A</td></tr>' * 10000) + '</table>'

        start = time.perf_counter()
        result = convert_html_to_markdown(large_html)
        elapsed = time.perf_counter() - start

        print(f"\n大型文件轉換時間: {elapsed:.2f}s")

        assert elapsed < 5.0, f"大型文件轉換太慢: {elapsed:.2f}s"
        assert isinstance(result, str)

    def test_logging_for_malformed_attributes(self):
        """
        TC5.3: 可觀察性測試 - 確保錯誤被正確記錄

        給定：包含錯誤屬性的 HTML
        當：轉換 HTML
        則：應該記錄警告訊息並包含有用的除錯資訊
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

            # 驗證至少有轉換結果
            assert isinstance(result, str)
            assert "Content" in result

            # 如果有日誌輸出，驗證內容
            # 注意：這個斷言可能在實作前不會觸發
            if log_output:
                assert "colspan" in log_output.lower() or "malformed" in log_output.lower(), \
                    "日誌應該提到 colspan 或 malformed"

        finally:
            logger.removeHandler(handler)

    def test_fallback_to_text_extraction(self):
        """
        TC5.4: 容錯測試 - 完全無法解析時的 fallback 行為

        給定：嚴重損壞的 HTML
        當：所有清理和解析都失敗
        則：應該 fallback 到純文字提取並移除 HTML 標籤
        """
        html = '<table><tr><td colspan="!!!"><strong>Important</strong></td></tr></table>'

        result = convert_html_to_markdown(html)

        # 應該有內容
        assert "Important" in result
        # HTML 標籤應該被移除（或轉換為 markdown）
        # 注意：具體行為取決於實作


# ============================================================================
# 驗收測試
# ============================================================================

class TestAcceptanceCriteria:
    """最終驗收測試：代表專案交付的最低標準"""

    def test_acceptance_all_criteria(self):
        """
        驗收測試：所有成功指標的綜合驗證

        這個測試涵蓋所有關鍵的驗收標準。
        """
        # 1. 原始 bug 已修復
        html_1232 = '<td colspan="27\'height=colspan=\'3\'">Supplement Facts</td>'
        result = convert_html_to_markdown(html_1232)
        assert "Supplement Facts" in result, "原始 bug 未修復"

        # 2. 有效 HTML 仍然正常運作
        valid_html = '<td colspan="3">Valid</td>'
        result = convert_html_to_markdown(valid_html)
        assert "Valid" in result, "有效 HTML 處理失敗（回歸問題）"

        # 3. 完全無效的輸入有 fallback
        garbage_html = '<td colspan="!@#$%">Content</td>'
        result = convert_html_to_markdown(garbage_html)
        assert "Content" in result, "Fallback 機制失敗"

        # 4. 效能可接受
        large_html = '<table>' + ('<tr><td>X</td></tr>' * 1000) + '</table>'
        start = time.perf_counter()
        result = convert_html_to_markdown(large_html)
        elapsed = time.perf_counter() - start
        assert elapsed < 0.2, f"效能不達標: {elapsed*1000:.2f}ms"

        print("\n✅ 所有驗收標準已達成！")


# ============================================================================
# Pytest 配置
# ============================================================================

def pytest_configure(config):
    """註冊自訂 markers"""
    config.addinivalue_line("markers", "integration: 整合測試（需要資料庫）")
    config.addinivalue_line("markers", "slow: 執行時間較長的測試")
    config.addinivalue_line("markers", "performance: 效能測試")
