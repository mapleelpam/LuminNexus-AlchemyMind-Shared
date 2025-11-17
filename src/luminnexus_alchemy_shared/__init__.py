"""
LuminNexus AlchemyMind Shared Utilities

Shared utilities for LuminNexus AlchemyMind projects:
- 鍊金之心 (Alchemy Mind): Frontend and data management
- TheRefinery: Data cleaning, deduplication, and matching
- TheWeaver: LLM-based validation
"""

__version__ = "0.1.0"

# Top-level imports for convenience
from luminnexus_alchemy_shared.converters import safe_decimal, safe_int, safe_str
from luminnexus_alchemy_shared.html import (
    ConversionConfig,
    HTMLToMarkdownConverter,
    convert_html_to_markdown,
    convert_html_to_table,
)

__all__ = [
    # Version
    "__version__",
    # HTML utilities
    "ConversionConfig",
    "HTMLToMarkdownConverter",
    "convert_html_to_markdown",
    "convert_html_to_table",
    # Type converters
    "safe_decimal",
    "safe_int",
    "safe_str",
]
