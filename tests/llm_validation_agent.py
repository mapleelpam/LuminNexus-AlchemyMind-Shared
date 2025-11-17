"""LLM-based validation agent for HTML conversion quality assessment.

This module provides a framework for using an LLM to evaluate the quality
of HTML to Markdown and HTML to Table conversions. Instead of rigid
assertion-based testing, the LLM evaluates:

1. Semantic correctness - Is all information preserved?
2. Readability - Is the output human-readable?
3. Format compliance - Does it follow Markdown/ASCII table conventions?
4. Edge case handling - Are special characters, nested structures handled correctly?

Usage:
    # After running tests, collect all validation data
    validator = LLMConversionValidator()

    # Validate Markdown conversions
    results = validator.validate_markdown_conversions(test_results)

    # Validate Table conversions
    results = validator.validate_table_conversions(test_results)
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ValidationResult:
    """Result of LLM validation for a single conversion."""

    test_name: str
    passed: bool
    score: float  # 0.0 to 1.0
    feedback: str
    issues: List[str]
    strengths: List[str]


class LLMConversionValidator:
    """Validates conversion quality using an LLM agent.

    This is designed to be used with Claude Code's Task tool or similar
    LLM agent frameworks.
    """

    def __init__(self, model: str = "claude-sonnet-3.5"):
        """Initialize validator with specified model."""
        self.model = model
        self.validation_results = []

    def validate_markdown_conversion(
        self,
        test_name: str,
        input_html: str,
        output_markdown: str,
        validation_criteria: List[str],
    ) -> ValidationResult:
        """Validate a single HTML to Markdown conversion.

        Args:
            test_name: Name of the test case
            input_html: Original HTML input
            output_markdown: Converted Markdown output
            validation_criteria: List of criteria to check

        Returns:
            ValidationResult with LLM assessment
        """
        prompt = self._build_markdown_validation_prompt(
            input_html, output_markdown, validation_criteria
        )

        # TODO: Implement actual LLM call
        # For now, return a placeholder
        # In real implementation, this would call Claude API or use Task tool
        return ValidationResult(
            test_name=test_name,
            passed=True,  # Placeholder
            score=0.85,  # Placeholder
            feedback="LLM validation not yet implemented",
            issues=[],
            strengths=[],
        )

    def validate_table_conversion(
        self,
        test_name: str,
        input_html: str,
        output_table: str,
        validation_criteria: List[str],
    ) -> ValidationResult:
        """Validate a single HTML table to ASCII table conversion.

        Args:
            test_name: Name of the test case
            input_html: Original HTML table input
            output_table: Converted ASCII table output
            validation_criteria: List of criteria to check

        Returns:
            ValidationResult with LLM assessment
        """
        prompt = self._build_table_validation_prompt(input_html, output_table, validation_criteria)

        # TODO: Implement actual LLM call
        return ValidationResult(
            test_name=test_name,
            passed=True,
            score=0.85,
            feedback="LLM validation not yet implemented",
            issues=[],
            strengths=[],
        )

    def _build_markdown_validation_prompt(
        self, input_html: str, output_markdown: str, criteria: List[str]
    ) -> str:
        """Build prompt for LLM to validate Markdown conversion."""
        return f"""You are a technical documentation expert evaluating the quality of an HTML to Markdown conversion.

**Original HTML:**
```html
{input_html}
```

**Converted Markdown:**
```markdown
{output_markdown}
```

**Evaluation Criteria:**
{chr(10).join(f"- {c}" for c in criteria)}

**Your Task:**
Evaluate the conversion quality on a scale of 0.0 to 1.0, considering:

1. **Information Preservation** (30%): Is all content from HTML present in Markdown?
   - Text content preserved
   - Formatting hints preserved (bold, italic, lists)
   - Links preserved
   - No information lost

2. **Readability** (30%): Is the Markdown human-readable and well-formatted?
   - Proper spacing and line breaks
   - Clear hierarchy
   - Easy to scan

3. **Markdown Standards** (25%): Does it follow Markdown conventions?
   - Proper list syntax
   - Correct heading markers
   - Valid table syntax (if applicable)
   - Proper escaping

4. **Edge Case Handling** (15%): Are special cases handled correctly?
   - HTML entities decoded (&amp; → &)
   - Special characters preserved (®, ™)
   - Nested structures handled
   - Empty elements handled

**Response Format (JSON):**
{{
  "passed": true/false,
  "score": 0.0-1.0,
  "feedback": "Overall assessment...",
  "issues": ["Issue 1", "Issue 2"],
  "strengths": ["Strength 1", "Strength 2"]
}}

Provide your evaluation:"""

    def _build_table_validation_prompt(
        self, input_html: str, output_table: str, criteria: List[str]
    ) -> str:
        """Build prompt for LLM to validate table conversion."""
        return f"""You are a technical documentation expert evaluating the quality of an HTML table to ASCII table conversion.

**Original HTML Table:**
```html
{input_html}
```

**Converted ASCII Table:**
```
{output_table}
```

**Evaluation Criteria:**
{chr(10).join(f"- {c}" for c in criteria)}

**Your Task:**
Evaluate the table conversion quality on a scale of 0.0 to 1.0, considering:

1. **Data Integrity** (35%): Is all table data preserved accurately?
   - All cell contents present
   - Correct values
   - No data loss
   - Numbers/units preserved

2. **Structure** (25%): Is the table structure clear and correct?
   - Headers clearly distinguished
   - Rows and columns aligned
   - Borders/separators visible
   - Cell boundaries clear

3. **Readability** (25%): Can humans easily read and understand the table?
   - Proper alignment
   - Reasonable width
   - Text not truncated unexpectedly
   - Clear visual hierarchy

4. **Edge Case Handling** (15%): Are special cases handled correctly?
   - Colspan/rowspan handled appropriately
   - Nested HTML in cells extracted
   - Long text wrapped or handled
   - Empty cells shown

**Response Format (JSON):**
{{
  "passed": true/false,
  "score": 0.0-1.0,
  "feedback": "Overall assessment...",
  "issues": ["Issue 1", "Issue 2"],
  "strengths": ["Strength 1", "Strength 2"]
}}

Provide your evaluation:"""

    def generate_validation_report(self, results: List[ValidationResult]) -> str:
        """Generate a human-readable report of all validation results.

        Args:
            results: List of validation results to report on

        Returns:
            Formatted markdown report
        """
        report = ["# HTML Conversion Validation Report\n"]
        report.append(f"Total tests: {len(results)}\n")

        passed = sum(1 for r in results if r.passed)
        report.append(f"Passed: {passed}/{len(results)}\n")

        avg_score = sum(r.score for r in results) / len(results) if results else 0
        report.append(f"Average score: {avg_score:.2%}\n\n")

        report.append("## Detailed Results\n\n")

        for result in results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            report.append(f"### {status} {result.test_name} (Score: {result.score:.1%})\n\n")
            report.append(f"**Feedback:** {result.feedback}\n\n")

            if result.strengths:
                report.append("**Strengths:**\n")
                for strength in result.strengths:
                    report.append(f"- {strength}\n")
                report.append("\n")

            if result.issues:
                report.append("**Issues:**\n")
                for issue in result.issues:
                    report.append(f"- {issue}\n")
                report.append("\n")

        return "".join(report)


# Example usage template for manual testing
MANUAL_VALIDATION_TEMPLATE = """
To manually validate conversions using Claude Code:

1. Run the tests to generate outputs:
   ```bash
   pytest tests/test_real_world_conversions.py -v
   ```

2. For each test output, use this prompt with Claude Code's Task tool:

   ```
   Please evaluate this HTML to Markdown conversion:

   **Original HTML:**
   [paste HTML]

   **Converted Markdown:**
   [paste Markdown]

   **Criteria:**
   - [criterion 1]
   - [criterion 2]

   Rate the conversion (0.0-1.0) and provide feedback on:
   - Information preservation
   - Readability
   - Format compliance
   - Edge case handling
   ```

3. Collect feedback and iterate on improvements.
"""
