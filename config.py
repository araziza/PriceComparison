"""
Configuration file for the Nitro Price Comparison Tool
"""

# Nitro Branding Colors
NITRO_ORANGE = "#FF6B35"
NITRO_BLACK = "#1A1A1A"
NITRO_GREY = "#757575"
NITRO_LIGHT_GREY = "#E0E0E0"
NITRO_WHITE = "#FFFFFF"

# Color coding for price comparisons
COLOR_CHEAPER = "#4CAF50"  # Green - we're cheaper
COLOR_MORE_EXPENSIVE = "#F44336"  # Red - we're more expensive
COLOR_EQUAL = "#FFC107"  # Yellow - equal pricing
COLOR_NO_DATA = "#9E9E9E"  # Grey - no data available

# Competitor websites (Canadian sites)
COMPETITORS = {
    "Princess Auto": "https://www.princessauto.com",
    "Canadian Tire": "https://www.canadiantire.ca",
    "Home Depot": "https://www.homedepot.ca",
    "Lowes": "https://www.lowes.ca",
    "Rona": "https://www.rona.ca"
}

# CSV column mappings (Excel columns are 1-indexed, Python is 0-indexed)
# Column L = index 11, Column M = index 12, Column Y = index 24
CSV_COLUMNS = {
    "part_number": 11,  # Column L
    "part_description": 12,  # Column M
    "nitro_price": 24  # Column Y
}

# Scraping settings
SCRAPE_TIMEOUT = 30  # seconds
SCRAPE_DELAY = 2  # seconds between requests to avoid rate limiting
MAX_RETRIES = 3
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Cache settings
CACHE_FILE = "price_cache.json"
CACHE_EXPIRY_HOURS = 24

# Matching confidence thresholds
CONFIDENCE_HIGH = 0.8
CONFIDENCE_MEDIUM = 0.6
CONFIDENCE_LOW = 0.4

# Excel export settings
EXPORT_FILENAME_PREFIX = "nitro_price_comparison_"
