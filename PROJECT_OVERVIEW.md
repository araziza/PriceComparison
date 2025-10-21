# Nitro Price Comparison Tool - Project Overview

## 🎯 Project Purpose

This tool enables Nitro Industrial Supply to automatically compare part prices against major Canadian competitors, providing real-time competitive intelligence for pricing decisions.

---

## 📋 Document Guide

### Getting Started
1. **[QUICKSTART.md](QUICKSTART.md)** - Start here! Get up and running in 5 minutes
2. **[README.md](README.md)** - Full documentation and feature list
3. **[sample_parts_template.csv](sample_parts_template.csv)** - Template for your data

### Configuration & Customization
4. **[CONFIGURATION.md](CONFIGURATION.md)** - Detailed configuration guide
5. **[config.py](config.py)** - Main configuration file (edit this)

### Development & Building
6. **[build_exe.py](build_exe.py)** - Create portable executable
7. **[requirements.txt](requirements.txt)** - Python dependencies
8. **[CHANGELOG.md](CHANGELOG.md)** - Version history

### Launcher Scripts
9. **[run_nitro_price_comparison.bat](run_nitro_price_comparison.bat)** - Windows launcher
10. **[run_nitro_price_comparison.sh](run_nitro_price_comparison.sh)** - Linux/Mac launcher

---

## 🏗️ Project Structure

```
PriceComparison/
│
├── app.py                              # Main Streamlit application
├── config.py                           # Configuration settings
├── data_handler.py                     # CSV parsing & cache management
├── scrapers.py                         # Web scraping logic
│
├── requirements.txt                    # Python dependencies
├── .gitignore                         # Git ignore rules
│
├── README.md                          # Full documentation
├── QUICKSTART.md                      # Quick start guide
├── CONFIGURATION.md                   # Configuration guide
├── CHANGELOG.md                       # Version history
├── PROJECT_OVERVIEW.md               # This file
│
├── build_exe.py                       # Executable builder
├── run_nitro_price_comparison.bat    # Windows launcher
├── run_nitro_price_comparison.sh     # Unix launcher
│
├── sample_parts_template.csv         # Sample CSV template
│
└── price_cache.json                  # Cache file (auto-generated)
```

---

## 🚀 Quick Reference

### Running the Application

**Option 1: Python (Recommended)**
```bash
streamlit run app.py
```

**Option 2: Launcher Script**
- Windows: Double-click `run_nitro_price_comparison.bat`
- Linux/Mac: Run `./run_nitro_price_comparison.sh`

**Option 3: Portable Executable**
```bash
python build_exe.py
./dist/NitroPriceComparison
```

### Common Tasks

#### Upload New Data
1. Prepare CSV with columns L, M, Y
2. Click "Upload Parts CSV" in sidebar
3. Select your file

#### Scrape Competitor Prices
1. Select competitors (all by default)
2. Click "Force Update Prices"
3. Wait for completion

#### Export Results
1. Click "Export to Excel"
2. Click "Download Excel File"
3. Open in Excel

#### Clear Cache
1. Open sidebar
2. Scroll to "Cache Management"
3. Click "Clear All Cache"

---

## 🎨 Features at a Glance

### Core Features
- ✅ Multi-competitor price scraping (5 retailers)
- ✅ CSV import (Excel format compatible)
- ✅ Intelligent product matching with confidence scores
- ✅ Price caching (24-hour expiry)
- ✅ Excel export with formatting

### Dashboard Features
- ✅ Modern web-based UI with Nitro branding
- ✅ Color-coded price comparisons
- ✅ Fixed header scrolling
- ✅ Real-time summary metrics
- ✅ Data freshness indicators

### Filtering & Analysis
- ✅ Full-text search
- ✅ Price difference filters
- ✅ Sort by multiple columns
- ✅ Competitor selection
- ✅ Percentage difference calculations

### Data Quality
- ✅ Confidence scoring
- ✅ Error handling with user-friendly messages
- ✅ Cache statistics
- ✅ Status indicators
- ✅ Retry logic

---

## 🔧 Technology Stack

### Frontend
- **Streamlit**: Web dashboard framework
- **HTML/CSS**: Custom styling

### Backend
- **Python 3.8+**: Core language
- **Pandas**: Data manipulation
- **BeautifulSoup4**: HTML parsing
- **Selenium**: JavaScript-heavy sites
- **Requests**: HTTP requests

### Data Processing
- **FuzzyWuzzy**: String matching
- **openpyxl**: Excel export
- **JSON**: Cache storage

### Build Tools
- **PyInstaller**: Executable creation
- **pip**: Dependency management

---

## 📊 Supported Competitors

| Competitor | Website | Status |
|------------|---------|--------|
| Princess Auto | princessauto.com | ✅ Active |
| Canadian Tire | canadiantire.ca | ✅ Active |
| Home Depot | homedepot.ca | ✅ Active |
| Lowes | lowes.ca | ✅ Active |
| Rona | rona.ca | ✅ Active |

**Note:** All scrapers target Canadian sites with CAD pricing.

---

## 🎯 Use Cases

### 1. Competitive Pricing Analysis
**Goal:** Identify parts where competitors are significantly cheaper
**Steps:**
1. Upload full catalog
2. Scrape all competitors
3. Filter: "Competitors 10%+ Cheaper"
4. Export for pricing review

### 2. Market Positioning
**Goal:** Understand overall competitive position
**Steps:**
1. Upload key products
2. Scrape all competitors
3. Review summary metrics
4. Track trends over time

### 3. Quick Price Checks
**Goal:** Check specific part pricing
**Steps:**
1. Upload single part or small list
2. Use search to find part
3. Click "Force Update Prices"
4. Review instantly

### 4. Regular Monitoring
**Goal:** Weekly competitive intelligence
**Steps:**
1. Upload catalog every Monday
2. Scrape all competitors
3. Export results
4. Compare with previous week
5. Identify pricing opportunities

---

## ⚙️ Configuration Quick Reference

### Key Settings in config.py

```python
# Branding
NITRO_ORANGE = "#FF6B35"
NITRO_BLACK = "#1A1A1A"

# Scraping
SCRAPE_TIMEOUT = 30      # seconds
SCRAPE_DELAY = 2         # seconds between requests
MAX_RETRIES = 3

# Cache
CACHE_EXPIRY_HOURS = 24

# CSV Columns (0-indexed)
CSV_COLUMNS = {
    "part_number": 11,      # Column L
    "part_description": 12, # Column M
    "nitro_price": 24       # Column Y
}
```

---

## 🐛 Troubleshooting Quick Guide

| Issue | Solution |
|-------|----------|
| App won't start | Install dependencies: `pip install -r requirements.txt` |
| Scraping fails | Increase SCRAPE_DELAY in config.py |
| No matches found | Verify part numbers and descriptions |
| Slow performance | Clear cache, reduce dataset size |
| Excel export fails | Check openpyxl is installed |

See [README.md](README.md) for detailed troubleshooting.

---

## 📈 Performance Tips

### For Large Datasets (1000+ parts)
1. Scrape in batches
2. Increase cache expiry to reduce re-scraping
3. Use filters to focus on important parts
4. Schedule overnight scraping

### For Reliable Results
1. Use specific part numbers
2. Include detailed descriptions
3. Monitor confidence scores
4. Manually verify low-confidence matches

### For Fast Scraping
1. Select only needed competitors
2. Use cached data when possible
3. Optimize SCRAPE_DELAY (careful not to get blocked)
4. Run during off-peak hours

---

## 🔒 Important Considerations

### Legal & Ethical
- Web scraping should comply with websites' terms of service
- Respect rate limits and robots.txt
- Use reasonable delays between requests
- This tool is for competitive intelligence, not data theft

### Data Privacy
- Cache file may contain competitor pricing data
- Secure storage recommended
- Regular cache clearing advised
- Consider encryption for sensitive data

### Maintenance
- Competitor websites change frequently
- Scrapers may need periodic updates
- Test regularly with sample data
- Keep Python and dependencies updated

---

## 🚀 Next Steps

### Immediate Actions
1. Read [QUICKSTART.md](QUICKSTART.md)
2. Install dependencies
3. Run with sample data
4. Test with your CSV

### Short Term (First Week)
1. Upload your full catalog
2. Scrape all competitors
3. Analyze results
4. Adjust configuration as needed

### Long Term (Ongoing)
1. Schedule regular scraping
2. Monitor for scraper failures
3. Track pricing trends
4. Expand to additional competitors

---

## 📞 Support Resources

### Documentation
- [QUICKSTART.md](QUICKSTART.md) - Getting started
- [README.md](README.md) - Full documentation
- [CONFIGURATION.md](CONFIGURATION.md) - Customization
- [CHANGELOG.md](CHANGELOG.md) - Version history

### Code Files
- [app.py](app.py) - Main application
- [scrapers.py](scrapers.py) - Scraping logic
- [data_handler.py](data_handler.py) - Data management
- [config.py](config.py) - Settings

### Tools
- [build_exe.py](build_exe.py) - Create executable
- [sample_parts_template.csv](sample_parts_template.csv) - CSV template

---

## 📋 Version Information

- **Current Version**: 1.0.0
- **Release Date**: 2024-10-21
- **Python Required**: 3.8+
- **Platform**: Windows, Linux, macOS

---

## 🎓 Learning Resources

### Understanding the Code
1. **app.py** - Start here to understand the UI
2. **scrapers.py** - Learn how scraping works
3. **data_handler.py** - See how data is managed
4. **config.py** - Understand configuration options

### Streamlit Documentation
- Official docs: https://docs.streamlit.io
- Gallery: https://streamlit.io/gallery
- Community: https://discuss.streamlit.io

### Web Scraping Best Practices
- BeautifulSoup: https://www.crummy.com/software/BeautifulSoup/
- Selenium: https://selenium-python.readthedocs.io
- Ethics: https://scraping.pro/web-scraping-ethics/

---

## 🤝 Contributing

### Reporting Issues
1. Document the problem clearly
2. Include error messages
3. Provide steps to reproduce
4. Note your environment (OS, Python version)

### Suggesting Features
1. Describe the use case
2. Explain expected behavior
3. Consider implementation complexity
4. Discuss with team first

### Code Changes
1. Test thoroughly with sample data
2. Update documentation
3. Follow existing code style
4. Comment complex logic

---

**Welcome to the Nitro Price Comparison Tool!**

Start with [QUICKSTART.md](QUICKSTART.md) to get up and running in minutes.
