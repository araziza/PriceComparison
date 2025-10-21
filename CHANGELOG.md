# Changelog

All notable changes to the Nitro Price Comparison Tool will be documented in this file.

## [1.0.0] - 2024-10-21

### Initial Release

#### Added
- **Core Functionality**
  - CSV import supporting columns L, M, Y (Part Number, Description, Price)
  - Web scraping for 5 major Canadian competitors:
    - Princess Auto
    - Canadian Tire
    - Home Depot Canada
    - Lowes Canada
    - Rona
  - Intelligent price caching system (24-hour expiry)
  - Fuzzy matching for product identification
  - Confidence scoring for match quality

- **Dashboard Features**
  - Modern Streamlit-based web interface
  - Nitro Industrial branding (orange/black color scheme)
  - Side-by-side price comparison table
  - Fixed header row for easy scrolling
  - Real-time scraping with progress indicators
  - Summary metrics dashboard

- **Filtering & Search**
  - Full-text search across part numbers and descriptions
  - Price difference filters:
    - Competitors 10%+ cheaper
    - Competitors 20%+ cheaper
    - We're 10%+ cheaper
    - Equal pricing (±5%)
  - Sort by multiple attributes
  - Competitor selection/deselection

- **Data Visualization**
  - Color-coded price comparisons:
    - Green: We're cheaper
    - Red: Competitor is cheaper
    - Yellow: Equal pricing
    - Grey: No data available
  - Percentage difference calculations
  - Confidence badges (High/Medium/Low)
  - Data freshness indicators

- **Export Capabilities**
  - Excel export with formatting
  - Metadata sheet with timestamps
  - Automatic filename generation
  - Full data preservation

- **Cache Management**
  - Persistent JSON-based cache
  - Cache statistics display
  - Manual cache clearing
  - 24-hour automatic expiry

- **Error Handling**
  - Graceful failure handling
  - User-friendly error messages
  - Retry logic for network failures
  - Status indicators for each scrape

- **Build Tools**
  - PyInstaller build script
  - Launcher scripts for Windows/Linux/Mac
  - Sample CSV template
  - Comprehensive documentation

#### Technical Details
- Python 3.8+ support
- Streamlit 1.31.0 for UI
- BeautifulSoup4 for HTML parsing
- Selenium for JavaScript-heavy sites
- Pandas for data manipulation
- FuzzyWuzzy for string matching
- openpyxl for Excel export

#### Documentation
- Comprehensive README.md
- Quick Start Guide
- Configuration documentation
- Sample CSV template
- Build instructions

### Known Limitations
- Scraping subject to website structure changes
- Rate limiting may cause delays
- Some sites may block automated access
- Confidence scores are estimates
- Canadian sites only

### Future Considerations
- Scheduled automatic updates
- Email alerts for price changes
- Historical price tracking
- Additional competitors
- API integrations
- Manual override capabilities
- Bulk import/export of matches

---

## Version History

### Legend
- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security fixes

---

**For support or to report issues, please contact your system administrator.**
