# LuminNexus AlchemyMind Shared

Shared utilities for LuminNexus AlchemyMind projects.

## Overview

This package provides common utilities used across the AlchemyMind project family:
- **鍊金之心** (Alchemy Mind): Frontend and data management
- **TheRefinery**: Data cleaning, deduplication, and matching
- **TheWeaver**: LLM-based validation

## Installation

### For development (editable mode)

```bash
# From TheWeaver project
cd /path/to/TheWeaver
pip install -e ../LuminNexus-AlchemyMind-Shared
```

or with uv:

```bash
uv pip install -e ../LuminNexus-AlchemyMind-Shared
```

### As a regular package

```bash
pip install luminnexus-alchemy-shared
```

## Features

### HTML Processing

Convert HTML content to Markdown or Rich tables:

```python
from luminnexus_alchemy_shared import convert_html_to_markdown, convert_html_to_table

# HTML to Markdown
html = "<p>Hello <strong>World</strong></p>"
markdown = convert_html_to_markdown(html)
print(markdown)  # Hello **World**

# HTML table to Rich table (for terminal display)
html_table = "<table>...</table>"
rich_table = convert_html_to_table(html_table)
print(rich_table)
```

### Type Converters

Safe type conversion utilities:

```python
from luminnexus_alchemy_shared import safe_decimal, safe_int, safe_str

# Safe decimal conversion
value = safe_decimal("123.45")  # Returns Decimal("123.45")
value = safe_decimal("<1")      # Returns Decimal("0.9999")
value = safe_decimal("invalid") # Returns None

# Safe integer conversion
count = safe_int("42")          # Returns 42
count = safe_int("3.14")        # Returns 3
count = safe_int("invalid")     # Returns None

# Safe string conversion
text = safe_str("  hello  ")    # Returns "hello"
text = safe_str("")             # Returns None
text = safe_str(123)            # Returns None
```

## Modules

### `luminnexus_alchemy_shared.html`

- `HTMLToMarkdownConverter`: Configurable HTML to Markdown converter
- `ConversionConfig`: Configuration options for HTML conversion
- `convert_html_to_markdown()`: Convenience function for HTML → Markdown
- `convert_html_to_table()`: Convert HTML tables to Rich tables

### `luminnexus_alchemy_shared.converters`

- `safe_decimal()`: Safe conversion to Decimal (for DecimalField)
- `safe_int()`: Safe conversion to integer
- `safe_str()`: Safe conversion to trimmed string

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/mapleelpam/LuminNexus-AlchemyMind-Shared.git
cd LuminNexus-AlchemyMind-Shared

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Quality

This project uses `ruff` for linting:

```bash
ruff check src/
ruff format src/
```

## License

MIT License

## Changelog

### 0.1.0 (2025-11-17)

- Initial release
- HTML to Markdown converter
- HTML table to Rich table converter
- Type conversion utilities
