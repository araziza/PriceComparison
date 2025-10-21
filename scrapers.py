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

    def __init__(self, competitor_name: str, base_url: str, debug_mode: bool = False):
        self.competitor_name = competitor_name
        self.base_url = base_url
        self.debug_mode = debug_mode
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})

    def save_debug_html(self, html_content: str, part_number: str, reason: str = "debug"):
        """Save HTML content for debugging purposes"""
        if self.debug_mode:
            import os
            debug_dir = "debug_html"
            os.makedirs(debug_dir, exist_ok=True)

            # Sanitize filename
            safe_part = re.sub(r'[^\w\-]', '_', part_number)
            safe_reason = re.sub(r'[^\w\-]', '_', reason)
            filename = f"{debug_dir}/{self.competitor_name}_{safe_part}_{safe_reason}.html"

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)

            print(f"Debug HTML saved to: {filename}")

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
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service

        chrome_options = Options()
        chrome_options.add_argument('--headless=new')  # Use new headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument(f'user-agent={USER_AGENT}')
        chrome_options.add_argument('--window-size=1920,1080')

        # Use webdriver-manager to automatically handle ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
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
    """Scraper for Canadian Tire (canadiantire.ca) - Uses Selenium for JavaScript content"""

    def __init__(self):
        super().__init__("Canadian Tire", "https://www.canadiantire.ca")

    def search_product(self, part_number: str, part_description: str) -> Tuple[Optional[float], Optional[str], float, str]:
        """Search Canadian Tire for a product using Selenium"""
        driver = None
        try:
            search_term = f"{part_number} {part_description}".strip()
            search_url = f"{self.base_url}/en/search-results.html?q={requests.utils.quote(search_term)}"

            time.sleep(SCRAPE_DELAY)

            driver = self._get_selenium_driver()
            driver.get(search_url)

            # Wait for products to load
            wait = WebDriverWait(driver, 10)
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-tile, div[data-track-product], div.product-card")))
            except TimeoutException:
                return None, None, 0.0, "Search results did not load"

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Canadian Tire product tiles
            product = (
                soup.find('div', class_='product-tile') or
                soup.find('div', {'data-track-product': True}) or
                soup.find('div', class_='product-card')
            )

            if not product:
                return None, None, 0.0, "No products found"

            # Extract title
            title_elem = (
                product.find('div', class_='product-name') or
                product.find('span', class_='product__name') or
                product.find('h3', class_='product-name')
            )
            title = title_elem.text.strip() if title_elem else ""

            # Extract price
            price_elem = (
                product.find('span', class_='price__value') or
                product.find('span', class_='price') or
                product.find('div', class_='price')
            )
            if not price_elem:
                price_text = product.find(string=re.compile(r'\$\s*\d+'))
                if price_text:
                    price = self.extract_price(price_text)
                else:
                    return None, None, 0.0, "Price not found"
            else:
                price = self.extract_price(price_elem.text)

            # Extract URL
            link_elem = product.find('a', class_='product-link') or product.find('a', href=True)
            url = link_elem.get('href') if link_elem else None
            if url and not url.startswith('http'):
                url = self.base_url + url

            # Calculate confidence
            confidence = self.calculate_match_confidence(search_term, title) if title else 0.5

            return price, url, confidence, "Success"

        except TimeoutException:
            return None, None, 0.0, "Page load timeout"
        except Exception as e:
            return None, None, 0.0, f"Error: {str(e)}"
        finally:
            if driver:
                driver.quit()


class HomeDepotScraper(BaseScraper):
    """Scraper for Home Depot Canada (homedepot.ca) - Uses Selenium for JavaScript content"""

    def __init__(self):
        super().__init__("Home Depot", "https://www.homedepot.ca")

    def search_product(self, part_number: str, part_description: str) -> Tuple[Optional[float], Optional[str], float, str]:
        """Search Home Depot Canada for a product using Selenium"""
        driver = None
        try:
            # Home Depot loads content via JavaScript, so we need Selenium
            search_term = f"{part_number} {part_description}".strip()
            search_url = f"{self.base_url}/search?q={requests.utils.quote(search_term)}"

            time.sleep(SCRAPE_DELAY)

            # Use Selenium to load JavaScript content
            driver = self._get_selenium_driver()
            driver.get(search_url)

            # Wait for page to fully load - give it more time
            time.sleep(3)  # Give page time to load before checking

            # Try to wait for common elements, but don't fail if not found
            wait = WebDriverWait(driver, 15)  # Increased from 10 to 15 seconds

            try:
                # Try multiple possible selectors that might appear
                wait.until(EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    "div.product-pod, div[data-testid='product-pod'], div.product-card, div.plp-pod, div[class*='product'], article"
                )))
            except TimeoutException:
                # Timeout is OK - we'll still try to parse what loaded
                # Save HTML for debugging
                self.save_debug_html(driver.page_source, part_number, "timeout_waiting_for_products")
                pass

            # Parse the page with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Save full HTML for debugging if debug mode enabled
            if self.debug_mode:
                self.save_debug_html(driver.page_source, part_number, "full_page")

            # Find first product - try MANY different selectors
            product = (
                soup.find('div', class_='product-pod') or
                soup.find('div', {'data-testid': 'product-pod'}) or
                soup.find('div', class_='product-card') or
                soup.find('div', class_='plp-pod') or
                soup.find('article', class_=re.compile(r'product', re.I)) or
                soup.find('div', class_=re.compile(r'product-item', re.I)) or
                soup.find('div', class_=re.compile(r'product-tile', re.I))
            )

            if not product:
                # Save debug HTML to help troubleshoot
                self.save_debug_html(driver.page_source, part_number, "no_products_found")
                return None, None, 0.0, "No products found in search results"

            # Extract title - try multiple selectors
            title_elem = (
                product.find('span', class_='product-header__title') or
                product.find('span', class_='product-identifier') or
                product.find('h2', class_='sui-text-primary') or
                product.find('h3') or
                product.find('a', class_='sui-font-bold')
            )
            title = title_elem.text.strip() if title_elem else ""

            # Extract price - Home Depot uses various price selectors
            price_elem = (
                product.find('span', {'data-testid': 'price'}) or
                product.find('div', class_='sui-text-primary') or
                product.find('span', class_='price') or
                product.find('div', class_='price__value') or
                product.find('span', string=re.compile(r'\$\d+'))
            )

            if not price_elem:
                # Try to find any element with a dollar sign as last resort
                price_text = product.find(string=re.compile(r'\$\s*\d+'))
                if price_text:
                    price = self.extract_price(price_text)
                else:
                    # Save debug HTML to help troubleshoot
                    self.save_debug_html(driver.page_source, part_number, "price_not_found")
                    return None, None, 0.0, "Price element not found on page"
            else:
                price = self.extract_price(price_elem.text)

            if not price:
                return None, None, 0.0, "Could not parse price from element"

            # Extract URL
            link_elem = (
                product.find('a', class_='product-pod__link') or
                product.find('a', class_='sui-font-bold') or
                product.find('a', href=re.compile(r'/product/'))
            )
            url = link_elem.get('href') if link_elem else None
            if url and not url.startswith('http'):
                url = self.base_url + url

            # Calculate confidence
            confidence = self.calculate_match_confidence(search_term, title) if title else 0.5

            return price, url, confidence, "Success"

        except TimeoutException:
            return None, None, 0.0, "Page load timeout"
        except Exception as e:
            return None, None, 0.0, f"Error: {str(e)}"
        finally:
            if driver:
                driver.quit()


class LowesScraper(BaseScraper):
    """Scraper for Lowes Canada (lowes.ca) - Uses Selenium for JavaScript content"""

    def __init__(self):
        super().__init__("Lowes", "https://www.lowes.ca")

    def search_product(self, part_number: str, part_description: str) -> Tuple[Optional[float], Optional[str], float, str]:
        """Search Lowes Canada for a product using Selenium"""
        driver = None
        try:
            search_term = f"{part_number} {part_description}".strip()
            search_url = f"{self.base_url}/search?q={requests.utils.quote(search_term)}"

            time.sleep(SCRAPE_DELAY)

            driver = self._get_selenium_driver()
            driver.get(search_url)

            # Wait for products to load
            wait = WebDriverWait(driver, 10)
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-tile, article.product-card, div.product-pod")))
            except TimeoutException:
                return None, None, 0.0, "Search results did not load"

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Lowes product tiles
            product = (
                soup.find('div', class_='product-tile') or
                soup.find('article', class_='product-card') or
                soup.find('div', class_='product-pod')
            )

            if not product:
                return None, None, 0.0, "No products found"

            # Extract title
            title_elem = (
                product.find('h2', class_='product-title') or
                product.find('div', class_='product-name') or
                product.find('a', class_='product-title')
            )
            title = title_elem.text.strip() if title_elem else ""

            # Extract price
            price_elem = (
                product.find('span', class_='price-value') or
                product.find('div', class_='price') or
                product.find('span', class_='price')
            )
            if not price_elem:
                price_text = product.find(string=re.compile(r'\$\s*\d+'))
                if price_text:
                    price = self.extract_price(price_text)
                else:
                    return None, None, 0.0, "Price not found"
            else:
                price = self.extract_price(price_elem.text)

            # Extract URL
            link_elem = product.find('a', href=True)
            url = link_elem.get('href') if link_elem else None
            if url and not url.startswith('http'):
                url = self.base_url + url

            # Calculate confidence
            confidence = self.calculate_match_confidence(search_term, title) if title else 0.5

            return price, url, confidence, "Success"

        except TimeoutException:
            return None, None, 0.0, "Page load timeout"
        except Exception as e:
            return None, None, 0.0, f"Error: {str(e)}"
        finally:
            if driver:
                driver.quit()


class RonaScraper(BaseScraper):
    """Scraper for Rona (rona.ca) - Uses Selenium for JavaScript content"""

    def __init__(self):
        super().__init__("Rona", "https://www.rona.ca")

    def search_product(self, part_number: str, part_description: str) -> Tuple[Optional[float], Optional[str], float, str]:
        """Search Rona for a product using Selenium"""
        driver = None
        try:
            search_term = f"{part_number} {part_description}".strip()
            search_url = f"{self.base_url}/en/search?q={requests.utils.quote(search_term)}"

            time.sleep(SCRAPE_DELAY)

            driver = self._get_selenium_driver()
            driver.get(search_url)

            # Wait for page to load
            time.sleep(3)

            wait = WebDriverWait(driver, 15)
            try:
                wait.until(EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    "div.product-tile, div.product-card, div[class*='product'], article"
                )))
            except TimeoutException:
                self.save_debug_html(driver.page_source, part_number, "timeout_waiting_for_products")
                pass

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            if self.debug_mode:
                self.save_debug_html(driver.page_source, part_number, "full_page")

            # Rona product tiles - try multiple selectors
            product = (
                soup.find('div', class_='product-tile') or
                soup.find('div', class_='product-card') or
                soup.find('article', class_=re.compile(r'product', re.I)) or
                soup.find('div', class_=re.compile(r'product-item', re.I)) or
                soup.find('div', {'data-product': True})
            )

            if not product:
                self.save_debug_html(driver.page_source, part_number, "no_products_found")
                return None, None, 0.0, "No products found"

            # Extract title - Rona specific selectors
            title_elem = (
                product.find('div', class_='product-name') or
                product.find('h3') or
                product.find('h2', class_='product-title') or
                product.find('a', class_=re.compile(r'product.*title', re.I)) or
                product.find('span', class_=re.compile(r'product.*name', re.I))
            )
            title = title_elem.text.strip() if title_elem else ""

            # Extract price - Rona specific
            price_elem = (
                product.find('span', class_='price-value') or
                product.find('div', class_='price') or
                product.find('span', class_='price') or
                product.find('span', class_=re.compile(r'price', re.I)) or
                product.find('div', class_=re.compile(r'price', re.I))
            )

            if not price_elem:
                price_text = product.find(string=re.compile(r'\$\s*\d+'))
                if price_text:
                    price = self.extract_price(price_text)
                else:
                    self.save_debug_html(driver.page_source, part_number, "price_not_found")
                    return None, None, 0.0, "Price not found"
            else:
                price = self.extract_price(price_elem.text)

            if not price:
                self.save_debug_html(driver.page_source, part_number, "price_parse_failed")
                return None, None, 0.0, "Could not parse price"

            # Extract URL
            link_elem = product.find('a', href=True)
            url = link_elem.get('href') if link_elem else None
            if url and not url.startswith('http'):
                url = self.base_url + url

            # Calculate confidence
            confidence = self.calculate_match_confidence(search_term, title) if title else 0.5

            return price, url, confidence, "Success"

        except TimeoutException:
            return None, None, 0.0, "Page load timeout"
        except Exception as e:
            return None, None, 0.0, f"Error: {str(e)}"
        finally:
            if driver:
                driver.quit()


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
