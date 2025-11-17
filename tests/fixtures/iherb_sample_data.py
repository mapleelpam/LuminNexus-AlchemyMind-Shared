"""Real-world test data from iHerb product catalog.

These fixtures contain actual HTML content extracted from iHerb products
to test HTML-to-Markdown and HTML-to-Table conversions with realistic data.

Source: /Users/maple/github/LuminNexus-AtlasVault-Vault/data/iherb/catalog/20250905/
Date: 2025-11-17
Selection: Randomly selected human supplement products
"""

# Product 1: Lemme Debloat - Digestive Probiotic Gummies (ID: 147956)
# Complex supplement facts table with probiotics, serving info, and daily values
PRODUCT_147956_DESCRIPTION = """<ul><li>Prebiotic &amp; Probiotic Blend with 2 Clinically-Studied Strains</li><li>Digestive Support</li><li>Dietary Supplement</li><li>No High Fructose Corn Syrup</li><li>No Artificial Sweeteners or Synthetic Colors</li><li>Gluten-Free &amp; Gelatin-Free</li><li>Vegan&nbsp; &amp; Non-GMO</li></ul><p>Go with your gut: Reduce bloating with two clinically-studied probiotics and a prebiotic that help support digestion, fuel a healthy gut and support your immune system.</p>"""

PRODUCT_147956_SUGGESTED_USE = """<p>Adults, take 2 gummies daily or as recommended by a physician.</p><p>Refrigeration not required.</p>"""

PRODUCT_147956_SUPPLEMENT_FACTS = """<table width="100%" border="1" cellspacing="0" cellpadding="3"><tbody><tr align="left" valign="top"><td colspan="3"><strong>Supplement Facts</strong></td></tr><tr align="left" valign="top"><td colspan="3"><strong>Serving Size:&nbsp;</strong>2 Gummies</td></tr><tr align="left" valign="top"><td colspan="3"><strong>Servings Per Container:&nbsp;</strong>30</td></tr><tr align="left" valign="top"><td style="width: 70%;">&nbsp;</td><td style="width: 15%;"><strong>Amount Per Serving</strong></td><td style="width: 15%;"><strong>%Daily Value</strong></td></tr><tr align="left" valign="top"><td>Calories</td><td>15</td><td><br></td></tr><tr align="left" valign="top"><td>Total Carbohydrate</td><td>4 g</td><td>1%†</td></tr><tr align="left" valign="top"><td>Total Sugars</td><td>3 g</td><td>**</td></tr><tr align="left" valign="top"><td>Includes 3 g Added Sugars</td><td><br></td><td>6%†</td></tr><tr align="left" valign="top"><td>Xylooligosaccharides (XOS)<br></td><td>80 mg</td><td>**</td></tr><tr align="left" valign="top"><td><strong>Proprietary Probiotic Blend (3 Billion CFUs‡)<br id="isPasted"></strong>Bacillus coagulans (MTCC 5856 LactoSpore®), Bacillus subtilis (DE111®)<br></td><td>44 mg</td><td>**<br>**</td></tr><tr align="left" valign="top"><td colspan="3">†Percent Daily Values are based on a 2,000 calorie diet.<br>**Daily Value not established.<br>‡Contains a minimum of 3 Billion CFUs through expiration,<br></td></tr></tbody></table>"""

# Product 2: DaVinci Laboratories Methyl Benefits - B Vitamin Complex (ID: 128082)
# Standard supplement facts table with vitamins and percentage daily values
PRODUCT_128082_DESCRIPTION = """<ul><li>Vegetarian</li><li>Gluten Free</li><li>Soy Free</li></ul><p>A dietary supplement to support healthy methylation and detoxification.</p><p id="isPasted">Simply formulated to deliver more.&nbsp;</p><p>The Benefits Line™ is designed for power. Each formula offers clinically relevant levels of evidence-based nutrients to provide more with less.</p>"""

PRODUCT_128082_SUGGESTED_USE = """<p>As a dietary supplement, take 1 capsule daily, or as directed by your healthcare practitioner.</p>"""

PRODUCT_128082_SUPPLEMENT_FACTS = """<table width="100%" border="1" cellspacing="0" cellpadding="3"><tbody><tr align="left" valign="top"><td colspan="3"><strong>Supplement Facts</strong></td></tr><tr align="left" valign="top"><td colspan="3"><strong>Serving Size: </strong>1 Capsule</td></tr><tr align="left" valign="top"><td colspan="3"><strong>Servings Per Container: </strong>60</td></tr><tr align="left" valign="top"><td width="70%">&nbsp;</td><td width="15%"><strong>Amount Per Serving</strong></td><td width="15%"><strong>%Daily Value</strong></td></tr><tr><td>Riboflavin</td><td>25 mg</td><td>1,923%</td></tr><tr><td>Vitamin B6 (as 75% Pyridoxine HCI and 25% Pyridoxal 5-Phosphate)</td><td>50 mg</td><td>2,941%</td></tr><tr><td>Folate (as L-Methyltetrahydrofolate Calcium)</td><td>2,500 mcg DFE</td><td>625%</td></tr><tr><td>Vitamin B12 (as Methylcobalamin)</td><td>1,000 mcg</td><td>41,667%</td></tr><tr><td>Trimethylglycine (Betaine Anhydrous)</td><td>500 mg</td><td>*</td></tr><tr><td colspan="3">*Daily Value not established.</td></tr></tbody></table>"""

# Product 3: 116921 - Simpler 3-column table structure
PRODUCT_116921_SUPPLEMENT_FACTS = """<table border="1" cellpadding="3" cellspacing="0" width="100%"><tbody><tr align="left" valign="top"><td colspan="3"><strong>Supplement Facts</strong></td></tr><tr align="left" valign="top"><td colspan="3"><strong>Serving Size: </strong>2 Tablets</td></tr><tr align="left" valign="top"><td colspan="3"><strong>Servings Per Container: </strong>45</td></tr><tr align="left" valign="top"><td width="70%">&nbsp;</td><td width="15%"><strong>Amount Per Serving</strong></td><td width="15%"><strong>% Daily Value</strong></td></tr><tr align="left" valign="top"><td>Vitamin C (as calcium ascorbate)</td><td>500 mg</td><td>556%</td></tr><tr align="left" valign="top"><td>Calcium (from calcium ascorbate and dicalcium phosphate)</td><td>230 mg</td><td>18%</td></tr><tr align="left" valign="top"><td>Magnesium (from magnesium oxide)</td><td>230 mg</td><td>55%</td></tr><tr align="left" valign="top"><td>Zinc (from zinc glycinate chelate)</td><td>15 mg</td><td>136%</td></tr><tr align="left" valign="top"><td>Selenium (from selenomethionine)</td><td>200 mcg</td><td>364%</td></tr><tr align="left" valign="top"><td>Copper (from copper glycinate chelate)</td><td>2 mg</td><td>222%</td></tr><tr align="left" valign="top"><td>Manganese (from manganese glycinate chelate)</td><td>5 mg</td><td>217%</td></tr><tr align="left" valign="top"><td>Quercetin</td><td>250 mg</td><td>**</td></tr><tr align="left" valign="top"><td colspan="3">**Daily Value not established.</td></tr></tbody></table>"""

# Product 4: 113511 - Simple 3-column structure with fewer nutrients
PRODUCT_113511_SUPPLEMENT_FACTS = """<table border="1" cellpadding="3" cellspacing="0" width="100%"><tbody><tr align="left" valign="top"><td colspan="3"><strong>Supplement Facts</strong></td></tr><tr align="left" valign="top"><td colspan="3"><strong>Serving Size: </strong>1 Vegetarian Capsule</td></tr><tr align="left" valign="top"><td width="65%">&nbsp;</td><td width="20%"><strong>Amount Per Serving</strong></td><td width="15%"><strong>%Daily Value</strong></td></tr><tr align="left" valign="top"><td>Quercetin</td><td>500 mg</td><td>*</td></tr><tr align="left" valign="top"><td colspan="3">*Daily Value not established</td></tr></tbody></table>"""

# Product 5: 129950 - Complex multi-serving table (protein powder style)
PRODUCT_129950_SUPPLEMENT_FACTS = """<table border="1" cellpadding="3" cellspacing="0" width="100%"><tbody><tr align="left" valign="top"><td colspan="7"><strong>Supplement Facts</strong></td></tr><tr align="left" valign="top"><td colspan="2" width="35%"><strong>Serving Size:</strong></td><td width="15%"><strong>1 Scoop (5.5 g)</strong></td><td width="15%"><strong>2 Scoops (11 g)</strong></td><td width="15%"><strong>3 Scoops (16.5 g)</strong></td></tr><tr align="left" valign="top"><td colspan="2"><strong>Servings Per Container:</strong></td><td>About 45</td><td>About 22</td><td>About 15</td></tr><tr align="left" valign="top"><td colspan="2">&nbsp;</td><td colspan="3"><strong>Amount Per Serving</strong></td></tr><tr align="left" valign="top"><td colspan="2">Calories</td><td>20</td><td>35</td><td>55</td></tr><tr align="left" valign="top"><td colspan="2">Total Fat</td><td>0 g</td><td>0 g</td><td>0 g</td></tr><tr align="left" valign="top"><td colspan="2">Total Carbohydrate</td><td>0 g</td><td>1 g</td><td>1 g</td></tr><tr align="left" valign="top"><td colspan="2">Protein</td><td>5 g</td><td>9 g</td><td>14 g</td></tr><tr align="left" valign="top"><td colspan="2">Vitamin C (as ascorbic acid)</td><td>30 mg</td><td>60 mg</td><td>90 mg</td></tr><tr align="left" valign="top"><td colspan="2">Calcium (from calcium caseinate)</td><td>45 mg</td><td>90 mg</td><td>135 mg</td></tr><tr align="left" valign="top"><td colspan="2">Sodium</td><td>70 mg</td><td>140 mg</td><td>210 mg</td></tr><tr align="left" valign="top"><td colspan="2">Potassium (from potassium phosphate)</td><td>140 mg</td><td>280 mg</td><td>420 mg</td></tr><tr align="left" valign="top"><td colspan="7"><strong>Amino Acid Profile</strong> (per serving)</td></tr><tr align="left" valign="top"><td width="5%">&nbsp;</td><td width="30%">L-Leucine</td><td>550 mg</td><td>1,100 mg</td><td>1,650 mg</td></tr><tr align="left" valign="top"><td>&nbsp;</td><td>L-Isoleucine</td><td>320 mg</td><td>640 mg</td><td>960 mg</td></tr><tr align="left" valign="top"><td>&nbsp;</td><td>L-Valine</td><td>320 mg</td><td>640 mg</td><td>960 mg</td></tr></tbody></table>"""


# Test case metadata
TEST_CASES = [
    {
        "id": "147956",
        "name": "Lemme Debloat - Digestive Probiotic Gummies",
        "category": "Gut Health / Probiotics",
        "description_html": PRODUCT_147956_DESCRIPTION,
        "suggested_use_html": PRODUCT_147956_SUGGESTED_USE,
        "supplement_facts_html": PRODUCT_147956_SUPPLEMENT_FACTS,
        "test_scenarios": [
            {
                "field": "description",
                "conversion_type": "html_to_markdown",
                "validation_criteria": [
                    "Should convert bullet list items correctly",
                    "Should handle HTML entities (&amp; -> &)",
                    "Should preserve ® trademark symbols",
                    "Should maintain paragraph structure",
                    "Should handle non-breaking spaces (&nbsp;)",
                ]
            },
            {
                "field": "suggested_use",
                "conversion_type": "html_to_markdown",
                "validation_criteria": [
                    "Should convert multiple paragraphs",
                    "Should preserve dosage instructions clearly",
                    "Should maintain readability",
                ]
            },
            {
                "field": "supplement_facts",
                "conversion_type": "html_to_table",
                "validation_criteria": [
                    "Should render as ASCII table using Rich",
                    "Should preserve serving size information",
                    "Should maintain all nutrient names and amounts",
                    "Should handle complex entries (Probiotic Blend with nested info)",
                    "Should preserve units (g, mg, CFUs)",
                    "Should show percentage daily values correctly",
                    "Should handle colspan for multi-column headers",
                    "Should preserve footnotes (†, **, ‡)",
                    "Should handle empty cells (calories with no % DV)",
                ]
            }
        ]
    },
    {
        "id": "128082",
        "name": "DaVinci Methyl Benefits - B Vitamin Complex",
        "category": "Vitamins / Vitamin B",
        "description_html": PRODUCT_128082_DESCRIPTION,
        "suggested_use_html": PRODUCT_128082_SUGGESTED_USE,
        "supplement_facts_html": PRODUCT_128082_SUPPLEMENT_FACTS,
        "test_scenarios": [
            {
                "field": "description",
                "conversion_type": "html_to_markdown",
                "validation_criteria": [
                    "Should convert bullet list items",
                    "Should preserve paragraph breaks",
                    "Should handle trademark symbols (™)",
                    "Should handle non-breaking spaces (&nbsp;)",
                    "Should maintain formatting for brand name",
                ]
            },
            {
                "field": "suggested_use",
                "conversion_type": "html_to_markdown",
                "validation_criteria": [
                    "Should convert single paragraph correctly",
                    "Should preserve dosage instructions",
                    "Should maintain professional healthcare language",
                ]
            },
            {
                "field": "supplement_facts",
                "conversion_type": "html_to_table",
                "validation_criteria": [
                    "Should render standard supplement facts table",
                    "Should preserve all vitamin names with forms (e.g., as Methylcobalamin)",
                    "Should handle long vitamin names with chemical details",
                    "Should maintain high percentage values (41,667%)",
                    "Should show asterisk for 'not established' values",
                    "Should preserve units (mg, mcg, DFE)",
                    "Should handle colspan for headers and footers",
                    "Should maintain proper alignment",
                ]
            }
        ]
    }
]


# Additional metadata for understanding the test data
TEST_DATA_INFO = {
    "source_directory": "/Users/maple/github/LuminNexus-AtlasVault-Vault/data/iherb/catalog/20250905/",
    "total_products_available": 50461,
    "selection_date": "2025-11-17",
    "selection_method": "Random sampling from Supplements category",
    "selection_criteria": [
        "Must be human supplements (not pet products)",
        "Must have supplementFacts field with substantial content",
        "Must represent common supplement types (probiotics, vitamins)",
    ],
    "key_testing_scenarios": {
        "html_entities": "Both products have &amp; and &nbsp;",
        "trademark_symbols": "Products have ® and ™ symbols",
        "complex_tables": "Product 147956 has nested probiotic blend info",
        "high_percentages": "Product 128082 has very high DV% (>40,000%)",
        "various_units": "mg, mcg, g, CFU, DFE",
        "footnotes": "†, **, ‡ symbols with explanations",
        "colspan": "Multi-column headers in supplement facts",
    }
}
