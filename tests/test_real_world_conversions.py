"""Integration tests using real-world iHerb data with LLM-based validation.

These tests use actual HTML content from iHerb products to validate:
1. HTML to Markdown conversion quality
2. HTML table to ASCII table rendering quality

Since output format can vary (especially markdown style choices), we use
an LLM-based validation approach where the LLM evaluates if the conversion
is semantically correct, readable, and preserves all information.
"""

import pytest

from luminnexus_alchemy_shared.html import convert_html_to_markdown, convert_html_to_table
from tests.fixtures.iherb_sample_data import (
    PRODUCT_147956_DESCRIPTION,
    PRODUCT_147956_SUGGESTED_USE,
    PRODUCT_147956_SUPPLEMENT_FACTS,
    PRODUCT_128082_DESCRIPTION,
    PRODUCT_128082_SUGGESTED_USE,
    PRODUCT_128082_SUPPLEMENT_FACTS,
    PRODUCT_116921_SUPPLEMENT_FACTS,
    PRODUCT_113511_SUPPLEMENT_FACTS,
    PRODUCT_129950_SUPPLEMENT_FACTS,
    TEST_CASES,
)


class TestRealWorldHTMLToMarkdown:
    """Test HTML to Markdown conversion with real iHerb product data."""

    def test_product_147956_description_conversion(self):
        """Test conversion of Lemme Debloat probiotic gummy description."""
        result = convert_html_to_markdown(PRODUCT_147956_DESCRIPTION)

        # Basic structural assertions
        assert result is not None
        assert len(result) > 0

        # Check for key content preservation (exact format may vary)
        assert "Prebiotic" in result
        assert "Probiotic" in result
        assert "Digestive Support" in result
        assert "Gluten-Free" in result

        # Check that lists were converted (should have bullet markers or numbers)
        assert "-" in result or "*" in result or "•" in result

        # Check HTML entities decoded
        assert "&amp;" not in result

        # Store for LLM validation
        self._store_for_llm_validation(
            test_name="product_147956_description",
            input_html=PRODUCT_147956_DESCRIPTION,
            output_markdown=result,
            validation_criteria=TEST_CASES[0]["test_scenarios"][0]["validation_criteria"],
        )

    def test_product_147956_suggested_use_conversion(self):
        """Test conversion of probiotic gummy usage instructions."""
        result = convert_html_to_markdown(PRODUCT_147956_SUGGESTED_USE)

        # Basic assertions
        assert result is not None
        assert "2 gummies daily" in result or "2 gummies" in result
        assert "physician" in result

        self._store_for_llm_validation(
            test_name="product_147956_suggested_use",
            input_html=PRODUCT_147956_SUGGESTED_USE,
            output_markdown=result,
            validation_criteria=TEST_CASES[0]["test_scenarios"][1]["validation_criteria"],
        )

    def test_product_128082_description_conversion(self):
        """Test conversion of B vitamin complex description."""
        result = convert_html_to_markdown(PRODUCT_128082_DESCRIPTION)

        # Basic assertions
        assert result is not None
        assert "Vegetarian" in result
        assert "Gluten Free" in result
        assert "methylation" in result

        # Check for list markers
        assert "-" in result or "*" in result

        # Check for trademark symbol
        assert "™" in result or "TM" in result

        self._store_for_llm_validation(
            test_name="product_128082_description",
            input_html=PRODUCT_128082_DESCRIPTION,
            output_markdown=result,
            validation_criteria=TEST_CASES[1]["test_scenarios"][0]["validation_criteria"],
        )

    def test_product_128082_suggested_use_conversion(self):
        """Test conversion of B vitamin usage instructions."""
        result = convert_html_to_markdown(PRODUCT_128082_SUGGESTED_USE)

        # Basic assertions
        assert result is not None
        assert "1 capsule daily" in result or "1 capsule" in result
        assert "healthcare practitioner" in result

        self._store_for_llm_validation(
            test_name="product_128082_suggested_use",
            input_html=PRODUCT_128082_SUGGESTED_USE,
            output_markdown=result,
            validation_criteria=TEST_CASES[1]["test_scenarios"][1]["validation_criteria"],
        )

    def _store_for_llm_validation(self, test_name, input_html, output_markdown, validation_criteria):
        """Store test results for later LLM-based validation.

        This is a placeholder for the LLM validation framework.
        In actual implementation, this would store results to be evaluated
        by an LLM agent that checks if the conversion is semantically correct.
        """
        # TODO: Implement actual LLM validation storage
        # For now, just ensure the data is structured correctly
        validation_data = {
            "test_name": test_name,
            "input_html": input_html,
            "output_markdown": output_markdown,
            "validation_criteria": validation_criteria,
        }
        # This would be sent to an LLM validation agent
        pass


class TestRealWorldHTMLToTable:
    """Test HTML table to ASCII table conversion with real iHerb data."""

    def test_product_147956_supplement_facts_table(self):
        """Test conversion of probiotic gummy supplement facts table to Rich ASCII table."""
        result = convert_html_to_table(PRODUCT_147956_SUPPLEMENT_FACTS)

        # Basic assertions
        assert result is not None
        assert len(result) > 0

        # Check for key content
        assert "Supplement Facts" in result
        assert "2 Gummies" in result  # Serving size
        assert "Calories" in result
        assert "Probiotic Blend" in result
        assert "CFU" in result  # Colony forming units

        # Check that it looks like a table (has box drawing or borders)
        # Rich tables typically use box characters
        assert any(char in result for char in ["─", "│", "┌", "┐", "+", "|", "-"])

        self._store_for_llm_validation(
            test_name="product_147956_supplement_facts_table",
            input_html=PRODUCT_147956_SUPPLEMENT_FACTS,
            output_table=result,
            validation_criteria=TEST_CASES[0]["test_scenarios"][2]["validation_criteria"],
        )

    def test_product_128082_supplement_facts_table(self):
        """Test conversion of B vitamin supplement facts table to Rich ASCII table."""
        result = convert_html_to_table(PRODUCT_128082_SUPPLEMENT_FACTS)

        # Basic assertions
        assert result is not None
        assert len(result) > 0

        # Check for key content
        assert "Supplement Facts" in result
        assert "1 Capsule" in result  # Serving size
        assert "Riboflavin" in result or "B" in result
        assert "41,667%" in result or "41667" in result  # High percentage DV
        assert "mcg" in result or "mg" in result

        # Check for table structure
        assert any(char in result for char in ["─", "│", "┌", "┐", "+", "|", "-"])

        self._store_for_llm_validation(
            test_name="product_128082_supplement_facts_table",
            input_html=PRODUCT_128082_SUPPLEMENT_FACTS,
            output_table=result,
            validation_criteria=TEST_CASES[1]["test_scenarios"][2]["validation_criteria"],
        )

    def test_empty_table_input(self):
        """Test that empty/null input is handled gracefully."""
        assert convert_html_to_table(None) == ""
        assert convert_html_to_table("") == ""
        assert convert_html_to_table("<p>No table</p>") == ""

    def _store_for_llm_validation(self, test_name, input_html, output_table, validation_criteria):
        """Store test results for later LLM-based validation."""
        validation_data = {
            "test_name": test_name,
            "input_html": input_html,
            "output_table": output_table,
            "validation_criteria": validation_criteria,
        }
        # This would be sent to an LLM validation agent
        pass


class TestEdgeCasesFromRealData:
    """Test edge cases discovered in real iHerb data."""

    def test_html_entities_in_description(self):
        """Test that HTML entities like &amp; are properly decoded."""
        result = convert_html_to_markdown(PRODUCT_147956_DESCRIPTION)
        # &amp; should become &
        assert "&amp;" not in result
        assert "&" in result  # Should be decoded

    def test_trademark_symbols_preserved(self):
        """Test that trademark symbols (™) are preserved."""
        result = convert_html_to_markdown(PRODUCT_128082_DESCRIPTION)
        # Should preserve or convert trademark symbols
        assert "™" in result or "TM" in result or "Benefits Line" in result

    def test_table_with_colspan(self):
        """Test tables with colspan attribute (common in supplement facts)."""
        # The supplement facts table has colspan="3" for headers
        result = convert_html_to_table(PRODUCT_147956_SUPPLEMENT_FACTS)
        # Should handle colspan gracefully (may span cells or merge)
        assert "Supplement Facts" in result
        assert "Serving Size" in result

    def test_nested_formatting_in_table_cells(self):
        """Test table cells containing nested HTML (bold, sup, etc)."""
        result = convert_html_to_table(PRODUCT_147956_SUPPLEMENT_FACTS)
        # Should extract text from nested tags
        assert "LactoSpore" in result or "Probiotic" in result  # Even with ® symbols
        assert "Supplement Facts" in result  # Even though wrapped in <strong>

    def test_non_breaking_spaces(self):
        """Test that &nbsp; is properly handled."""
        result = convert_html_to_markdown(PRODUCT_128082_DESCRIPTION)
        # Should not have raw &nbsp; in output
        assert "&nbsp;" not in result

    def test_high_percentage_values(self):
        """Test that very high percentage daily values are preserved."""
        result = convert_html_to_table(PRODUCT_128082_SUPPLEMENT_FACTS)
        # Should handle 41,667% correctly
        assert "41,667" in result or "41667" in result


class TestAdditionalSupplementFactsTables:
    """Test additional supplement facts tables with diverse structures."""

    def test_product_116921_minerals_table(self):
        """Test mineral supplement with multiple nutrients (Product 116921)."""
        result = convert_html_to_markdown(PRODUCT_116921_SUPPLEMENT_FACTS)

        # Should have proper markdown table structure
        assert "| --- |" in result or "|---|" in result

        # Check for key minerals
        assert "Vitamin C" in result
        assert "Calcium" in result
        assert "Magnesium" in result
        assert "Zinc" in result
        assert "Selenium" in result

        # Check amounts
        assert "500 mg" in result
        assert "230 mg" in result

        # Check percentages
        assert "556%" in result
        assert "364%" in result

    def test_product_113511_simple_table(self):
        """Test simple single-ingredient supplement (Product 113511)."""
        result = convert_html_to_markdown(PRODUCT_113511_SUPPLEMENT_FACTS)

        # Should have proper markdown table structure
        assert "| --- |" in result or "|---|" in result

        # Check content
        assert "Quercetin" in result
        assert "500 mg" in result
        assert "Daily Value not established" in result or "*" in result

    def test_product_129950_multi_serving_table(self):
        """Test complex multi-serving table (Product 129950 - protein powder)."""
        result = convert_html_to_markdown(PRODUCT_129950_SUPPLEMENT_FACTS)

        # Should have proper markdown table structure
        assert "| --- |" in result or "|---|" in result

        # Check for multi-serving columns
        assert "1 Scoop" in result
        assert "2 Scoops" in result
        assert "3 Scoops" in result

        # Check for different serving amounts
        assert "5.5 g" in result or "5.5g" in result
        assert "11 g" in result or "11g" in result

        # Check nutrients scale correctly
        assert "Calories" in result
        assert "20" in result  # 1 scoop calories
        assert "35" in result  # 2 scoops calories
        assert "55" in result  # 3 scoops calories

        # Check amino acids section
        assert "Amino Acid Profile" in result or "L-Leucine" in result

    def test_all_new_tables_have_headers(self):
        """Ensure all new supplement facts tables generate proper headers."""
        test_data = [
            (PRODUCT_116921_SUPPLEMENT_FACTS, "116921"),
            (PRODUCT_113511_SUPPLEMENT_FACTS, "113511"),
            (PRODUCT_129950_SUPPLEMENT_FACTS, "129950"),
        ]

        for html, product_id in test_data:
            result = convert_html_to_markdown(html)
            # All should have table separator
            assert ("| --- |" in result or "|---|" in result), \
                f"Product {product_id} missing table separator"
            # All should have "Amount Per Serving" or similar header
            assert ("Amount Per Serving" in result or "Serving Size" in result), \
                f"Product {product_id} missing expected headers"
