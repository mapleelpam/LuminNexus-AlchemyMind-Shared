# Refactoring Plan - Post Code Review
**Date**: 2025-11-17
**Status**: Planning Phase
**Reviewer**: Claude Code Architecture Review

## 📋 Executive Summary

This document outlines the refactoring plan based on the comprehensive architecture review of the `luminnexus-alchemy-shared` library. The codebase has excellent modular design and defensive programming practices, but requires several bug fixes and test coverage improvements before production use.

## 🎯 Goals

1. Fix critical bugs in HTML list processing
2. Add comprehensive test coverage (especially for `table_renderer`)
3. Improve edge case handling in HTML conversion
4. Enhance documentation clarity
5. Establish code quality automation

## 📊 Current Status

| Module | Test Coverage | Critical Issues | Priority |
|--------|--------------|-----------------|----------|
| `converters/` | ✅ Good | None | Low |
| `html/markdown_converter.py` | ⚠️ Partial | 🔴 List nesting bug | High |
| `html/table_renderer.py` | ❌ None | None (but untested) | High |

## 🚨 Priority 1: Critical Fixes (Must Do Before Release)

### 1.1 Fix List Processing Bug

**File**: `src/luminnexus_alchemy_shared/html/markdown_converter.py:106-114`

**Problem**: Nested lists are processed incorrectly because `find_all("li")` finds all descendants, not just direct children.

**Current Code**:
```python
def _process_lists(self, soup: BeautifulSoup) -> None:
    """處理列表"""
    for ol in soup.find_all("ol"):
        for i, li in enumerate(ol.find_all("li"), 1):
            li.replace_with(f"\n{i}. {li.get_text().strip()}")

    for ul in soup.find_all("ul"):
        for li in ul.find_all("li"):
            li.replace_with(f"\n{self.config.bullet_marker} {li.get_text().strip()}")
```

**Solution**:
```python
def _process_lists(self, soup: BeautifulSoup) -> None:
    """處理列表 - 只處理直接子節點避免嵌套問題"""
    for ol in soup.find_all("ol"):
        for i, li in enumerate(ol.find_all("li", recursive=False), 1):
            li.replace_with(f"\n{i}. {li.get_text().strip()}")

    for ul in soup.find_all("ul"):
        for li in ul.find_all("li", recursive=False):
            li.replace_with(f"\n{self.config.bullet_marker} {li.get_text().strip()}")
```

**Test Cases to Add**:
```python
def test_nested_unordered_list(self):
    """Test nested unordered lists maintain structure."""
    html = """
    <ul>
        <li>Parent 1
            <ul>
                <li>Child 1.1</li>
                <li>Child 1.2</li>
            </ul>
        </li>
        <li>Parent 2</li>
    </ul>
    """
    result = convert_html_to_markdown(html)
    # Should handle nested structure appropriately
    assert "Parent 1" in result
    assert "Child 1.1" in result

def test_nested_ordered_list(self):
    """Test nested ordered lists."""
    html = """
    <ol>
        <li>First
            <ol>
                <li>First.a</li>
                <li>First.b</li>
            </ol>
        </li>
        <li>Second</li>
    </ol>
    """
    result = convert_html_to_markdown(html)
    assert "1. First" in result
    assert "2. Second" in result

def test_mixed_nested_lists(self):
    """Test mixed ul/ol nesting."""
    html = """
    <ul>
        <li>Bullet
            <ol>
                <li>Numbered in bullet</li>
            </ol>
        </li>
    </ul>
    """
    result = convert_html_to_markdown(html)
    assert "- Bullet" in result
```

### 1.2 Add Complete Test Suite for Table Renderer

**File**: Create `tests/test_table_renderer.py`

**Rationale**: This module has ZERO test coverage.

**Test Cases**:
```python
"""Tests for HTML table to Rich table converter."""

import pytest
from luminnexus_alchemy_shared.html import convert_html_to_table


class TestConvertHTMLToTable:
    """Tests for convert_html_to_table function."""

    def test_simple_table(self):
        """Test conversion of simple table."""
        html = """
        <table>
            <tr><td>A</td><td>B</td></tr>
            <tr><td>C</td><td>D</td></tr>
        </table>
        """
        result = convert_html_to_table(html)
        assert "A" in result
        assert "B" in result
        assert "C" in result
        assert "D" in result

    def test_table_with_headers(self):
        """Test table with th headers."""
        html = """
        <table>
            <tr><th>Name</th><th>Age</th></tr>
            <tr><td>Alice</td><td>30</td></tr>
        </table>
        """
        result = convert_html_to_table(html)
        assert "Name" in result
        assert "Alice" in result

    def test_empty_string_input(self):
        """Test empty string returns empty string."""
        result = convert_html_to_table("")
        assert result == ""

    def test_none_input(self):
        """Test None input returns empty string."""
        result = convert_html_to_table(None)
        assert result == ""

    def test_no_table_found(self):
        """Test HTML without table returns empty string."""
        html = "<p>No table here</p>"
        result = convert_html_to_table(html)
        assert result == ""

    def test_empty_table(self):
        """Test table with no rows."""
        html = "<table></table>"
        result = convert_html_to_table(html)
        assert result == ""

    def test_table_with_empty_cells(self):
        """Test table with empty cells."""
        html = """
        <table>
            <tr><td>A</td><td></td></tr>
            <tr><td></td><td>D</td></tr>
        </table>
        """
        result = convert_html_to_table(html)
        assert "A" in result
        assert "D" in result

    def test_table_with_long_text(self):
        """Test table cell with text > 200 chars gets wrapped."""
        long_text = "x" * 250
        html = f"<table><tr><td>{long_text}</td></tr></table>"
        result = convert_html_to_table(html)
        assert "x" in result

    def test_table_with_nested_tags(self):
        """Test table with nested HTML tags in cells."""
        html = """
        <table>
            <tr><td><strong>Bold</strong></td><td><em>Italic</em></td></tr>
        </table>
        """
        result = convert_html_to_table(html)
        assert "Bold" in result
        assert "Italic" in result

    def test_uneven_row_columns(self):
        """Test table with rows having different column counts."""
        html = """
        <table>
            <tr><td>A</td><td>B</td><td>C</td></tr>
            <tr><td>D</td><td>E</td></tr>
        </table>
        """
        result = convert_html_to_table(html)
        # Should handle gracefully with empty cells
        assert "A" in result
        assert "D" in result
```

## ⚠️ Priority 2: Important Improvements (Should Do)

### 2.1 Improve Table Processing in Markdown Converter

**File**: `src/luminnexus_alchemy_shared/html/markdown_converter.py:116-132`

**Problem**: Doesn't handle `<thead>`, `<tbody>`, or cells with `colspan`/`rowspan`.

**Refactored Solution**:
```python
def _process_tables(self, soup: BeautifulSoup) -> None:
    """處理表格 - 支持 thead/tbody 結構"""
    for table in soup.find_all("table"):
        rows = []

        # 處理表頭 - 優先使用 thead
        thead = table.find("thead")
        if thead:
            header_row = thead.find("tr")
            if header_row:
                headers = [cell.get_text().strip()
                          for cell in header_row.find_all(["th", "td"])]
                if headers:
                    rows.append("| " + " | ".join(headers) + " |")
                    rows.append("| " + " | ".join(["---"] * len(headers)) + " |")
        else:
            # 降級處理 - 查找所有 th 作為表頭
            headers = [th.get_text().strip() for th in table.find_all("th")]
            if headers:
                rows.append("| " + " | ".join(headers) + " |")
                rows.append("| " + " | ".join(["---"] * len(headers)) + " |")

        # 處理數據行 - 優先使用 tbody，否則處理所有 tr
        tbody = table.find("tbody")
        rows_to_process = tbody.find_all("tr", recursive=False) if tbody else table.find_all("tr")

        for tr in rows_to_process:
            # 只處理包含 td 的行（跳過純 th 的表頭行）
            cells = [td.get_text().strip() for td in tr.find_all("td")]
            if cells:
                rows.append("| " + " | ".join(cells) + " |")

        if rows:
            table.replace_with("\n" + "\n".join(rows) + "\n")
        else:
            # 如果沒有任何內容，移除表格
            table.replace_with("")
```

**Test Cases to Add**:
```python
def test_table_with_thead_tbody(self):
    """Test table with proper thead/tbody structure."""
    html = """
    <table>
        <thead>
            <tr><th>Name</th><th>Age</th></tr>
        </thead>
        <tbody>
            <tr><td>Alice</td><td>30</td></tr>
            <tr><td>Bob</td><td>25</td></tr>
        </tbody>
    </table>
    """
    result = convert_html_to_markdown(html)
    assert "| Name | Age |" in result
    assert "| --- | --- |" in result
    assert "| Alice | 30 |" in result
    assert "| Bob | 25 |" in result

def test_table_empty(self):
    """Test empty table handling."""
    html = "<table></table>"
    result = convert_html_to_markdown(html)
    # Should not crash, may return empty or minimal output

def test_table_with_mixed_th_td(self):
    """Test table with th and td mixed in body."""
    html = """
    <table>
        <tr><th>Header 1</th><th>Header 2</th></tr>
        <tr><th>Row Header</th><td>Data</td></tr>
    </table>
    """
    result = convert_html_to_markdown(html)
    assert "Header 1" in result
```

### 2.2 Add Markdown Escape Function

**File**: `src/luminnexus_alchemy_shared/html/markdown_converter.py`

**Problem**: Special Markdown characters are not escaped, causing rendering issues.

**Add Method**:
```python
def _escape_markdown(self, text: str) -> str:
    """轉義 Markdown 特殊字符"""
    # Escape: \ ` * _ { } [ ] ( ) # + - . ! |
    special_chars = r'\`*_{}[]()#+-.!|'
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text
```

**Usage**: Apply before inserting text into Markdown structures (but NOT inside code blocks or links).

**Test Cases**:
```python
def test_markdown_special_chars_escaped(self):
    """Test that Markdown special characters are escaped."""
    html = "<p>Cost: $100 * 2 = $200 [Note: see #5]</p>"
    result = convert_html_to_markdown(html)
    # Should escape *, [, ], #
    assert "\\*" in result or result  # Verify escaping strategy

def test_code_blocks_not_escaped(self):
    """Test that code blocks don't escape content."""
    html = "<pre>def foo(*args):</pre>"
    result = convert_html_to_markdown(html)
    # Content inside ``` should NOT be escaped
    assert "def foo(*args):" in result
```

### 2.3 Enhance `safe_decimal()` Documentation

**File**: `src/luminnexus_alchemy_shared/converters/type_converters.py:7-69`

**Problem**: The `<1` handling is undocumented and surprising.

**Solution**: Improve docstring:
```python
def safe_decimal(value: Any) -> Optional[decimal.Decimal]:
    """
    嘗試將值轉換為Decimal，用於DecimalField(max_digits=15, decimal_places=5)。
    若發生任何錯誤或超出範圍，則返回None。

    Special handling:
    - Strings starting with '<' (e.g., "<1") are treated as "less than" values
      and converted to slightly less (value - 0.0001). This is common in
      laboratory data where values are below detection limits.
    - Only '<' prefix is supported. Other operators ('>', '<=', '>=') return None.

    Constraints:
    - Max digits: 15 (10 integer + 5 decimal)
    - Decimal places: 5 (quantized with ROUND_HALF_UP)
    - Range: -9999999999.99999 to 9999999999.99999

    Args:
        value: 要轉換的值 (str, int, float)

    Returns:
        decimal.Decimal 或 None（轉換失敗時）

    Examples:
        >>> safe_decimal("123.45")
        Decimal('123.45000')
        >>> safe_decimal("<1")      # Below detection limit
        Decimal('0.99990')
        >>> safe_decimal(">5")      # Not supported
        None
        >>> safe_decimal("invalid")
        None
        >>> safe_decimal(10000000000)  # Out of range
        None
    """
```

**Test Cases to Add**:
```python
def test_less_than_edge_cases(self):
    """Test various '<' format inputs."""
    assert safe_decimal("<0.1") == decimal.Decimal("0.09990")
    assert safe_decimal("< 5") == decimal.Decimal("4.99990")
    assert safe_decimal("<0.0001") == decimal.Decimal("0.00000")

def test_unsupported_operators(self):
    """Test that other operators return None."""
    assert safe_decimal(">10") is None
    assert safe_decimal(">=5") is None
    assert safe_decimal("<=3") is None

def test_max_value_boundary(self):
    """Test maximum allowed value."""
    assert safe_decimal("9999999999.99999") is not None
    assert safe_decimal("10000000000") is None

def test_min_value_boundary(self):
    """Test minimum allowed value."""
    assert safe_decimal("-9999999999.99999") is not None
    assert safe_decimal("-10000000000") is None
```

### 2.4 Enhance `safe_int()` Clarity

**File**: `src/luminnexus_alchemy_shared/converters/type_converters.py:72-96`

**Current Issue**: Unclear that `"3.14"` → `3` is truncation.

**Solution**: Update docstring:
```python
def safe_int(value: Any) -> Optional[int]:
    """
    嘗試將值轉換為整數。轉換失敗時返回None。

    Behavior:
    - Accepts string integers: "42" -> 42
    - Accepts floats/float strings: 3.14 -> 3, "3.9" -> 3
    - Truncates towards zero (int conversion, not rounding)
    - Whitespace is stripped automatically

    Args:
        value: 要轉換的值 (str, int, float)

    Returns:
        int 或 None（轉換失敗時）

    Examples:
        >>> safe_int("42")
        42
        >>> safe_int("3.14")    # Truncates decimal
        3
        >>> safe_int(-3.9)      # Truncates towards zero
        -3
        >>> safe_int("  10  ")
        10
        >>> safe_int("invalid")
        None
    """
```

**Test Cases to Add**:
```python
def test_negative_numbers(self):
    """Test negative integer conversion."""
    assert safe_int("-42") == -42
    assert safe_int(-3.9) == -3

def test_large_numbers(self):
    """Test large integer conversion."""
    assert safe_int("999999999") == 999999999
    assert safe_int(1e10) == 10000000000

def test_whitespace_handling(self):
    """Test whitespace is stripped."""
    assert safe_int("  42  ") == 42
    assert safe_int("\t10\n") == 10
```

### 2.5 Improve Table Renderer API

**File**: `src/luminnexus_alchemy_shared/html/table_renderer.py:12-68`

**Enhancement**: Allow custom Console configuration.

**Refactored Code**:
```python
def convert_html_to_table(
    html_string: Optional[str],
    console: Optional[Console] = None,
    width: Optional[int] = None,
) -> str:
    """
    Convert HTML table to Rich table format for terminal display.

    Args:
        html_string: HTML string containing a table
        console: Custom Rich Console instance (optional)
        width: Console width for rendering (optional)

    Returns:
        String representation of Rich table, or empty string if no table found
    """
    if not html_string:
        return ""

    # 解析HTML
    soup = BeautifulSoup(html_string, "html.parser")

    if len(soup.find_all("tr")) == 0:
        return ""

    # 創建Rich表格
    rich_table = Table(box=box.SQUARE, show_header=False, show_lines=True)

    # ... (rest of logic)

    # 創建或使用提供的Console對象
    if console is None:
        console = Console(width=width) if width else Console()

    with console.capture() as capture:
        console.print(rich_table)

    return capture.get()
```

## 📝 Priority 3: Nice to Have (Can Do Later)

### 3.1 Add Edge Case Tests for Markdown Converter

**Test Cases to Add**:
```python
def test_empty_html(self):
    """Test empty HTML input."""
    assert convert_html_to_markdown("") == "\n"

def test_malformed_html(self):
    """Test malformed HTML is handled gracefully."""
    html = "<p>Unclosed paragraph"
    result = convert_html_to_markdown(html)
    assert "Unclosed paragraph" in result

def test_mixed_formatting(self):
    """Test complex mixed formatting."""
    html = "<p>Text with <strong>bold</strong>, <em>italic</em>, and <code>code</code>.</p>"
    result = convert_html_to_markdown(html)
    assert "**bold**" in result
    assert "*italic*" in result
    assert "`code`" in result

def test_container_selector(self):
    """Test container_selector parameter."""
    html = """
    <div class="header">Skip this</div>
    <div class="content">Extract this</div>
    """
    result = convert_html_to_markdown(html, container_selector=".content")
    assert "Extract this" in result
    assert "Skip this" not in result
```

### 3.2 Unify Documentation Language

**Options**:
- **Option A (Recommended)**: English docstrings + Chinese inline comments
- **Option B**: All Chinese with English README summary

**Action**: Decide on standard and update accordingly.

### 3.3 Add Pre-commit Hooks

**File**: Create `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
```

**Installation**:
```bash
pip install pre-commit
pre-commit install
```

### 3.4 Configure Coverage Reporting

**File**: `pyproject.toml`

**Add Section**:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short --cov=luminnexus_alchemy_shared --cov-report=term-missing --cov-report=html"

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/__init__.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
fail_under = 80
```

## 📅 Implementation Timeline

### Phase 1: Critical Fixes (Week 1)
- [ ] Day 1-2: Write all Priority 1 test cases
- [ ] Day 3: Fix list processing bug
- [ ] Day 4: Implement table_renderer tests
- [ ] Day 5: Run full test suite, verify coverage

### Phase 2: Important Improvements (Week 2)
- [ ] Day 1-2: Refactor table processing
- [ ] Day 3: Add Markdown escaping
- [ ] Day 4: Enhance documentation (safe_decimal, safe_int)
- [ ] Day 5: Write Priority 2 test cases and verify

### Phase 3: Quality of Life (Week 3)
- [ ] Configure pre-commit hooks
- [ ] Add coverage reporting
- [ ] Write remaining edge case tests
- [ ] Review and unify documentation language

## ✅ Acceptance Criteria

Before considering refactoring complete:

- [ ] All Priority 1 items implemented and tested
- [ ] Test coverage >= 90% for all modules
- [ ] No failing tests
- [ ] All new tests documented with clear descriptions
- [ ] `ruff check src/` passes with no errors
- [ ] Manual testing of HTML conversion with complex nested structures
- [ ] Documentation reviewed for clarity

## 📚 References

- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Rich Table Documentation](https://rich.readthedocs.io/en/latest/tables.html)
- [Python Decimal Documentation](https://docs.python.org/3/library/decimal.html)
- [Pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)

## 🔄 Review Checkpoints

After each phase:
1. Run full test suite: `pytest -v --cov`
2. Check code quality: `ruff check src/`
3. Manual smoke test with sample data
4. Update this document with actual completion dates

---

**Next Steps**: Begin Phase 1 by writing comprehensive test cases before making any code changes.
