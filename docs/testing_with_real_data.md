# Testing with Real-World Data and LLM Validation

**Date**: 2025-11-17
**Purpose**: Document the testing strategy for HTML conversion using real iHerb product data

## Overview

Traditional unit tests with exact string matching are insufficient for validating HTML conversion quality because:

1. **Multiple Valid Outputs**: There are many valid ways to represent the same content in Markdown
2. **Formatting Flexibility**: Spacing, line breaks, and style choices can vary
3. **Semantic Equivalence**: What matters is meaning preservation, not exact format

Therefore, we use a **dual approach**:
- **Basic assertions** for structural integrity (content present, no crashes)
- **LLM-based validation** for quality assessment (readability, correctness, completeness)

## Test Data Source

**Location**: `/Users/maple/github/LuminNexus-AtlasVault-Vault/data/iherb/catalog/20250905/`

**Products Selected** (randomly chosen):
1. **Product 100627**: Zesty Paws Senior Advanced Allergy & Immune Bites
   - Complex nested HTML with lists
   - Tables in `suggestedUse`
   - Rich `supplementFacts` table with colspan

2. **Product 150817**: Sun Bum Mineral Sunscreen Face Stick
   - Simple bullet lists
   - Drug Facts table in `ingredients`
   - Multiple paragraphs

## Test Files Structure

```
tests/
├── fixtures/
│   └── iherb_sample_data.py          # Real HTML data from iHerb
├── test_real_world_conversions.py     # Integration tests
└── llm_validation_agent.py            # LLM validation framework
```

## Running Tests

### 1. Basic Structural Tests

Run the standard pytest tests:

```bash
# Run all real-world data tests
pytest tests/test_real_world_conversions.py -v

# Run specific test class
pytest tests/test_real_world_conversions.py::TestRealWorldHTMLToMarkdown -v

# Run with output captured for review
pytest tests/test_real_world_conversions.py -v -s
```

These tests verify:
- ✅ No crashes or exceptions
- ✅ Key content is preserved
- ✅ Basic formatting markers present
- ✅ Tables have structure indicators

### 2. LLM-Based Quality Validation

After running basic tests, use LLM validation for quality assessment.

#### Option A: Using Claude Code Task Tool (Recommended)

```bash
# Run tests and capture outputs
pytest tests/test_real_world_conversions.py -v > test_outputs.txt

# Then use Claude Code to analyze
# The test file stores validation criteria that can be reviewed
```

#### Option B: Manual Review with Structured Prompts

```python
# In Python/IPython console
from tests.fixtures.iherb_sample_data import PRODUCT_100627_DESCRIPTION
from luminnexus_alchemy_shared.html import convert_html_to_markdown

# Convert
result = convert_html_to_markdown(PRODUCT_100627_DESCRIPTION)

# Print for review
print("=== ORIGINAL HTML ===")
print(PRODUCT_100627_DESCRIPTION)
print("\n=== CONVERTED MARKDOWN ===")
print(result)
```

Then ask Claude to evaluate using the validation criteria.

#### Option C: Automated LLM Validation (Future)

```python
from tests.llm_validation_agent import LLMConversionValidator

validator = LLMConversionValidator()

# Run validation
result = validator.validate_markdown_conversion(
    test_name="product_100627_description",
    input_html=PRODUCT_100627_DESCRIPTION,
    output_markdown=converted_result,
    validation_criteria=[
        "Should convert bullet list items correctly",
        "Should preserve bold text",
        # ... more criteria
    ]
)

print(f"Score: {result.score}")
print(f"Feedback: {result.feedback}")
```

## Validation Criteria

### For HTML to Markdown Conversion

The LLM evaluates based on:

1. **Information Preservation** (30%)
   - All text content present
   - Formatting hints preserved (bold → `**text**`, italic → `*text*`)
   - Links preserved with correct syntax
   - No data loss

2. **Readability** (30%)
   - Proper spacing between elements
   - Clear visual hierarchy
   - Easy to scan and read
   - Logical flow

3. **Markdown Standards** (25%)
   - Valid Markdown syntax
   - Consistent style choices
   - Proper list markers (-, *, or numbered)
   - Correct heading levels
   - Valid table syntax

4. **Edge Case Handling** (15%)
   - HTML entities decoded (`&amp;` → `&`)
   - Special characters preserved (`®`, `™`)
   - Nested structures handled correctly
   - Empty/whitespace-only elements handled

### For HTML Table to ASCII Table Conversion

The LLM evaluates based on:

1. **Data Integrity** (35%)
   - All cell contents present and correct
   - Numbers and units preserved exactly
   - No missing or corrupted data

2. **Structure** (25%)
   - Clear table structure with borders
   - Headers visually distinct
   - Rows and columns aligned
   - Cell boundaries clear

3. **Readability** (25%)
   - Proper column alignment
   - Reasonable width (not too wide or narrow)
   - Text wrapping handled well
   - Visual hierarchy clear

4. **Edge Case Handling** (15%)
   - Colspan/rowspan handled appropriately
   - Nested HTML extracted correctly
   - Long text cells handled
   - Empty cells displayed correctly

## Scoring Interpretation

- **0.90-1.00**: Excellent - Production ready
- **0.80-0.89**: Good - Minor improvements recommended
- **0.70-0.79**: Acceptable - Some issues to address
- **0.60-0.69**: Poor - Significant improvements needed
- **<0.60**: Failing - Major issues, refactoring required

## Example Validation Session

### Step 1: Run Test and Capture Output

```bash
pytest tests/test_real_world_conversions.py::TestRealWorldHTMLToMarkdown::test_product_100627_description_conversion -v -s
```

### Step 2: Review Output Manually

```python
from tests.fixtures.iherb_sample_data import PRODUCT_100627_DESCRIPTION
from luminnexus_alchemy_shared.html import convert_html_to_markdown

html = PRODUCT_100627_DESCRIPTION
md = convert_html_to_markdown(html)

print(md)
```

### Step 3: Ask Claude for Evaluation

Provide Claude with:
```
Please evaluate this HTML to Markdown conversion:

**Original HTML:**
<ul><li>Immune System</li><li>No Artificial Flavors...</li>...</ul>

**Converted Markdown:**
- Immune System
- No Artificial Flavors...
...

**Criteria:**
- Should convert bullet list items correctly
- Should preserve bold text (**text**)
- Should handle HTML entities (&amp; -> &)

Rate on 0.0-1.0 scale and provide:
- Overall score
- What works well
- What needs improvement
```

### Step 4: Iterate Based on Feedback

Based on LLM feedback, make improvements and re-test.

## Adding New Test Cases

To add more real-world test cases:

1. **Select Random Products**:
   ```bash
   find /Users/maple/github/LuminNexus-AtlasVault-Vault/data/iherb/catalog/20250905 -name "*.json" | shuf -n 2
   ```

2. **Extract Relevant Fields**:
   ```python
   import json

   with open('path/to/product.json') as f:
       data = json.load(f)

   description = data['description']
   supplement_facts = data['supplementFacts']
   # etc.
   ```

3. **Add to Fixtures**:
   - Add constants to `tests/fixtures/iherb_sample_data.py`
   - Add test case metadata to `TEST_CASES` list

4. **Create Test Methods**:
   - Add test methods to `test_real_world_conversions.py`
   - Include validation criteria

## Current Test Coverage

### HTML to Markdown
- ✅ Simple bullet lists
- ✅ Nested formatting (bold, italic in paragraphs)
- ✅ Mixed content (text + lists + paragraphs)
- ✅ HTML entities (`&amp;`, `&nbsp;`)
- ✅ Special characters (®, ™)
- ✅ Tables embedded in content
- ⚠️ Need to add: Nested lists, complex tables

### HTML Table to ASCII
- ✅ Simple data tables
- ✅ Tables with headers (th)
- ✅ Tables with colspan
- ✅ Nested HTML in cells (bold, sup)
- ✅ Long text cells (wrapping)
- ⚠️ Need to add: Rowspan, very wide tables, deeply nested content

## Integration with Refactoring Plan

This testing approach integrates with the refactoring plan (`docs/20251117_refactoring_plan.md`):

- **Phase 1**: Run these tests to establish baseline
- **After each fix**: Re-run tests and validate improvements
- **Before release**: Ensure all tests pass with scores >0.85

## Future Enhancements

1. **Automated LLM Integration**: Implement actual API calls in `llm_validation_agent.py`
2. **Test Report Generation**: Auto-generate validation reports after test runs
3. **Regression Suite**: Save "golden" outputs and track changes over time
4. **Performance Benchmarks**: Add timing tests for large documents
5. **More Test Data**: Expand to 10-20 representative products

## References

- Test fixtures: `tests/fixtures/iherb_sample_data.py`
- Integration tests: `tests/test_real_world_conversions.py`
- LLM validator: `tests/llm_validation_agent.py`
- Refactoring plan: `docs/20251117_refactoring_plan.md`
