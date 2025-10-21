"""
HTML Inspector - Analyzes debug HTML files
"""

import os
from bs4 import BeautifulSoup
import re

def inspect_html_file(filepath):
    """Inspect an HTML file and show what's in it"""
    print("=" * 70)
    print(f"Inspecting: {os.path.basename(filepath)}")
    print("=" * 70)
    print()

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        # File size
        file_size = len(html_content)
        print(f"File size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
        print()

        # Check for products
        print("Looking for product elements...")

        # Try multiple product selectors
        products = (
            soup.find_all('div', class_=re.compile(r'product', re.I))[:5] or
            soup.find_all('article', class_=re.compile(r'product', re.I))[:5] or
            soup.find_all('div', {'data-product': True})[:5]
        )

        if products:
            print(f"✓ Found {len(products)} product elements")
            print()

            for i, product in enumerate(products, 1):
                print(f"Product {i}:")

                # Try to find title/name
                title = (
                    product.find('h1') or
                    product.find('h2') or
                    product.find('h3') or
                    product.find('a', class_=re.compile(r'title|name', re.I)) or
                    product.find('div', class_=re.compile(r'title|name', re.I))
                )
                if title:
                    print(f"  Title: {title.text.strip()[:100]}")

                # Try to find price
                price_text = product.find(string=re.compile(r'\$\s*\d+'))
                if price_text:
                    print(f"  Price text: {price_text.strip()}")

                # Try to find link
                link = product.find('a', href=True)
                if link:
                    href = link.get('href', '')[:100]
                    print(f"  Link: {href}")

                print()
        else:
            print("✗ No product elements found")
            print()
            print("Let's check what IS on the page...")
            print()

        # Search for specific part numbers in the entire HTML
        print("Searching for part numbers in HTML...")

        part_numbers = ['RH328VC', 'RH540M', 'RH432VCQ']
        for part in part_numbers:
            count = html_content.upper().count(part.upper())
            if count > 0:
                print(f"  ✓ Found '{part}' {count} times")
            else:
                print(f"  ✗ '{part}' not found")

        print()

        # Search for prices
        print("Searching for prices...")
        prices = re.findall(r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', html_content)
        if prices:
            unique_prices = sorted(set(prices), key=lambda x: float(x.replace(',', '')))
            print(f"  Found {len(prices)} price references")
            print(f"  Unique prices: {', '.join(['$' + p for p in unique_prices[:10]])}")
        else:
            print("  ✗ No prices found")

        print()

        # Check for common error messages
        print("Checking for error messages...")
        error_keywords = [
            'no results', 'not found', 'no products', 'error',
            'sorry', 'unavailable', '404', 'empty'
        ]

        text_content = soup.get_text().lower()
        for keyword in error_keywords:
            if keyword in text_content:
                # Find context around the keyword
                idx = text_content.find(keyword)
                context = text_content[max(0, idx-50):min(len(text_content), idx+50)]
                print(f"  ⚠ Found '{keyword}': ...{context.strip()}...")

        print()

        # Check page title
        title_tag = soup.find('title')
        if title_tag:
            print(f"Page title: {title_tag.text.strip()}")

        print()

        # Show first few lines of visible text
        print("First 500 characters of visible text:")
        print("-" * 70)
        visible_text = soup.get_text()[:500].strip()
        print(visible_text)
        print("-" * 70)
        print()

    except Exception as e:
        print(f"✗ Error reading file: {e}")
        import traceback
        traceback.print_exc()

    print()


if __name__ == "__main__":
    debug_folder = "debug_html"

    if not os.path.exists(debug_folder):
        print(f"✗ Debug folder '{debug_folder}' not found")
        print("Run the scraper tests first to generate debug HTML files")
        exit(1)

    # Find all HTML files
    html_files = [f for f in os.listdir(debug_folder) if f.endswith('.html')]

    if not html_files:
        print(f"✗ No HTML files found in '{debug_folder}'")
        exit(1)

    print()
    print("=" * 70)
    print(f"HTML INSPECTOR - Found {len(html_files)} files")
    print("=" * 70)
    print()

    # Inspect each file
    for filename in sorted(html_files):
        filepath = os.path.join(debug_folder, filename)
        inspect_html_file(filepath)

    print()
    print("=" * 70)
    print("Inspection complete!")
    print("=" * 70)
