"""
Detailed Rona HTML Inspector - Find where RH328VC actually appears
"""

from bs4 import BeautifulSoup
import re

print("=" * 70)
print("DETAILED RONA INSPECTION")
print("=" * 70)
print()

# Read the Rona debug HTML
with open('debug_html/Rona_RH328VC_full_page.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

# Find all products
products_div = soup.find_all('div', class_='product-tile')
products_card = soup.find_all('div', class_='product-card')
products_all = soup.find_all('div', class_=re.compile(r'product', re.I))[:20]

print(f"Found {len(products_div)} product-tile elements")
print(f"Found {len(products_card)} product-card elements")
print(f"Found {len(products_all)} elements with 'product' in class")
print()

# Check each product for RH328VC
print("Checking each product for part numbers...")
print("-" * 70)

for i, product in enumerate(products_all[:10], 1):
    print(f"\nProduct {i}:")
    print(f"  Classes: {product.get('class', [])}")

    # Get all text from this product
    product_text = product.get_text()

    # Check for part numbers
    has_rh328vc = 'RH328VC' in product_text.upper()
    has_rh432vcq = 'RH432VCQ' in product_text.upper()
    has_rh540m = 'RH540M' in product_text.upper()

    if has_rh328vc:
        print(f"  ✓ Contains RH328VC")
    if has_rh432vcq:
        print(f"  ✓ Contains RH432VCQ")
    if has_rh540m:
        print(f"  ✓ Contains RH540M")

    # Find title
    title_elem = (
        product.find('div', class_='product-name') or
        product.find('h3') or
        product.find('h2') or
        product.find('a', class_=re.compile(r'title|name', re.I))
    )
    if title_elem:
        print(f"  Title: {title_elem.text.strip()[:80]}")

    # Find price
    price_match = re.search(r'\$\s*(\d+(?:\.\d{2})?)', product_text)
    if price_match:
        print(f"  Price: ${price_match.group(1)}")

    # Find link
    link = product.find('a', href=True)
    if link:
        href = link.get('href', '')
        if 'product' in href:
            print(f"  URL: {href[:80]}")

print()
print("=" * 70)
print("Searching entire HTML for 'RH328VC' context...")
print("=" * 70)
print()

# Find all occurrences of RH328VC with context
import re
pattern = re.compile(r'.{50}RH328VC.{50}', re.IGNORECASE)
matches = pattern.findall(html_content)

print(f"Found {len(matches)} occurrences of RH328VC in HTML")
print()
print("First 5 occurrences with context:")
print("-" * 70)

for i, match in enumerate(matches[:5], 1):
    print(f"{i}. ...{match}...")
    print()
