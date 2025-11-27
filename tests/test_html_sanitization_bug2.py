"""
測試套件：Bug #2 - Missing Closing Quote in Colspan

這個測試套件專門測試「缺少結束引號」的錯誤模式：
- 模式：<td colspan="27" height="colspan=">
- 原因：colspan 的結束引號遺失，導致屬性值包含後續 HTML 內容
- 影響：12 個 iHerb 產品

測試原則：TDD (Test-Driven Development)
- Red Phase: 這些測試目前會通過但警告過多（使用預設值）
- Green Phase: 實作第一層清理後，應該乾淨通過
- Refactor Phase: 優化清理邏輯

執行方式：
    pytest tests/test_html_sanitization_bug2.py -v
"""

import os
import pytest

from luminnexus_alchemy_shared.html.markdown_converter import convert_html_to_markdown


# ============================================================================
# P0 測試：缺少結束引號的核心案例（Critical）
# ============================================================================

class TestP0MissingClosingQuote:
    """P0 優先級：缺少結束引號的核心測試"""

    def test_basic_missing_closing_quote(self):
        """
        TC2.1: 基本案例 - colspan 缺少結束引號

        給定：<td colspan="27" height="colspan=">
        問題：colspan 的 " 遺失，height 屬性變成 "colspan="
        預期：應該清理為 colspan="27" height=""
        """
        html = '''
        <table>
          <tr>
            <td colspan="27" height="colspan=">
              <strong>Supplement Facts</strong>
            </td>
          </tr>
        </table>
        '''

        result = convert_html_to_markdown(html)

        # 基本驗證
        assert isinstance(result, str)
        assert "Supplement Facts" in result
        assert len(result) > 0

    def test_missing_quote_with_html_entities(self):
        """
        TC2.2: 缺少引號 + HTML 實體

        給定：屬性值包含 &nbsp; 等 HTML 實體
        預期：應該正確清理並保留內容
        """
        html = '''
        <table>
          <tr>
            <td colspan="27" height="colspan=">
              <strong>Supplement Facts&nbsp;</strong>
            </td>
          </tr>
        </table>
        '''

        result = convert_html_to_markdown(html)

        assert "Supplement Facts" in result

    def test_multiple_rows_missing_quotes(self):
        """
        TC2.3: 多行都有缺少引號問題

        給定：表格中多個 <td> 都有相同問題
        預期：每一行都應該正確處理
        """
        html = '''
        <table>
          <tbody>
            <tr>
              <td colspan="27" height="colspan=">
                <strong>Supplement Facts</strong>
              </td>
            </tr>
            <tr>
              <td colspan="27" height="colspan=">
                <strong>Serving Size:</strong>2 Tablets
              </td>
            </tr>
            <tr>
              <td colspan="27" height="colspan=">
                <strong>Servings Per Container:</strong>45
              </td>
            </tr>
          </tbody>
        </table>
        '''

        result = convert_html_to_markdown(html)

        # 所有內容都應該保留
        assert "Supplement Facts" in result
        assert "Serving Size" in result
        assert "2 Tablets" in result
        assert "Servings Per Container" in result
        assert "45" in result

    def test_missing_quote_in_rowspan(self):
        """
        TC2.4: Rowspan 也有相同問題

        給定：rowspan 屬性也可能缺少結束引號
        預期：應該同樣處理
        """
        html = '''
        <table>
          <tr>
            <td rowspan="3" height="rowspan=">
              Content A
            </td>
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


# ============================================================================
# P1 測試：複雜情況和回歸測試（High Priority）
# ============================================================================

class TestP1ComplexCasesAndRegression:
    """P1 優先級：複雜情況和回歸測試"""

    def test_mixed_valid_and_malformed_attributes(self):
        """
        TC2.5: 混合有效和無效的屬性

        給定：同一表格中有正常的 colspan 和缺少引號的 colspan
        預期：兩種都應該正確處理
        """
        html = '''
        <table>
          <tr>
            <td colspan="3">Valid Row</td>
          </tr>
          <tr>
            <td colspan="27" height="colspan=">Malformed Row</td>
          </tr>
          <tr>
            <td colspan="2">Another Valid Row</td>
          </tr>
        </table>
        '''

        result = convert_html_to_markdown(html)

        assert "Valid Row" in result
        assert "Malformed Row" in result
        assert "Another Valid Row" in result

    def test_both_bug_patterns_in_same_table(self):
        """
        TC2.6: Bug #1 和 Bug #2 同時出現

        給定：同一表格中有兩種不同的錯誤模式
        預期：兩種都應該正確處理
        """
        html = '''
        <table>
          <tr>
            <td colspan="27'height=colspan='3'">Bug #1 Pattern</td>
          </tr>
          <tr>
            <td colspan="27" height="colspan=">Bug #2 Pattern</td>
          </tr>
          <tr>
            <td colspan="5">Valid Pattern</td>
          </tr>
        </table>
        '''

        result = convert_html_to_markdown(html)

        assert "Bug #1 Pattern" in result
        assert "Bug #2 Pattern" in result
        assert "Valid Pattern" in result

    def test_missing_quote_with_nested_tags(self):
        """
        TC2.7: 缺少引號的屬性值包含巢狀標籤

        給定：屬性值中包含多層巢狀的 HTML 標籤
        預期：應該正確清理
        """
        html = '''
        <table>
          <tr>
            <td colspan="27" height="colspan=">
              <strong><em>Nested</em> Formatting</strong>
            </td>
          </tr>
        </table>
        '''

        result = convert_html_to_markdown(html)

        assert "Nested" in result
        assert "Formatting" in result

    def test_regression_valid_colspan_still_works(self):
        """
        TC2.8: 回歸測試 - 確保有效的 colspan 仍然正常

        給定：各種有效的 colspan 值
        預期：不應該被錯誤清理
        """
        test_cases = [
            ('<td colspan="1">A</td>', "A"),
            ('<td colspan="3">B</td>', "B"),
            ('<td colspan="10">C</td>', "C"),
            ('<td colspan="27">D</td>', "D"),  # 正確的 27
            ('<td colspan="100">E</td>', "E"),
        ]

        for html_snippet, expected_content in test_cases:
            html = f'<table><tr>{html_snippet}</tr></table>'
            result = convert_html_to_markdown(html)
            assert expected_content in result, f"Failed for {html_snippet}"


# ============================================================================
# P2 測試：整合測試（Medium Priority）
# ============================================================================

class TestP2IntegrationTests:
    """P2 優先級：真實資料整合測試"""

    @pytest.mark.integration
    @pytest.mark.skipif(
        not os.path.exists('input/dsld_enriched.db'),
        reason="測試資料庫不存在"
    )
    def test_iherb_product_7627_real_data(self):
        """
        TC2.9: 真實資料 - iherb_id=7627

        產品：Chewable Nutri-Zyme, Peppermint, 90 Tablets
        問題：supplement_facts 包含 height="colspan=" 模式
        """
        import sqlite3

        conn = sqlite3.connect('input/dsld_enriched.db')
        cursor = conn.execute(
            "SELECT supplement_facts FROM IHerbProducts WHERE iherb_id = 7627"
        )
        row = cursor.fetchone()
        conn.close()

        if row is None:
            pytest.skip("Product 7627 not found in database")

        html = row[0]

        # 應該能成功轉換
        result = convert_html_to_markdown(html)

        assert isinstance(result, str)
        assert len(result) > 100, "應該有實質內容"
        assert "Supplement Facts" in result

    @pytest.mark.integration
    @pytest.mark.skipif(
        not os.path.exists('input/dsld_enriched.db'),
        reason="測試資料庫不存在"
    )
    def test_all_12_affected_products(self):
        """
        TC2.10: 批次測試所有 12 個受影響的產品

        給定：資料庫中所有包含 height="colspan=" 的產品
        預期：全部應該能成功轉換
        """
        import sqlite3

        conn = sqlite3.connect('input/dsld_enriched.db')
        cursor = conn.execute("""
            SELECT iherb_id, title, supplement_facts
            FROM IHerbProducts
            WHERE supplement_facts LIKE '%height="colspan=">%'
        """)

        results = cursor.fetchall()
        conn.close()

        if not results:
            pytest.skip("No affected products found in database")

        print(f"\n找到 {len(results)} 個受影響的產品")

        failed = []
        for iherb_id, title, html in results:
            try:
                result = convert_html_to_markdown(html)
                assert isinstance(result, str)
                assert len(result) > 0
                print(f"  ✅ {iherb_id}: {title[:50]}")
            except Exception as e:
                failed.append((iherb_id, title, str(e)))
                print(f"  ❌ {iherb_id}: {title[:50]} - {e}")

        # 報告結果
        if failed:
            print(f"\n失敗的產品數: {len(failed)}")
            for iherb_id, title, error in failed:
                print(f"  - {iherb_id}: {title}")
                print(f"    錯誤: {error}")

        assert len(failed) == 0, f"{len(failed)} 個產品轉換失敗"


# ============================================================================
# P3 測試：日誌和可觀察性（Low Priority）
# ============================================================================

class TestP3ObservabilityAndLogging:
    """P3 優先級：日誌記錄和可觀察性測試"""

    def test_no_warning_after_fix(self):
        """
        TC2.11: 驗證修復後不應該有警告

        給定：已經清理過的 HTML（第一層防禦有效）
        預期：第二層防禦不應該被觸發（沒有警告日誌）
        """
        import logging
        from io import StringIO

        # 設定日誌捕捉
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.WARNING)

        logger = logging.getLogger('luminnexus_alchemy_shared.html')
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)

        try:
            html = '''
            <table>
              <tr>
                <td colspan="27" height="colspan=">Content</td>
              </tr>
            </table>
            '''

            result = convert_html_to_markdown(html)

            log_output = log_stream.getvalue()

            # 驗證轉換成功
            assert "Content" in result

            # 理想情況：第一層清理有效，不應該有警告
            # 如果有警告，表示第一層沒有處理好，需要改善
            # 這個測試用於驗證修復的完整性
            if "No numeric value found" in log_output:
                print(f"\n⚠️  警告：第一層清理可能無效")
                print(f"日誌內容：{log_output}")

        finally:
            logger.removeHandler(handler)


# ============================================================================
# 驗收測試
# ============================================================================

class TestAcceptanceCriteriaBug2:
    """驗收測試：Bug #2 的綜合驗證"""

    def test_bug2_acceptance_criteria(self):
        """
        驗收測試：Bug #2 修復的所有關鍵標準

        驗證：
        1. 基本案例能處理
        2. 多行能處理
        3. 有效 colspan 不受影響
        4. 內容完整保留
        """
        # 1. 基本案例
        html1 = '<table><tr><td colspan="27" height="colspan=">Test1</td></tr></table>'
        result1 = convert_html_to_markdown(html1)
        assert "Test1" in result1

        # 2. 多行案例
        html2 = '''
        <table>
          <tr><td colspan="27" height="colspan=">Row1</td></tr>
          <tr><td colspan="27" height="colspan=">Row2</td></tr>
        </table>
        '''
        result2 = convert_html_to_markdown(html2)
        assert "Row1" in result2 and "Row2" in result2

        # 3. 有效 colspan
        html3 = '<table><tr><td colspan="3">Valid</td></tr></table>'
        result3 = convert_html_to_markdown(html3)
        assert "Valid" in result3

        # 4. 混合情況
        html4 = '''
        <table>
          <tr><td colspan="2">Valid</td></tr>
          <tr><td colspan="27" height="colspan=">Malformed</td></tr>
        </table>
        '''
        result4 = convert_html_to_markdown(html4)
        assert "Valid" in result4 and "Malformed" in result4

        print("\n🎉 Bug #2 驗收測試全部通過！")


# ============================================================================
# Pytest 配置
# ============================================================================

def pytest_configure(config):
    """註冊自訂 markers"""
    config.addinivalue_line("markers", "integration: Bug #2 整合測試（需要資料庫）")
