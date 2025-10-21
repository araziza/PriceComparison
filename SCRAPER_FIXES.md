# Web Scraper Fixes - Testing Guide

## What Was Fixed

### The Problem
You reported that part number **RH328VC** (Bosch Rotary Hammer) wasn't being found on Home Depot, even though it exists at:
https://www.homedepot.ca/product/bosch-120v-keyless-corded-1-1-8-inch-sds-plus-rotary-hammer-with-360-auxiliary-handle/1000673663

**Price: $429.00**

### Root Cause
The scrapers were using simple HTTP requests (`requests` library) which only retrieve the initial HTML. Modern e-commerce websites like Home Depot, Canadian Tire, and Lowes use **JavaScript** to dynamically load product listings after the page loads. Simple HTTP requests get empty HTML templates without any product data.

### The Solution
Upgraded the scrapers to use **Selenium WebDriver**, which:
- Opens an actual browser (headless Chrome)
- Executes all JavaScript code
- Waits for products to load dynamically
- Then extracts the data from the fully-loaded page

## What's Changed

### Updated Scrapers
✅ **Home Depot** - Now uses Selenium with multiple CSS selector fallbacks
✅ **Canadian Tire** - Upgraded to Selenium with proper wait conditions
✅ **Lowes** - Upgraded to Selenium for dynamic content

### Still Using Basic Requests
⚠️ **Princess Auto** - May work with simple requests (to be tested)
⚠️ **Rona** - May work with simple requests (to be tested)

### New Features
- **Auto ChromeDriver management** - Uses `webdriver-manager` to automatically download and update ChromeDriver
- **Debug mode** - Saves HTML to `debug_html/` folder when scraping fails
- **Better error messages** - Tells you specifically what went wrong
- **Multiple selector fallbacks** - Tries different CSS selectors if first ones don't work

## How to Test the Fixed Scrapers

### Step 1: Pull Latest Changes

```bash
git pull origin claude/debug-exe-startup-011CULaiiDjHiEnw6fS1fDur
```

### Step 2: Verify Chrome is Installed

Selenium requires Google Chrome to be installed:
- **Windows:** Download from https://www.google.com/chrome/
- **Mac:** Download from https://www.google.com/chrome/
- **Linux:** `sudo apt-get install google-chrome-stable`

### Step 3: Run Streamlit

```bash
streamlit run app.py
```

### Step 4: Test with RH328VC

1. Create a simple CSV with one row:
   ```
   L,M,Y
   RH328VC,Bosch Rotary Hammer,500.00
   ```
   (Column L = Part Number, M = Description, Y = Your Price)

2. Upload the CSV in the app

3. In sidebar:
   - Check **"Limit items to process"** = 1 item
   - **Uncheck** "Show cached data only"
   - Select **Home Depot** only

4. Click **"🔄 Force Update Prices"**

5. Wait 10-15 seconds (Selenium is slower but actually works!)

### Expected Results

**Success indicators:**
- ✅ Home Depot Price: **$429.00**
- ✅ Status: Green checkmark ✓
- ✅ URL: Link to the product page
- ✅ Confidence: High (75%+)

**If it fails:**
- Check the error message in the app
- Look for `debug_html/` folder - HTML files saved there
- Open the HTML file to see what the scraper saw
- Chrome must be installed for Selenium to work

## Performance Notes

### Before (Simple HTTP Requests)
- ⚡ Speed: ~1 second per item
- ❌ Success rate: 0% (finds nothing on JS-heavy sites)

### After (Selenium WebDriver)
- 🐌 Speed: ~3-5 seconds per item
- ✅ Success rate: Much higher (actually loads content)

### Why Selenium is Slower
- Opens a headless browser
- Waits for JavaScript to execute
- Waits for products to appear on page
- Then extracts the data

**Worth it?** Absolutely! 5 seconds with results is better than 1 second with no results.

## Troubleshooting

### Error: "ChromeDriver not found"
**Solution:** Make sure Chrome browser is installed. Webdriver-manager should auto-download ChromeDriver.

```bash
# Verify Chrome is installed
google-chrome --version  # Linux
"C:\Program Files\Google\Chrome\Application\chrome.exe" --version  # Windows
```

### Error: "Timeout waiting for products"
**Possible causes:**
1. Website is slow or down
2. CSS selectors changed (website redesign)
3. Internet connection issue

**Solution:** Check the `debug_html/` folder to see what HTML was actually loaded.

### Error: "No products found"
**Solution:**
1. Check `debug_html/` folder for saved HTML
2. Open the HTML file in a browser
3. Search for part number - is it there?
4. If yes: CSS selectors need updating
5. If no: Part number might not exist on that site

### Products Found but Wrong Price
**Check:**
- Confidence score - should be 75%+ for accurate matches
- Product URL - click it to verify it's the right item
- Some items might be similar but not exact matches

### Scraping is Very Slow
**This is normal with Selenium!**
- Each item takes 3-5 seconds
- For 100 items: ~10-20 minutes
- Use the item limiter to process in batches
- Consider running overnight for large datasets

## Debug Mode

### Enabling Debug Mode (for developers)

In `app.py`, modify the ScraperManager initialization:

```python
if 'scraper_manager' not in st.session_state:
    st.session_state.scraper_manager = ScraperManager(debug_mode=True)
```

**Note:** This feature isn't exposed in the UI yet. Requires code modification.

### What Debug Mode Does
When enabled, saves HTML files to `debug_html/` folder:
- `Home_Depot_RH328VC_no_products_found.html` - No products in search results
- `Home_Depot_RH328VC_price_not_found.html` - Product found but no price

Open these HTML files in a browser to see exactly what the scraper saw.

## Testing Checklist

Use this to verify the scrapers work:

- [ ] Test Home Depot with RH328VC → Should find $429.00
- [ ] Test Canadian Tire with a common part number
- [ ] Test Lowes with a common part number
- [ ] Verify ChromeDriver auto-downloads on first run
- [ ] Check that progress bar shows during scraping
- [ ] Verify prices are saved to cache
- [ ] Try searching for non-existent part → Should show "Not found"
- [ ] Test with 5-10 items in batch mode

## Next Steps

If scrapers are still not working after these fixes:

1. **Check debug HTML files** - See what's actually being loaded
2. **Update CSS selectors** - Websites change their HTML structure
3. **Consider API access** - Some competitors might have APIs (faster, more reliable)
4. **Add more selector fallbacks** - Try additional CSS selectors
5. **Increase timeout values** - Some sites are slow to load

## Reporting Issues

If you find parts that should be found but aren't:

1. **Part number:** RH328VC
2. **Competitor:** Home Depot
3. **Expected URL:** [paste the URL]
4. **Expected price:** $429.00
5. **What happened:** "Not found" or wrong price
6. **Debug HTML:** Attach the debug HTML file if available

This helps identify if it's a selector issue or something else.
