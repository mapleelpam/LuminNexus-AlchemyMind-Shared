# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**luminnexus-alchemy-shared** is a Python utility library providing shared functionality for the AlchemyMind project family:
- **鍊金之心** (Alchemy Mind): Frontend and data management
- **TheRefinery**: Data cleaning, deduplication, and matching
- **TheWeaver**: LLM-based validation

The package is designed to be installed in editable mode (`pip install -e`) across multiple sibling projects.

## Development Commands

### Setup
```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Or with uv
uv pip install -e ".[dev]"
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_type_converters.py
pytest tests/test_markdown_converter.py

# Run with coverage
pytest --cov=luminnexus_alchemy_shared
```

### Code Quality
```bash
# Check code with ruff
ruff check src/

# Format code with ruff
ruff format src/

# Check and format together
ruff check src/ && ruff format src/
```

### Building
```bash
# Build distribution packages
python -m build
```

## Architecture

### Package Structure

The library is organized into two main functional areas:

1. **HTML Processing** (`luminnexus_alchemy_shared.html`)
   - `markdown_converter.py`: Converts HTML to Markdown with configurable options
   - `table_renderer.py`: Converts HTML tables to Rich table objects for terminal display
   - **Key class**: `HTMLToMarkdownConverter` with `ConversionConfig` for customization

2. **Type Converters** (`luminnexus_alchemy_shared.converters`)
   - `type_converters.py`: Safe type conversion utilities
   - **Key functions**: `safe_decimal()`, `safe_int()`, `safe_str()`
   - Designed for Django model field conversion (especially DecimalField)

### Design Patterns

**HTML Converter Architecture**: The `HTMLToMarkdownConverter` uses BeautifulSoup for parsing and applies transformations in phases:
1. Structure processing (headings, lists, tables, code blocks)
2. Basic formatting (bold, italic, links)
3. Cleaning and normalization

The converter accepts both string HTML and BeautifulSoup/Tag objects, allowing for flexible integration.

**Type Converter Philosophy**: All converters follow a "safe" pattern returning `Optional[T]` rather than raising exceptions. This is intentional for data pipeline robustness where invalid data should be logged but not crash the process. Key behaviors:
- `safe_decimal()`: Handles edge cases like `"<1"` (converts to 0.9999), enforces max_digits=15 and decimal_places=5
- `safe_int()`: Accepts string decimals like `"3.14"` (converts to 3)
- `safe_str()`: Only returns trimmed non-empty strings, returns None for non-string types

## Key Configuration

### Project Metadata
- **Python version**: >=3.10
- **Main dependencies**: beautifulsoup4, rich
- **Dev dependencies**: pytest, pytest-cov, ruff
- **Package location**: Source in `src/`, tests in `tests/`

### Ruff Configuration
- Line length: 100 characters
- Target: Python 3.10
- Enabled rules: E (errors), F (pyflakes), I (isort), N (naming), W (warnings)

### Pytest Configuration
- Test discovery: `tests/test_*.py`
- Default options: `-v --tb=short`

## Important Notes

- This is a shared library used by multiple projects, so maintain backward compatibility
- The codebase contains Chinese comments (Traditional Chinese) - preserve them when editing
- Type converters are designed for data cleaning pipelines where graceful degradation is preferred over exceptions
- When working with HTML conversion, the `ConversionConfig` allows customization of markdown style (ATX vs Setext headings, emphasis markers, etc.)
- All public APIs are exposed through `__init__.py` for convenient top-level imports
