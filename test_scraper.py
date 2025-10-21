"""
Diagnostic Test Script for Web Scrapers
Run this to test if the scrapers are working and see detailed error messages
"""

import sys
import os

print("=" * 60)
print("Web Scraper Diagnostic Test")
print("=" * 60)
print()

# Test 1: Check imports
print("Test 1: Checking required packages...")
try:
    import requests
    print("✓ requests installed")
except ImportError:
    print("✗ requests NOT installed - run: pip install requests")
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
    print("✓ BeautifulSoup installed")
except ImportError:
    print("✗ beautifulsoup4 NOT installed - run: pip install beautifulsoup4")
    sys.exit(1)

try:
    from selenium import webdriver
    print("✓ Selenium installed")
except ImportError:
    print("✗ selenium NOT installed - run: pip install selenium")
    sys.exit(1)

try:
    from webdriver_manager.chrome import ChromeDriverManager
    print("✓ webdriver-manager installed")
except ImportError:
    print("✗ webdriver-manager NOT installed - run: pip install webdriver-manager")
    sys.exit(1)

print()

# Test 2: Check Chrome
print("Test 2: Checking for Chrome browser...")
import subprocess

chrome_paths = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/usr/bin/google-chrome",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
]

chrome_found = False
for path in chrome_paths:
    if os.path.exists(path):
        print(f"✓ Chrome found at: {path}")
        chrome_found = True
        break

if not chrome_found:
    print("✗ Chrome NOT found - please install Google Chrome")
    print("  Download from: https://www.google.com/chrome/")
    sys.exit(1)

print()

# Test 3: Test ChromeDriver installation
print("Test 3: Testing ChromeDriver...")
try:
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options

    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    print("  Installing/updating ChromeDriver (this may take a moment)...")
    service = Service(ChromeDriverManager().install())

    print("  Creating test driver...")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    print("✓ ChromeDriver working!")
    driver.quit()
except Exception as e:
    print(f"✗ ChromeDriver failed: {e}")
    sys.exit(1)

print()

# Test 4: Test actual scraping
print("Test 4: Testing Home Depot scraper with RH328VC...")
print()

try:
    from scrapers import HomeDepotScraper

    scraper = HomeDepotScraper()
    scraper.debug_mode = True  # Enable debug mode

    print("  Searching for: RH328VC (Bosch Rotary Hammer)")
    print("  This will take 10-15 seconds...")
    print()

    price, url, confidence, status = scraper.search_product("RH328VC", "Bosch Rotary Hammer")

    print("-" * 60)
    print("RESULTS:")
    print("-" * 60)
    print(f"Price:      {f'${price:.2f}' if price else 'NOT FOUND'}")
    print(f"URL:        {url if url else 'N/A'}")
    print(f"Confidence: {f'{confidence:.1%}' if confidence else 'N/A'}")
    print(f"Status:     {status}")
    print("-" * 60)
    print()

    if price:
        print("✓ SUCCESS! Scraper is working!")
        print(f"  Expected: $429.00")
        print(f"  Got:      ${price:.2f}")

        if abs(price - 429.00) < 5.00:
            print("  ✓ Price matches!")
        else:
            print("  ⚠ Price is different - might be a different product or price changed")
    else:
        print("✗ FAILED: No price found")
        print()
        print("Troubleshooting:")
        print("1. Check debug_html/ folder for saved HTML")
        print("2. Make sure you have internet connection")
        print("3. Home Depot website might have changed structure")
        print("4. Part number might not exist on their site")

except Exception as e:
    print(f"✗ ERROR: {e}")
    print()
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 60)
print("Diagnostic test complete!")
print("=" * 60)
