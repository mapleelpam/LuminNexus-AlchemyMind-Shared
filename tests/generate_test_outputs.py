"""
Generate human-readable test output files for manual review.

This script converts all test HTML samples to Markdown and saves them
to the output/test_conversions/ directory for easy human review.
"""

from pathlib import Path
from datetime import datetime

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
)


def generate_output_file(filename: str, content: str, html_input: str = None):
    """Generate a markdown output file with metadata."""
    output_dir = Path("output/test_conversions")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / filename

    with open(output_path, "w", encoding="utf-8") as f:
        # Header
        f.write("# HTML to Markdown Conversion Test Output\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")

        # Original HTML (if provided)
        if html_input:
            f.write("## Original HTML\n\n")
            f.write("```html\n")
            f.write(html_input[:500])  # First 500 chars
            if len(html_input) > 500:
                f.write("\n... (truncated)")
            f.write("\n```\n\n")
            f.write("---\n\n")

        # Converted output
        f.write("## Converted Markdown\n\n")
        f.write(content)
        f.write("\n")

    return output_path


def main():
    """Generate all test output files."""
    print("=" * 80)
    print("Generating Test Conversion Outputs")
    print("=" * 80)
    print()

    test_cases = [
        # Product 147956 - Probiotic Gummies
        {
            "id": "147956",
            "name": "Lemme Debloat - Probiotic Gummies",
            "tests": [
                ("description", PRODUCT_147956_DESCRIPTION, convert_html_to_markdown),
                ("suggested_use", PRODUCT_147956_SUGGESTED_USE, convert_html_to_markdown),
                ("supplement_facts_markdown", PRODUCT_147956_SUPPLEMENT_FACTS, convert_html_to_markdown),
                ("supplement_facts_table", PRODUCT_147956_SUPPLEMENT_FACTS, convert_html_to_table),
            ]
        },
        # Product 128082 - B Vitamin Complex
        {
            "id": "128082",
            "name": "DaVinci Methyl Benefits - B Vitamin Complex",
            "tests": [
                ("description", PRODUCT_128082_DESCRIPTION, convert_html_to_markdown),
                ("suggested_use", PRODUCT_128082_SUGGESTED_USE, convert_html_to_markdown),
                ("supplement_facts_markdown", PRODUCT_128082_SUPPLEMENT_FACTS, convert_html_to_markdown),
                ("supplement_facts_table", PRODUCT_128082_SUPPLEMENT_FACTS, convert_html_to_table),
            ]
        },
        # Product 116921 - Mineral Complex
        {
            "id": "116921",
            "name": "Mineral Complex with Quercetin",
            "tests": [
                ("supplement_facts_markdown", PRODUCT_116921_SUPPLEMENT_FACTS, convert_html_to_markdown),
                ("supplement_facts_table", PRODUCT_116921_SUPPLEMENT_FACTS, convert_html_to_table),
            ]
        },
        # Product 113511 - Simple Quercetin
        {
            "id": "113511",
            "name": "Quercetin 500mg",
            "tests": [
                ("supplement_facts_markdown", PRODUCT_113511_SUPPLEMENT_FACTS, convert_html_to_markdown),
                ("supplement_facts_table", PRODUCT_113511_SUPPLEMENT_FACTS, convert_html_to_table),
            ]
        },
        # Product 129950 - Protein Powder (Multi-serving)
        {
            "id": "129950",
            "name": "Protein Powder - Multi-Serving",
            "tests": [
                ("supplement_facts_markdown", PRODUCT_129950_SUPPLEMENT_FACTS, convert_html_to_markdown),
                ("supplement_facts_table", PRODUCT_129950_SUPPLEMENT_FACTS, convert_html_to_table),
            ]
        },
    ]

    generated_files = []

    for product in test_cases:
        product_id = product["id"]
        product_name = product["name"]

        print(f"Product {product_id}: {product_name}")
        print("-" * 60)

        for test_type, html_input, converter_func in product["tests"]:
            # Convert
            result = converter_func(html_input)

            # Generate filename
            filename = f"product_{product_id}_{test_type}.md"

            # Save to file
            output_path = generate_output_file(filename, result, html_input)
            generated_files.append(output_path)

            print(f"  ✅ {test_type:<30} → {filename}")

        print()

    # Generate index file
    index_path = Path("output/test_conversions/INDEX.md")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("# Test Conversion Outputs - Index\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("This directory contains HTML to Markdown conversion outputs for manual review.\n\n")
        f.write("## Test Products\n\n")

        for product in test_cases:
            f.write(f"### Product {product['id']}: {product['name']}\n\n")
            for test_type, _, _ in product["tests"]:
                filename = f"product_{product['id']}_{test_type}.md"
                f.write(f"- [{test_type}](./{filename})\n")
            f.write("\n")

    print("=" * 80)
    print(f"✅ Generated {len(generated_files)} output files")
    print(f"✅ Created index file: {index_path}")
    print()
    print("📁 Output directory: output/test_conversions/")
    print("=" * 80)


if __name__ == "__main__":
    main()
