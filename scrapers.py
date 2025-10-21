"""
Web scraping module for competitor price data
"""

import requests
import time
import re
from abc import ABC, abstractmethod
from typing import Optional, Dict, Tuple
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import SCRAPE_TIMEOUT, SCRAPE_DELAY, MAX_RETRIES, USER_AGENT, CONFIDENCE_HIGH, CONFIDENCE_MEDIUM


class BaseScraper(ABC):
    """Base class for all competitor scrapers"""

    def __init__(self, competitor_name: str, base_url: str):
        self.competitor_name = competitor_name
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})

    @abstractmethod
    def search_product(self, part_number: str, part_description: str) -> Tuple[Optional[float], Optional[str], float, str]:
        """
        Search for a product and return its price

        Args:
            part_number: Part number to search for
            part_description: Part description for matching

        Returns:
            Tuple of (price, url, confidence_score, status_message)
        """
        pass

    def calculate_match_confidence(self, search_term: str, found_title: str, found_description: str = "") -> float:
        """
        Calculate confidence score for a product match

        Args:
            search_term: Original search term
            found_title: Product title found
            found_description: Product description found

        Returns:
            Confidence score between 0 and 1
        """
        search_lower = search_term.lower()
        title_lower = found_title.lower()
        desc_lower = found_description.lower()

        # Calculate fuzzy match scores
        title_score = fuzz.token_sort_ratio(search_lower, title_lower) / 100
        desc_score = fuzz.token_sort_ratio(search_lower, desc_lower) / 100 if desc_lower else 0

        # Weighted average (title is more important)
        confidence = (title_score * 0.7) + (desc_score * 0.3)

        return confidence

    def extract_price(self, text: str) -> Optional[float]:
        """
        Extract price from text string

        Args:
            text: Text containing price

        Returns:
            Price as float or None if not found
        """
        # Remove extra whitespace and normalize
        text = ' '.join(text.split())

        # Pattern for Canadian prices: $X,XXX.XX or $XXX.XX
        patterns = [
            r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # $1,234.56 or $1234.56
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*\$',  # 1,234.56$ or 1234.56$
            r'(\d{1,3}(?:,\d{3})*\.\d{2})',  # 1,234.56 or 1234.56
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                price_str = match.group(1).replace(',', '')
                try:
                    return float(price_str)
                except ValueError:
                    continue

        return None

    def _get_selenium_driver(self) -> webdriver.Chrome:
        """Create and configure a Selenium Chrome driver"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument(f'user-agent={USER_AGENT}')

        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(SCRAPE_TIMEOUT)
        return driver


class PrincessAutoScraper(BaseScraper):
    """Scraper for Princess Auto (princessauto.com)"""

    def __init__(self):
        super().__init__("Princess Auto", "https://www.princessauto.com")

    def search_product(self, part_number: str, part_description: str) -> Tuple[Optional[float], Optional[str], float, str]:
        """Search Princess Auto for a product"""
        try:
            # Create search query
            search_term = f"{part_number} {part_description}".strip()
            search_url = f"{self.base_url}/en/search?text={requests.utils.quote(search_term)}"

            time.sleep(SCRAPE_DELAY)
            response = self.session.get(search_url, timeout=SCRAPE_TIMEOUT)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find first product in search results
            # Princess Auto uses various selectors, we'll try multiple
            product = soup.find('div', class_='product-tile') or soup.find('div', class_='product-item')

            if not product:
                return None, None, 0.0, "No products found"

            # Extract title
            title_elem = product.find('div', class_='product-name') or product.find('h3') or product.find('a', class_='name-link')
            title = title_elem.text.strip() if title_elem else ""

            # Extract price
            price_elem = product.find('span', class_='price-value') or product.find('span', class_='price')
            if not price_elem:
                return None, None, 0.0, "Price not found"

            price = self.extract_price(price_elem.text)

            # Extract URL
            link_elem = product.find('a', href=True)
            url = self.base_url + link_elem['href'] if link_elem and not link_elem['href'].startswith('http') else link_elem['href'] if link_elem else None

            # Calculate confidence
            confidence = self.calculate_match_confidence(search_term, title)

            return price, url, confidence, "Success"

        except requests.RequestException as e:
            return None, None, 0.0, f"Request error: {str(e)}"
        except Exception as e:
            return None, None, 0.0, f"Error: {str(e)}"


class CanadianTireScraper(BaseScraper):
    """Scraper for Canadian Tire (canadiantire.ca)"""

    def __init__(self):
        super().__init__("Canadian Tire", "https://www.canadiantire.ca")

    def search_product(self, part_number: str, part_description: str) -> Tuple[Optional[float], Optional[str], float, str]:
        """Search Canadian Tire for a product"""
        try:
            search_term = f"{part_number} {part_description}".strip()
            search_url = f"{self.base_url}/en/search-results.html?q={requests.utils.quote(search_term)}"

            time.sleep(SCRAPE_DELAY)
            response = self.session.get(search_url, timeout=SCRAPE_TIMEOUT)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Canadian Tire product tiles
            product = soup.find('div', class_='product-tile') or soup.find('div', {'data-track-product': True})

            if not product:
                return None, None, 0.0, "No products found"

            # Extract title
            title_elem = product.find('div', class_='product-name') or product.find('span', class_='product__name')
            title = title_elem.text.strip() if title_elem else ""

            # Extract price
            price_elem = product.find('span', class_='price__value') or product.find('span', class_='price')
            if not price_elem:
                return None, None, 0.0, "Price not found"

            price = self.extract_price(price_elem.text)

            # Extract URL
            link_elem = product.find('a', class_='product-link') or product.find('a', href=True)
            url = self.base_url + link_elem['href'] if link_elem and not link_elem['href'].startswith('http') else link_elem['href'] if link_elem else None

            # Calculate confidence
            confidence = self.calculate_match_confidence(search_term, title)

            return price, url, confidence, "Success"

        except requests.RequestException as e:
            return None, None, 0.0, f"Request error: {str(e)}"
        except Exception as e:
            return None, None, 0.0, f"Error: {str(e)}"


class HomeDepotScraper(BaseScraper):
    """Scraper for Home Depot Canada (homedepot.ca)"""

    def __init__(self):
        super().__init__("Home Depot", "https://www.homedepot.ca")

    def search_product(self, part_number: str, part_description: str) -> Tuple[Optional[float], Optional[str], float, str]:
        """Search Home Depot Canada for a product"""
        try:
            search_term = f"{part_number} {part_description}".strip()
            search_url = f"{self.base_url}/search?q={requests.utils.quote(search_term)}"

            time.sleep(SCRAPE_DELAY)
            response = self.session.get(search_url, timeout=SCRAPE_TIMEOUT)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Home Depot product tiles
            product = soup.find('div', class_='product-pod') or soup.find('div', {'data-testid': 'product-pod'})

            if not product:
                return None, None, 0.0, "No products found"

            # Extract title
            title_elem = product.find('span', class_='product-identifier') or product.find('h2')
            title = title_elem.text.strip() if title_elem else ""

            # Extract price
            price_elem = product.find('div', class_='price') or product.find('span', {'data-testid': 'price'})
            if not price_elem:
                return None, None, 0.0, "Price not found"

            price = self.extract_price(price_elem.text)

            # Extract URL
            link_elem = product.find('a', class_='product-link') or product.find('a', href=True)
            url = link_elem['href'] if link_elem else None
            if url and not url.startswith('http'):
                url = self.base_url + url

            # Calculate confidence
            confidence = self.calculate_match_confidence(search_term, title)

            return price, url, confidence, "Success"

        except requests.RequestException as e:
            return None, None, 0.0, f"Request error: {str(e)}"
        except Exception as e:
            return None, None, 0.0, f"Error: {str(e)}"


class LowesScraper(BaseScraper):
    """Scraper for Lowes Canada (lowes.ca)"""

    def __init__(self):
        super().__init__("Lowes", "https://www.lowes.ca")

    def search_product(self, part_number: str, part_description: str) -> Tuple[Optional[float], Optional[str], float, str]:
        """Search Lowes Canada for a product"""
        try:
            search_term = f"{part_number} {part_description}".strip()
            search_url = f"{self.base_url}/search?q={requests.utils.quote(search_term)}"

            time.sleep(SCRAPE_DELAY)
            response = self.session.get(search_url, timeout=SCRAPE_TIMEOUT)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Lowes product tiles
            product = soup.find('div', class_='product-tile') or soup.find('article', class_='product-card')

            if not product:
                return None, None, 0.0, "No products found"

            # Extract title
            title_elem = product.find('h2', class_='product-title') or product.find('div', class_='product-name')
            title = title_elem.text.strip() if title_elem else ""

            # Extract price
            price_elem = product.find('span', class_='price-value') or product.find('div', class_='price')
            if not price_elem:
                return None, None, 0.0, "Price not found"

            price = self.extract_price(price_elem.text)

            # Extract URL
            link_elem = product.find('a', href=True)
            url = link_elem['href'] if link_elem else None
            if url and not url.startswith('http'):
                url = self.base_url + url

            # Calculate confidence
            confidence = self.calculate_match_confidence(search_term, title)

            return price, url, confidence, "Success"

        except requests.RequestException as e:
            return None, None, 0.0, f"Request error: {str(e)}"
        except Exception as e:
            return None, None, 0.0, f"Error: {str(e)}"


class RonaScraper(BaseScraper):
    """Scraper for Rona (rona.ca)"""

    def __init__(self):
        super().__init__("Rona", "https://www.rona.ca")

    def search_product(self, part_number: str, part_description: str) -> Tuple[Optional[float], Optional[str], float, str]:
        """Search Rona for a product"""
        try:
            search_term = f"{part_number} {part_description}".strip()
            search_url = f"{self.base_url}/en/search?q={requests.utils.quote(search_term)}"

            time.sleep(SCRAPE_DELAY)
            response = self.session.get(search_url, timeout=SCRAPE_TIMEOUT)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Rona product tiles
            product = soup.find('div', class_='product-tile') or soup.find('div', class_='product-card')

            if not product:
                return None, None, 0.0, "No products found"

            # Extract title
            title_elem = product.find('div', class_='product-name') or product.find('h3')
            title = title_elem.text.strip() if title_elem else ""

            # Extract price
            price_elem = product.find('span', class_='price-value') or product.find('div', class_='price')
            if not price_elem:
                return None, None, 0.0, "Price not found"

            price = self.extract_price(price_elem.text)

            # Extract URL
            link_elem = product.find('a', href=True)
            url = link_elem['href'] if link_elem else None
            if url and not url.startswith('http'):
                url = self.base_url + url

            # Calculate confidence
            confidence = self.calculate_match_confidence(search_term, title)

            return price, url, confidence, "Success"

        except requests.RequestException as e:
            return None, None, 0.0, f"Request error: {str(e)}"
        except Exception as e:
            return None, None, 0.0, f"Error: {str(e)}"


class ScraperManager:
    """Manager class for all competitor scrapers"""

    def __init__(self):
        self.scrapers = {
            "Princess Auto": PrincessAutoScraper(),
            "Canadian Tire": CanadianTireScraper(),
            "Home Depot": HomeDepotScraper(),
            "Lowes": LowesScraper(),
            "Rona": RonaScraper()
        }

    def scrape_competitor(self, competitor: str, part_number: str, part_description: str) -> Dict:
        """
        Scrape a specific competitor for a product

        Args:
            competitor: Competitor name
            part_number: Part number
            part_description: Part description

        Returns:
            Dictionary with scrape results
        """
        if competitor not in self.scrapers:
            return {
                'price': None,
                'url': None,
                'confidence': 0.0,
                'status': 'error',
                'error_message': f"Unknown competitor: {competitor}"
            }

        scraper = self.scrapers[competitor]

        for attempt in range(MAX_RETRIES):
            try:
                price, url, confidence, status = scraper.search_product(part_number, part_description)

                return {
                    'price': price,
                    'url': url,
                    'confidence': confidence,
                    'status': 'success' if price is not None else 'not_found',
                    'error_message': '' if price is not None else status
                }

            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    return {
                        'price': None,
                        'url': None,
                        'confidence': 0.0,
                        'status': 'error',
                        'error_message': str(e)
                    }
                time.sleep(SCRAPE_DELAY * (attempt + 1))

    def scrape_all_competitors(self, part_number: str, part_description: str) -> Dict[str, Dict]:
        """
        Scrape all competitors for a product

        Args:
            part_number: Part number
            part_description: Part description

        Returns:
            Dictionary mapping competitor names to scrape results
        """
        results = {}

        for competitor in self.scrapers.keys():
            results[competitor] = self.scrape_competitor(competitor, part_number, part_description)

        return results
