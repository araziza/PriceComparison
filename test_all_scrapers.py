"""
Comprehensive Test Script for All Scrapers
Tests multiple part numbers across multiple competitors
"""

import sys

print("=" * 70)
print("COMPREHENSIVE SCRAPER TEST")
print("=" * 70)
print()

# Test cases: (part_number, description, expected_results)
test_cases = [
    {
        'part_number': 'RH328VC',
        'description': 'Bosch Rotary Hammer',
        'expected': {
            'Home Depot': {'price': 429.00, 'url_contains': '1000673663'},
            'Rona': {'price': 449.00, 'url_contains': '19835429'},
        }
    },
    {
        'part_number': 'RH540M',
        'description': 'Bosch SDS Max Hammer',
        'expected': {
            'Canadian Tire': {'price': 599.99, 'url_contains': '7748301'},
        }
    }
]

# Check imports
print("Checking dependencies...")
try:
    from scrapers import ScraperManager
    print("✓ Scrapers module loaded")
except ImportError as e:
    print(f"✗ Failed to import scrapers: {e}")
    sys.exit(1)

print()

# Initialize scraper manager
manager = ScraperManager()

# Enable debug mode for all scrapers
for scraper in manager.scrapers.values():
    scraper.debug_mode = True

print("=" * 70)
print("Running Tests...")
print("=" * 70)
print()

results = []

for test_case in test_cases:
    part_num = test_case['part_number']
    desc = test_case['description']
    expected = test_case['expected']

    print(f"\n{'=' * 70}")
    print(f"Testing: {part_num} - {desc}")
    print(f"{'=' * 70}\n")

    for competitor, expected_data in expected.items():
        print(f"  Competitor: {competitor}")
        print(f"  Expected Price: ${expected_data['price']:.2f}")
        print(f"  Scraping (15-20 seconds)...", end='', flush=True)

        try:
            result = manager.scrape_competitor(competitor, part_num, desc)

            print(" Done!")
            print()
            print(f"  Results:")
            price_str = f"${result['price']:.2f}" if result['price'] else 'NOT FOUND'
            print(f"    Price:      {price_str}")
            print(f"    URL:        {result.get('url', 'N/A')}")
            confidence_str = f"{result.get('confidence', 0):.1%}"
            print(f"    Confidence: {confidence_str}")
            print(f"    Status:     {result.get('status', 'unknown')}")

            # Validate results
            success = True
            if result['price']:
                # Check price (allow $5 variance)
                price_diff = abs(result['price'] - expected_data['price'])
                if price_diff <= 5.00:
                    print(f"    ✓ Price matches (within $5)")
                else:
                    print(f"    ⚠ Price different: expected ${expected_data['price']:.2f}, got ${result['price']:.2f}")
                    success = False

                # Check URL
                if result.get('url') and expected_data['url_contains'] in result['url']:
                    print(f"    ✓ URL correct")
                else:
                    print(f"    ⚠ URL might be wrong (expected to contain {expected_data['url_contains']})")
                    success = False

                if success:
                    print(f"\n  ✓✓✓ {competitor} TEST PASSED! ✓✓✓")
                else:
                    print(f"\n  ⚠ {competitor} TEST PARTIAL - Check warnings above")
            else:
                print(f"\n  ✗✗✗ {competitor} TEST FAILED - No price found ✗✗✗")
                print(f"  Error: {result.get('error_message', 'Unknown error')}")
                success = False

            results.append({
                'part': part_num,
                'competitor': competitor,
                'success': success,
                'price_found': result['price'] is not None
            })

        except Exception as e:
            print(f" ERROR!")
            print(f"  ✗ Exception: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                'part': part_num,
                'competitor': competitor,
                'success': False,
                'price_found': False
            })

        print()

# Summary
print()
print("=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print()

total_tests = len(results)
passed = sum(1 for r in results if r['success'])
found_price = sum(1 for r in results if r['price_found'])

print(f"Total Tests:       {total_tests}")
print(f"Passed:            {passed}/{total_tests}")
print(f"Prices Found:      {found_price}/{total_tests}")
print()

if passed == total_tests:
    print("✓✓✓ ALL TESTS PASSED! ✓✓✓")
    print()
    print("Your scrapers are working perfectly!")
elif found_price == total_tests:
    print("⚠ All prices found, but some validation warnings")
    print()
    print("Check the warnings above - prices might have changed or URLs might differ")
else:
    print("✗ Some tests failed")
    print()
    print("Failed tests:")
    for r in results:
        if not r['success']:
            print(f"  - {r['competitor']}: {r['part']}")
    print()
    print("Troubleshooting:")
    print("1. Check debug_html/ folder for saved HTML files")
    print("2. Verify internet connection")
    print("3. Website structure might have changed")
    print("4. Part numbers might not exist on those sites")

print()
print("Debug HTML files saved to: debug_html/")
print()
print("=" * 70)
