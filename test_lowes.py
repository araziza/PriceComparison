#!/usr/bin/env python3
"""
Test script for Lowes scraper
Tests with specific part number provided by user
"""

import sys
from scrapers import LowesScraper

def test_lowes_scraper():
    """Test Lowes scraper with real product"""

    print("=" * 70)
    print("LOWES SCRAPER TEST")
    print("=" * 70)
    print()

    # Test case from user
    test_case = {
        "part_number": "GDX18V-1860CB25",
        "description": "Bosch Impact Driver",
        "expected_price": 319.00,
        "expected_url_contains": "5013988201"
    }

    print(f"Testing: {test_case['part_number']} - {test_case['description']}")
    print(f"Expected Price: ${test_case['expected_price']:.2f}")
    print()

    # Create scraper with debug mode enabled
    scraper = LowesScraper(debug_mode=True)

    print(f"  Competitor: Lowes")
    print(f"  Scraping (15-20 seconds)...", end='', flush=True)

    # Run the scraper
    price, url, confidence, status = scraper.search_product(
        test_case['part_number'],
        test_case['description']
    )

    print(" Done!")
    print()

    # Display results
    print("  Results:")
    if price:
        print(f"    Price:      ${price:.2f}")
    else:
        print(f"    Price:      NOT FOUND")
    print(f"    URL:        {url}")
    print(f"    Confidence: {confidence * 100:.1f}%")
    print(f"    Status:     {status}")
    print()

    # Validation
    passed = True
    warnings = []

    if price:
        # Check if price is within $5 of expected
        if abs(price - test_case['expected_price']) <= 5.0:
            print(f"    ✓ Price matches (within $5)")
        else:
            print(f"    ⚠ Price different: expected ${test_case['expected_price']:.2f}, got ${price:.2f}")
            warnings.append(f"Price mismatch")

        # Check URL
        if url and test_case['expected_url_contains'] in url:
            print(f"    ✓ URL correct")
        else:
            print(f"    ⚠ URL might be wrong (expected to contain {test_case['expected_url_contains']})")
            warnings.append(f"URL mismatch")

        print()

        if warnings:
            print(f"  ⚠ Lowes TEST PARTIAL - Check warnings above")
        else:
            print(f"  ✓✓✓ Lowes TEST PASSED! ✓✓✓")
    else:
        print(f"  ✗✗✗ Lowes TEST FAILED - No price found ✗✗✗")
        if status:
            print(f"  Error: {status}")
        passed = False

    print()
    print("=" * 70)
    print()

    # Summary
    if passed and not warnings:
        print("✓ Test PASSED")
        return 0
    elif price:
        print("⚠ Test PARTIAL - Price found but validation warnings")
        print()
        print("Troubleshooting:")
        print("1. Check debug_html/ folder for saved HTML files")
        print("2. Verify the expected price hasn't changed on the website")
        print("3. URL pattern might have changed")
        return 1
    else:
        print("✗ Test FAILED - No price found")
        print()
        print("Troubleshooting:")
        print("1. Check debug_html/ folder for saved HTML files")
        print("2. Verify internet connection")
        print("3. Website structure might have changed")
        print("4. Part number might not exist on Lowes")
        print()
        print(f"Debug HTML files saved to: debug_html/")
        return 2

    print()
    print("=" * 70)


if __name__ == "__main__":
    sys.exit(test_lowes_scraper())
