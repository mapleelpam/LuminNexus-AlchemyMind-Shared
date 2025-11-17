# Validate HTML Conversion Quality

You are an expert technical documentation evaluator. Your task is to validate the quality of HTML to Markdown and HTML to Table conversions using real-world iHerb product data.

## Your Mission

1. **Run the integration tests** to generate conversion outputs
2. **Evaluate each conversion** using LLM-based quality assessment
3. **Generate a comprehensive report** with scores and recommendations

## Step 1: Run Tests and Collect Outputs

First, run the real-world conversion tests:

```bash
pytest tests/test_real_world_conversions.py -v -s
```

## Step 2: Evaluate Conversions

For each test case, you will evaluate the conversion by comparing:
- **Input**: Original HTML from iHerb products
- **Output**: Converted Markdown or ASCII table
- **Criteria**: Specific validation requirements

You will score each conversion on a 0.0 to 1.0 scale based on:

### For HTML → Markdown Conversions

1. **Information Preservation (30%)**
   - Is all text content from HTML present in Markdown?
   - Are formatting hints preserved (bold → `**text**`, italic → `*text*`)?
   - Are links preserved with correct syntax?
   - Is there any data loss?

2. **Readability (30%)**
   - Is there proper spacing between elements?
   - Is the visual hierarchy clear?
   - Is it easy to scan and read?
   - Does it have logical flow?

3. **Markdown Standards (25%)**
   - Is the Markdown syntax valid?
   - Are style choices consistent?
   - Are list markers correct (-, *, or numbered)?
   - Are heading levels appropriate?
   - Is table syntax valid (if applicable)?

4. **Edge Case Handling (15%)**
   - Are HTML entities decoded (`&amp;` → `&`)?
   - Are special characters preserved (`®`, `™`)?
   - Are nested structures handled correctly?
   - Are empty/whitespace-only elements handled gracefully?

### For HTML Table → ASCII Table Conversions

1. **Data Integrity (35%)**
   - Are all cell contents present and correct?
   - Are numbers and units preserved exactly?
   - Is there any missing or corrupted data?

2. **Structure (25%)**
   - Is the table structure clear with borders?
   - Are headers visually distinct from data rows?
   - Are rows and columns properly aligned?
   - Are cell boundaries clear?

3. **Readability (25%)**
   - Is column alignment appropriate?
   - Is the table width reasonable (not too wide or narrow)?
   - Is text wrapping handled well for long content?
   - Is visual hierarchy clear?

4. **Edge Case Handling (15%)**
   - Is colspan/rowspan handled appropriately?
   - Is nested HTML extracted correctly?
   - Are long text cells handled gracefully?
   - Are empty cells displayed correctly?

## Step 3: Evaluation Process

For each conversion output, follow this process:

### 3.1 Read Test Data

```python
from tests.fixtures.iherb_sample_data import (
    PRODUCT_100627_DESCRIPTION,
    PRODUCT_100627_SUPPLEMENT_FACTS,
    PRODUCT_150817_DESCRIPTION,
    PRODUCT_150817_INGREDIENTS,
    TEST_CASES
)
```

### 3.2 Generate Conversion

```python
from luminnexus_alchemy_shared.html import convert_html_to_markdown, convert_html_to_table

# For Markdown conversion
markdown_output = convert_html_to_markdown(PRODUCT_100627_DESCRIPTION)

# For Table conversion
table_output = convert_html_to_table(PRODUCT_100627_SUPPLEMENT_FACTS)
```

### 3.3 Evaluate Each Conversion

For each conversion, create a structured evaluation:

```
Test: product_100627_description
Type: HTML → Markdown

Original HTML:
<ul><li>Immune System</li>...</ul><p><strong>Paw-erful...</strong></p>

Converted Markdown:
- Immune System
...
**Paw-erful...**

Evaluation:
---
1. Information Preservation: 9/10
   - All bullet points present ✓
   - Bold text converted correctly ✓
   - One minor formatting inconsistency

2. Readability: 9/10
   - Clear spacing ✓
   - Good hierarchy ✓
   - Easy to scan ✓

3. Markdown Standards: 8/10
   - Valid syntax ✓
   - Consistent markers ✓
   - Minor: Could use more consistent spacing

4. Edge Cases: 10/10
   - HTML entities decoded correctly ✓
   - ® symbols preserved ✓
   - &amp; → & conversion correct ✓

Overall Score: 0.90 / 1.0
Status: ✅ PASS

Strengths:
• Perfect list conversion
• Correct HTML entity handling
• Clean, readable output

Issues:
• Minor spacing inconsistencies in some bullet points

Recommendation: Excellent conversion quality. Minor issues don't affect usability.
```

## Step 4: Generate Comprehensive Report

After evaluating all conversions, generate a summary report:

```markdown
# HTML Conversion Validation Report
Generated: [date]

## Summary
- Total Tests: 6
- Passed: 5 / 6 (83%)
- Failed: 1 / 6 (17%)
- Average Score: 0.87 / 1.0

## Detailed Results

### ✅ PASS - product_100627_description (Score: 0.92)
**Strengths:**
- Perfect list item conversion
- HTML entities correctly decoded
- Bold text formatting preserved

**Issues:**
- Minor spacing inconsistencies

---

### ✅ PASS - product_100627_supplement_facts (Score: 0.95)
**Strengths:**
- All data present and accurate
- Excellent visual structure
- Colspan handled correctly

**Issues:**
- None

---

### ❌ FAIL - product_150817_ingredients (Score: 0.68)
**Strengths:**
- Basic structure correct
- Headers identified

**Issues:**
- Long ingredient list not wrapped properly
- Colspan processing has errors
- Some nested HTML not extracted

---

## Overall Recommendations

### High Priority
1. Fix table colspan handling (product_150817_ingredients)
2. Improve long text wrapping in table cells

### Medium Priority
1. Standardize spacing in list conversions
2. Add support for rowspan in tables

### Low Priority
1. Consider adding heading markers for product names
2. Optimize table width for terminal display

## Scoring Distribution
- 0.90-1.00 (Excellent): 3 tests
- 0.80-0.89 (Good): 2 tests
- 0.70-0.79 (Acceptable): 0 tests
- 0.60-0.69 (Poor): 1 test
- <0.60 (Failing): 0 tests

## Next Steps
1. Address failing test (product_150817_ingredients)
2. Implement improvements from refactoring plan
3. Re-run validation to confirm fixes
```

## Step 5: Save Results

Save the validation report to:
```
docs/validation_report_[date].md
```

## Important Notes

- Be objective and thorough in your evaluation
- Consider both technical correctness and user experience
- Provide specific, actionable feedback
- Use the scoring rubrics consistently
- If a conversion is borderline, err on the side of being critical
- Document any unexpected behaviors or edge cases discovered

## Execution

Now proceed with:
1. Running the tests
2. Collecting all conversion outputs
3. Evaluating each one systematically
4. Generating the comprehensive report

Begin execution now.
