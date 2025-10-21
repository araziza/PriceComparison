"""
Test direct product URL access
This tests if we can scrape a product by going directly to its URL
instead of searching for it
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import time

print("=" * 70)
print("DIRECT URL PRODUCT TEST")
print("=" * 70)
print()

# Test URLs
test_urls = [
    {
        'name': 'Rona RH328VC',
        'url': 'https://www.rona.ca/en/product/bosch-1-1-8-in-sds-plus-corded-hammer-drill-8-amp-motor-multi-function-selector-variable-speed-rh328vc-19835429',
        'expected_price': 449.00,
        'part_number': 'RH328VC'
    },
    {
        'name': 'Canadian Tire RH540M',
        'url': 'https://www.canadiantire.ca/en/pdp/bosch-rh540m-sds-max-1-9-16-in-combination-hammer-7748301p.html',
        'expected_price': 599.99,
        'part_number': 'RH540M'
    }
]

def scrape_direct_url(name, url, expected_price, part_number):
    """Scrape a product page directly"""
    print(f"\nTesting: {name}")
    print(f"URL: {url}")
    print(f"Expected: ${expected_price:.2f}")
    print()

    driver = None
    try:
        # Setup Chrome
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)

        # Load the page
        print("Loading page...")
        driver.get(url)
        time.sleep(3)

        # Parse
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Save debug HTML
        with open(f'debug_html/direct_{part_number}.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(f"✓ Saved HTML to debug_html/direct_{part_number}.html")

        # Look for price
        prices_found = re.findall(r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', driver.page_source)

        if prices_found:
            print(f"\nPrices found on page: {', '.join(['$' + p for p in prices_found[:10]])}")

            # Check if expected price is there
            expected_str = f"{expected_price:.2f}".replace('.00', '')
            for price in prices_found:
                price_val = float(price.replace(',', ''))
                if abs(price_val - expected_price) < 5:
                    print(f"\n✓✓✓ FOUND! Price: ${price_val:.2f}")
                    print(f"    Matches expected: ${expected_price:.2f}")
                    return True
        else:
            print("\n✗ No prices found on page")

        # Check if part number is on page
        if part_number.upper() in driver.page_source.upper():
            print(f"✓ Part number '{part_number}' found on page")
        else:
            print(f"✗ Part number '{part_number}' NOT on page")

        # Check page title
        title = soup.find('title')
        if title:
            print(f"\nPage title: {title.text.strip()[:100]}")

        # Check for "out of stock" or "unavailable"
        text_lower = driver.page_source.lower()
        if 'out of stock' in text_lower or 'unavailable' in text_lower:
            print("\n⚠ Product may be out of stock or unavailable")

        if 'discontinued' in text_lower:
            print("\n⚠ Product may be discontinued")

        if '404' in text_lower or 'not found' in text_lower:
            print("\n⚠ Page shows 404 or Not Found")

        return False

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

    finally:
        if driver:
            driver.quit()

# Run tests
print("Testing direct product URLs...")
print("=" * 70)

results = []
for test in test_urls:
    found = scrape_direct_url(**test)
    results.append({'name': test['name'], 'found': found})
    print()
    print("-" * 70)

# Summary
print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)

for result in results:
    status = "✓ FOUND" if result['found'] else "✗ NOT FOUND"
    print(f"{result['name']}: {status}")

print()
print("Check debug_html/ folder for saved HTML files")
print("=" * 70)
