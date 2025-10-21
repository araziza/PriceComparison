"""
Data handling module for CSV parsing and data management
"""

import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from config import CSV_COLUMNS, CACHE_FILE, CACHE_EXPIRY_HOURS


class DataHandler:
    """Handles CSV data loading and price data caching"""

    def __init__(self, csv_path: Optional[str] = None):
        self.csv_path = csv_path
        self.parts_data = None
        self.price_cache = self._load_cache()

    def load_csv(self, csv_path: Optional[str] = None) -> pd.DataFrame:
        """
        Load parts data from CSV file

        Args:
            csv_path: Path to the CSV file

        Returns:
            DataFrame with part_number, part_description, and nitro_price columns
        """
        if csv_path:
            self.csv_path = csv_path

        if not self.csv_path or not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")

        # Read CSV file with proper header detection
        df = pd.read_csv(self.csv_path, header=0)

        # Get column names (Excel columns L, M, Y)
        columns = df.columns.tolist()

        # Create new dataframe with renamed columns
        parts_df = pd.DataFrame({
            'part_number': df.iloc[:, CSV_COLUMNS['part_number']],
            'part_description': df.iloc[:, CSV_COLUMNS['part_description']],
            'nitro_price': df.iloc[:, CSV_COLUMNS['nitro_price']]
        })

        # Clean the data
        parts_df['part_number'] = parts_df['part_number'].astype(str).str.strip()
        parts_df['part_description'] = parts_df['part_description'].astype(str).str.strip()
        parts_df['nitro_price'] = pd.to_numeric(parts_df['nitro_price'], errors='coerce')

        # Remove rows with missing critical data
        parts_df = parts_df.dropna(subset=['part_number', 'nitro_price'])

        self.parts_data = parts_df
        return parts_df

    def _load_cache(self) -> Dict:
        """Load price cache from file"""
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading cache: {e}")
                return {}
        return {}

    def save_cache(self) -> None:
        """Save price cache to file"""
        try:
            with open(CACHE_FILE, 'w') as f:
                json.dump(self.price_cache, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")

    def get_cached_price(self, part_number: str, competitor: str) -> Optional[Dict]:
        """
        Get cached price for a part from a specific competitor

        Args:
            part_number: Part number to look up
            competitor: Competitor name

        Returns:
            Dictionary with price data or None if not cached or expired
        """
        cache_key = f"{part_number}_{competitor}"

        if cache_key in self.price_cache:
            cached_data = self.price_cache[cache_key]
            timestamp = datetime.fromisoformat(cached_data['timestamp'])

            # Check if cache is still valid
            if datetime.now() - timestamp < timedelta(hours=CACHE_EXPIRY_HOURS):
                return cached_data

        return None

    def cache_price(self, part_number: str, competitor: str, price: Optional[float],
                   url: Optional[str] = None, confidence: float = 0.0,
                   status: str = "success", error_message: str = "") -> None:
        """
        Cache price data for a part from a specific competitor

        Args:
            part_number: Part number
            competitor: Competitor name
            price: Price found (or None if not found)
            url: URL where price was found
            confidence: Confidence score for the match (0-1)
            status: Status of the scrape (success, not_found, error)
            error_message: Error message if status is error
        """
        cache_key = f"{part_number}_{competitor}"

        self.price_cache[cache_key] = {
            'part_number': part_number,
            'competitor': competitor,
            'price': price,
            'url': url,
            'confidence': confidence,
            'status': status,
            'error_message': error_message,
            'timestamp': datetime.now().isoformat()
        }

    def get_all_competitor_prices(self, part_number: str) -> Dict[str, Dict]:
        """
        Get all cached competitor prices for a part

        Args:
            part_number: Part number to look up

        Returns:
            Dictionary mapping competitor names to price data
        """
        from config import COMPETITORS

        result = {}
        for competitor in COMPETITORS.keys():
            cached = self.get_cached_price(part_number, competitor)
            if cached:
                result[competitor] = cached

        return result

    def clear_cache(self, competitor: Optional[str] = None) -> None:
        """
        Clear the price cache

        Args:
            competitor: If specified, only clear cache for this competitor
        """
        if competitor:
            # Clear only specific competitor's cache
            keys_to_remove = [k for k in self.price_cache.keys() if k.endswith(f"_{competitor}")]
            for key in keys_to_remove:
                del self.price_cache[key]
        else:
            # Clear all cache
            self.price_cache = {}

        self.save_cache()

    def get_cache_stats(self) -> Dict:
        """Get statistics about the cache"""
        from config import COMPETITORS

        stats = {
            'total_entries': len(self.price_cache),
            'by_competitor': {},
            'by_status': {'success': 0, 'not_found': 0, 'error': 0}
        }

        for competitor in COMPETITORS.keys():
            stats['by_competitor'][competitor] = 0

        for entry in self.price_cache.values():
            competitor = entry.get('competitor')
            status = entry.get('status', 'unknown')

            if competitor in stats['by_competitor']:
                stats['by_competitor'][competitor] += 1

            if status in stats['by_status']:
                stats['by_status'][status] += 1

        return stats
