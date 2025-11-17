"""Tests for HTML to Markdown converter."""

import pytest

from luminnexus_alchemy_shared.html import (
    ConversionConfig,
    HTMLToMarkdownConverter,
    convert_html_to_markdown,
)


class TestHTMLToMarkdownConverter:
    """Tests for HTMLToMarkdownConverter class."""

    def test_simple_paragraph(self):
        """Test conversion of simple paragraph."""
        html = "<p>Hello World</p>"
        result = convert_html_to_markdown(html)
        assert "Hello World" in result

    def test_bold_text(self):
        """Test conversion of bold text."""
        html = "<p>Hello <strong>World</strong></p>"
        result = convert_html_to_markdown(html)
        assert "**World**" in result

    def test_italic_text(self):
        """Test conversion of italic text."""
        html = "<p>Hello <em>World</em></p>"
        result = convert_html_to_markdown(html)
        assert "*World*" in result

    def test_heading(self):
        """Test conversion of heading."""
        html = "<h1>Title</h1>"
        result = convert_html_to_markdown(html)
        assert "# Title" in result

    def test_unordered_list(self):
        """Test conversion of unordered list."""
        html = "<ul><li>Item 1</li><li>Item 2</li></ul>"
        result = convert_html_to_markdown(html)
        assert "- Item 1" in result
        assert "- Item 2" in result

    def test_ordered_list(self):
        """Test conversion of ordered list."""
        html = "<ol><li>First</li><li>Second</li></ol>"
        result = convert_html_to_markdown(html)
        assert "1. First" in result
        assert "2. Second" in result

    def test_link(self):
        """Test conversion of link."""
        html = '<a href="https://example.com">Click here</a>'
        result = convert_html_to_markdown(html)
        assert "[Click here](https://example.com)" in result

    def test_table(self):
        """Test conversion of table."""
        html = """
        <table>
            <tr><th>Name</th><th>Age</th></tr>
            <tr><td>Alice</td><td>30</td></tr>
            <tr><td>Bob</td><td>25</td></tr>
        </table>
        """
        result = convert_html_to_markdown(html)
        assert "| Name | Age |" in result
        assert "| --- | --- |" in result
        assert "| Alice | 30 |" in result

    def test_table_with_thead_tbody(self):
        """Test conversion of table with thead and tbody."""
        html = """
        <table>
            <thead>
                <tr><th>Product</th><th>Price</th></tr>
            </thead>
            <tbody>
                <tr><td>Apple</td><td>$1.00</td></tr>
                <tr><td>Orange</td><td>$1.50</td></tr>
            </tbody>
        </table>
        """
        result = convert_html_to_markdown(html)
        # Should have header row
        assert "| Product | Price |" in result
        # Should have separator
        assert "| --- | --- |" in result or "|---|---|" in result
        # Should have data rows
        assert "| Apple | $1.00 |" in result
        assert "| Orange | $1.50 |" in result

    def test_table_without_thead(self):
        """Test table with only td cells (no th)."""
        html = """
        <table>
            <tr><td>Row1Col1</td><td>Row1Col2</td></tr>
            <tr><td>Row2Col1</td><td>Row2Col2</td></tr>
        </table>
        """
        result = convert_html_to_markdown(html)
        # First row should be treated as data
        assert "| Row1Col1 | Row1Col2 |" in result
        assert "| Row2Col1 | Row2Col2 |" in result

    def test_table_with_colspan(self):
        """Test table with colspan attribute."""
        html = """
        <table>
            <tr><td colspan="3">Title Spanning 3 Columns</td></tr>
            <tr><th>Col1</th><th>Col2</th><th>Col3</th></tr>
            <tr><td>A</td><td>B</td><td>C</td></tr>
        </table>
        """
        result = convert_html_to_markdown(html)
        # Should handle colspan by expanding to multiple columns
        # Title should appear across columns
        assert "Title Spanning 3 Columns" in result
        # Headers should be present
        assert "Col1" in result and "Col2" in result and "Col3" in result
        # Data row should be present
        assert "A" in result and "B" in result and "C" in result

    def test_table_empty_cells(self):
        """Test table with empty cells."""
        html = """
        <table>
            <tr><th>Name</th><th>Value</th></tr>
            <tr><td>Item1</td><td></td></tr>
            <tr><td></td><td>Value2</td></tr>
        </table>
        """
        result = convert_html_to_markdown(html)
        # Should handle empty cells gracefully
        assert "| Name | Value |" in result
        assert "| Item1 |" in result
        assert "| Value2 |" in result

    def test_table_nested_formatting(self):
        """Test table cells with nested formatting (bold, links)."""
        html = """
        <table>
            <tr><th>Product</th><th>Details</th></tr>
            <tr><td><strong>Bold Item</strong></td><td><a href="http://example.com">Link</a></td></tr>
        </table>
        """
        result = convert_html_to_markdown(html)
        # Should preserve inline formatting in cells
        assert "**Bold Item**" in result
        assert "[Link](http://example.com)" in result

    def test_custom_config(self):
        """Test conversion with custom configuration."""
        config = ConversionConfig(bullet_marker="*")
        html = "<ul><li>Item</li></ul>"
        result = convert_html_to_markdown(html, config=config)
        assert "* Item" in result


class TestConversionConfig:
    """Tests for ConversionConfig dataclass."""

    def test_default_values(self):
        """Test default configuration values."""
        config = ConversionConfig()
        assert config.preserve_structure is True
        assert config.preserve_tables is True
        assert config.heading_style == "atx"
        assert config.bullet_marker == "-"

    def test_custom_values(self):
        """Test custom configuration values."""
        config = ConversionConfig(
            preserve_structure=False, heading_style="setext", bullet_marker="*"
        )
        assert config.preserve_structure is False
        assert config.heading_style == "setext"
        assert config.bullet_marker == "*"
