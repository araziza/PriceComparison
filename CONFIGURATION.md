# Configuration Guide

This guide explains how to customize the Nitro Price Comparison Tool to suit your needs.

## Configuration File: config.py

All customizable settings are located in `config.py`. Edit this file to change application behavior.

---

## 1. Branding Colors

### Nitro Brand Colors
```python
NITRO_ORANGE = "#FF6B35"   # Main accent color
NITRO_BLACK = "#1A1A1A"    # Primary dark color
NITRO_GREY = "#757575"     # Secondary grey
NITRO_LIGHT_GREY = "#E0E0E0"  # Light background grey
NITRO_WHITE = "#FFFFFF"    # White
```

**How to customize:**
- Replace hex codes with your preferred colors
- Use online color pickers to find hex codes
- Test changes by restarting the application

**Example:**
```python
NITRO_ORANGE = "#FF5722"  # Different orange shade
```

### Price Comparison Colors
```python
COLOR_CHEAPER = "#4CAF50"         # Green - we're cheaper
COLOR_MORE_EXPENSIVE = "#F44336"  # Red - we're more expensive
COLOR_EQUAL = "#FFC107"           # Yellow - equal pricing
COLOR_NO_DATA = "#9E9E9E"        # Grey - no data
```

**Tip:** Use colorblind-friendly palettes for accessibility.

---

## 2. Competitor Websites

### Current Competitors
```python
COMPETITORS = {
    "Princess Auto": "https://www.princessauto.com",
    "Canadian Tire": "https://www.canadiantire.ca",
    "Home Depot": "https://www.homedepot.ca",
    "Lowes": "https://www.lowes.ca",
    "Rona": "https://www.rona.ca"
}
```

### Adding New Competitors
1. Add entry to COMPETITORS dictionary
2. Create new scraper class in `scrapers.py`
3. Register in ScraperManager

**Example:**
```python
COMPETITORS = {
    "Princess Auto": "https://www.princessauto.com",
    "Canadian Tire": "https://www.canadiantire.ca",
    "Home Depot": "https://www.homedepot.ca",
    "Lowes": "https://www.lowes.ca",
    "Rona": "https://www.rona.ca",
    "New Store": "https://www.newstore.ca"  # Added
}
```

### Removing Competitors
Simply comment out or delete the line:
```python
# "Princess Auto": "https://www.princessauto.com",  # Disabled
```

---

## 3. CSV Column Mappings

### Default Mapping
```python
CSV_COLUMNS = {
    "part_number": 11,       # Column L (0-indexed)
    "part_description": 12,  # Column M
    "nitro_price": 24        # Column Y
}
```

### Changing Columns
If your CSV uses different columns:

1. Count columns from left (A=0, B=1, C=2, etc.)
2. Update the indices

**Example:** If your data is in columns A, B, C:
```python
CSV_COLUMNS = {
    "part_number": 0,       # Column A
    "part_description": 1,  # Column B
    "nitro_price": 2        # Column C
}
```

**Excel Column Reference:**
| Excel | Index | Excel | Index | Excel | Index |
|-------|-------|-------|-------|-------|-------|
| A | 0 | J | 9 | S | 18 |
| B | 1 | K | 10 | T | 19 |
| C | 2 | L | 11 | U | 20 |
| D | 3 | M | 12 | V | 21 |
| E | 4 | N | 13 | W | 22 |
| F | 5 | O | 14 | X | 23 |
| G | 6 | P | 15 | Y | 24 |
| H | 7 | Q | 16 | Z | 25 |
| I | 8 | R | 17 | | |

---

## 4. Scraping Settings

### Timeout and Delays
```python
SCRAPE_TIMEOUT = 30    # Maximum time to wait for a page (seconds)
SCRAPE_DELAY = 2       # Delay between requests (seconds)
MAX_RETRIES = 3        # Number of retry attempts
```

**When to adjust:**
- **Slow internet**: Increase SCRAPE_TIMEOUT
- **Getting blocked**: Increase SCRAPE_DELAY
- **Frequent failures**: Increase MAX_RETRIES

**Recommended values:**
- Fast, reliable connection: DELAY=1, TIMEOUT=20
- Slow connection: DELAY=3, TIMEOUT=60
- Avoiding blocks: DELAY=5, TIMEOUT=30

### User Agent
```python
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."
```

**Note:** Some websites block scrapers. Changing user agent can help.

Find user agents at: https://www.useragentstring.com/

---

## 5. Cache Settings

### Cache File Location
```python
CACHE_FILE = "price_cache.json"
```

Change to store cache elsewhere:
```python
CACHE_FILE = "/path/to/my/cache.json"
```

### Cache Expiry
```python
CACHE_EXPIRY_HOURS = 24  # Cache valid for 24 hours
```

**Adjust based on needs:**
- Daily scraping: 24 hours
- Frequent updates: 6-12 hours
- Weekly checks: 168 hours (1 week)

**Example:**
```python
CACHE_EXPIRY_HOURS = 12  # Refresh twice daily
```

---

## 6. Matching Confidence Thresholds

### Confidence Levels
```python
CONFIDENCE_HIGH = 0.8    # 80% match or better
CONFIDENCE_MEDIUM = 0.6  # 60-80% match
CONFIDENCE_LOW = 0.4     # 40-60% match
```

**What they mean:**
- **High**: Very likely the correct product
- **Medium**: Probably correct, verify if critical
- **Low**: May not be correct match

**Adjusting:**
- Stricter matching: Increase values (0.85, 0.7, 0.5)
- More lenient: Decrease values (0.75, 0.55, 0.35)

---

## 7. Excel Export Settings

### Export Filename
```python
EXPORT_FILENAME_PREFIX = "nitro_price_comparison_"
```

Results in files like: `nitro_price_comparison_20241021_143022.xlsx`

**Customize:**
```python
EXPORT_FILENAME_PREFIX = "price_report_"
```

---

## Advanced Configuration

### Streamlit Settings

Create `.streamlit/config.toml` for advanced UI customization:

```toml
[theme]
primaryColor = "#FF6B35"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#1A1A1A"
font = "sans serif"

[server]
port = 8501
headless = true
```

### Performance Tuning

For large datasets, adjust in `data_handler.py`:

```python
# Increase batch size for faster processing
BATCH_SIZE = 100

# Disable progress bars for speed
SHOW_PROGRESS = False
```

---

## Configuration Examples

### Example 1: Conservative Scraping
For websites that are sensitive to scraping:

```python
SCRAPE_TIMEOUT = 45
SCRAPE_DELAY = 5
MAX_RETRIES = 5
```

### Example 2: Fast Scraping
For reliable connections and tolerant websites:

```python
SCRAPE_TIMEOUT = 15
SCRAPE_DELAY = 1
MAX_RETRIES = 2
```

### Example 3: Custom Branding
For different company colors:

```python
NITRO_ORANGE = "#0066CC"    # Blue instead
NITRO_BLACK = "#2C3E50"     # Dark blue-grey
COLOR_CHEAPER = "#27AE60"   # Different green
```

---

## Testing Configuration Changes

After making changes:

1. **Save** `config.py`
2. **Restart** the application
3. **Test** with a small dataset first
4. **Verify** colors and behavior
5. **Scale up** once confirmed working

---

## Troubleshooting Configuration

### Changes not appearing
- Ensure you saved `config.py`
- Restart the Streamlit server (Ctrl+C, then rerun)
- Clear browser cache (Ctrl+Shift+R)

### Scraping errors after changes
- Revert SCRAPE_TIMEOUT, SCRAPE_DELAY, MAX_RETRIES to defaults
- Test with one competitor at a time
- Check internet connection

### Color changes not visible
- Check hex codes are valid (# followed by 6 characters)
- Clear browser cache
- Try a different browser

### Cache not clearing
- Manually delete `price_cache.json`
- Check file permissions
- Verify CACHE_FILE path is correct

---

## Best Practices

1. **Backup before changes**: Copy `config.py` before editing
2. **Test incrementally**: Change one thing at a time
3. **Document changes**: Add comments explaining why you changed values
4. **Monitor performance**: Watch for increased errors or slowdowns
5. **Keep defaults**: Comment out original values instead of deleting

**Example:**
```python
# Original: SCRAPE_DELAY = 2
SCRAPE_DELAY = 5  # Increased to avoid rate limiting
```

---

## Need Help?

- Review default values in `config.py`
- Check error messages for hints
- Test with sample data first
- Consult README.md for related topics

---

**Remember:** Always test configuration changes with a small dataset before running on your full catalog!
