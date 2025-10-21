# Nitro Price Comparison Tool

A comprehensive, portable desktop application for comparing Nitro Industrial Supply part prices against major Canadian competitors.

![Nitro Industrial](https://nitroindustrial.com/logo.png)

## Features

### Core Functionality
- **Multi-Competitor Price Scraping**: Automatically scrapes prices from:
  - Princess Auto
  - Canadian Tire
  - Home Depot Canada
  - Lowes Canada
  - Rona

- **CSV Import**: Reads part data from CSV files (Columns L, M, Y)
  - Column L: Part Number
  - Column M: Part Description
  - Column Y: Nitro Price (CAD)

- **Intelligent Price Matching**: Uses fuzzy matching to find the best product matches across competitor websites

- **Real-time Comparison**: Side-by-side price comparison with visual indicators

### Dashboard Features

#### Main Comparison View
- Side-by-side comparison table with all competitors
- Fixed header row that stays visible while scrolling
- Color-coded price indicators:
  - 🟢 Green: We're cheaper than competitor
  - 🔴 Red: Competitor is cheaper than us
  - 🟡 Yellow: Equal pricing (±1%)
  - ⚫ Grey: No data available

#### Price Analysis
- Percentage difference calculations
- Summary metrics showing competitive position
- Filter by price difference thresholds
- Sort by multiple attributes

#### Smart Filtering & Search
- Search by part number or description
- Filter by price difference thresholds:
  - Competitors 10%+ cheaper
  - Competitors 20%+ cheaper
  - We're 10%+ cheaper
  - Equal pricing (±5%)
- Sort by various attributes

#### Data Quality Indicators
- Confidence scores for product matches (High/Medium/Low)
- Timestamps showing data freshness
- Clear error messages when scraping fails
- Cache management for faster performance

#### Export Capabilities
- Export to Excel with formatting
- Includes metadata sheet with timestamps
- Automatic filename with date/time
- Preserves all comparison data

### Design
- Modern, clean interface with Nitro branding
- Orange and black color scheme matching nitroindustrial.com
- Responsive layout optimized for desktop use
- Professional visual hierarchy

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Chrome/Chromium browser (for Selenium scraping)

### Quick Start

1. **Clone or download this repository**
   ```bash
   git clone https://github.com/yourusername/PriceComparison.git
   cd PriceComparison
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Open your browser**
   The application will automatically open at `http://localhost:8501`

## Usage

### Step 1: Upload Your CSV File
1. Click the "Upload Parts CSV" button in the sidebar
2. Select your CSV file containing part data
3. The application will automatically read columns L, M, and Y

### Step 2: Select Competitors
- Check/uncheck competitors in the sidebar to include/exclude them from comparisons
- By default, all competitors are selected

### Step 3: View Price Comparisons
- The main table shows all parts with competitor prices
- Use the search box to find specific parts
- Apply filters to see only parts meeting certain criteria

### Step 4: Scrape Prices
- Click "Force Update Prices" to scrape fresh data from competitor websites
- The application will cache results for 24 hours
- Watch the progress indicators as each competitor is scraped

### Step 5: Export Results
- Click "Export to Excel" to generate a formatted Excel file
- The export includes:
  - Full comparison data
  - Metadata sheet with timestamps
  - Formatted headers and columns

## CSV Format

Your input CSV must have the following columns:

| Column | Content | Example |
|--------|---------|---------|
| L (12th column) | Part Number | "ABC-123" |
| M (13th column) | Part Description | "1/4 inch drill bit" |
| Y (25th column) | Nitro Price (CAD) | 12.99 |

**Note**: Column letters refer to Excel column names. In code, these are accessed as indices 11, 12, and 24 respectively (0-indexed).

## Configuration

Edit `config.py` to customize:

- **Colors**: Adjust Nitro branding colors
- **Competitor URLs**: Update if websites change
- **Scraping settings**: Timeout, delays, retries
- **Cache expiry**: How long to keep cached prices (default: 24 hours)
- **Confidence thresholds**: Adjust matching sensitivity

## Creating a Portable Executable

To create a standalone executable that can run without Python:

### Windows

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Run the build script:
   ```bash
   python build_exe.py
   ```

3. Find the executable in the `dist` folder

### Linux/Mac

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Build the executable:
   ```bash
   pyinstaller --onefile --name NitroPriceComparison app.py
   ```

## Troubleshooting

### "No products found" errors
- Some websites may block automated scraping
- Try increasing the `SCRAPE_DELAY` in `config.py`
- Check if the competitor website structure has changed

### Slow performance
- Clear the cache using the "Clear All Cache" button
- Reduce the number of parts in your CSV
- Scrape one competitor at a time

### Excel export fails
- Ensure openpyxl is installed: `pip install openpyxl`
- Check that you have write permissions in the directory

### Chrome driver issues
- The application will automatically download the Chrome driver
- Ensure Chrome/Chromium is installed on your system
- Update to the latest version of Chrome

## Technical Details

### Architecture
- **Frontend**: Streamlit web framework
- **Scraping**: BeautifulSoup4 + Selenium
- **Data Processing**: Pandas
- **Export**: openpyxl
- **Matching**: FuzzyWuzzy string matching

### File Structure
```
PriceComparison/
├── app.py                 # Main Streamlit application
├── config.py             # Configuration settings
├── data_handler.py       # CSV parsing and cache management
├── scrapers.py           # Web scraping logic
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── price_cache.json     # Cache file (auto-generated)
```

### Cache Management
- Prices are cached for 24 hours by default
- Cache is stored in `price_cache.json`
- Each cache entry includes:
  - Price
  - URL
  - Confidence score
  - Timestamp
  - Status/error information

## Limitations

- Scraping is subject to website availability and structure changes
- Rate limiting may cause delays when scraping large datasets
- Some websites may block automated access
- Confidence scores are estimates based on text matching
- Canadian sites only (not compatible with US sites for these retailers)

## Future Enhancements

Potential features for future versions:
- Scheduled automatic updates
- Email alerts for significant price changes
- Historical price tracking
- Additional competitors
- API integrations (if available)
- Manual price override capability
- Bulk import/export of manual matches

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the configuration in `config.py`
3. Check application logs in the Streamlit interface
4. Ensure your CSV format matches the specification

## License

Copyright © 2024 Nitro Industrial Supply. All rights reserved.

---

**Version**: 1.0
**Last Updated**: 2024
**Built with**: Python, Streamlit, and open-source libraries
