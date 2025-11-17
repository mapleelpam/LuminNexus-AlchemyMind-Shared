# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-17

### Added

- Initial release of luminnexus-alchemy-shared
- HTML to Markdown converter with configurable options
  - Support for headings, lists, tables, code blocks, blockquotes
  - Configurable heading style (atx vs setext)
  - Configurable bullet markers and emphasis markers
- HTML table to Rich table converter for terminal display
- Type conversion utilities:
  - `safe_decimal()`: Safe conversion to Decimal with precision handling
  - `safe_int()`: Safe conversion to integer
  - `safe_str()`: Safe conversion to trimmed string
- Comprehensive test suite
- Full documentation in README.md

[0.1.0]: https://github.com/yourusername/LuminNexus-AlchemyMind-Shared/releases/tag/v0.1.0
