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
        # Check if text is None
        if text is None:
            return None

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
            # Canadian Tire needs brand context - extract first word (usually brand name)
            brand = part_description.split()[0] if part_description else ""
            search_term = f"{part_number} {brand}".strip()
            search_url = f"{self.base_url}/en/search-results.html?q={requests.utils.quote(search_term)}"

            time.sleep(SCRAPE_DELAY)

            driver = self._get_selenium_driver()
            driver.get(search_url)

            # Give page extra time to load
            time.sleep(5)  # Canadian Tire needs more time

            # Try to wait for products with longer timeout
            wait = WebDriverWait(driver, 20)  # Increased from 10 to 20
            try:
                # Try multiple possible selectors
                wait.until(EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    "div.product-tile, div[data-track-product], div.product-card, article[class*='product'], div[class*='product-item']"
                )))
            except TimeoutException:
                # Don't fail immediately - still try to parse what loaded
                self.save_debug_html(driver.page_source, part_number, "timeout_waiting_for_products")
                pass

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            if self.debug_mode:
                self.save_debug_html(driver.page_source, part_number, "full_page")

            # Find ALL products - not just the first one
            products = (
                soup.find_all('div', class_='product-tile') or
                soup.find_all('div', {'data-track-product': True}) or
                soup.find_all('div', class_='product-card') or
                soup.find_all('article', class_=re.compile(r'product', re.I)) or
                soup.find_all('div', class_=re.compile(r'product-item', re.I)) or
                soup.find_all('div', class_=re.compile(r'nl-product', re.I)) or
                soup.find_all('div', {'data-product-id': True})
            )

            if not products:
                self.save_debug_html(driver.page_source, part_number, "no_products_found")
                return None, None, 0.0, "No products found"

            # Search through ALL products to find the one matching our part number
            best_match = None
            best_confidence = 0.0

            for product in products[:10]:  # Check first 10 products
                # Extract title - try multiple selectors
                title_elem = (
                    product.find('div', class_='product-name') or
                    product.find('span', class_='product__name') or
                    product.find('h3', class_='product-name') or
                    product.find('h2') or
                    product.find('a', class_=re.compile(r'product.*title', re.I)) or
                    product.find('span', class_=re.compile(r'product.*name', re.I))
                )
                title = title_elem.text.strip() if title_elem else ""

                # Check if this product contains our exact part number
                if part_number.upper() in title.upper() or part_number.upper() in str(product).upper():
                    confidence = self.calculate_match_confidence(search_term, title)
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = product

            # If no exact match found, fall back to first product with low confidence
            if not best_match:
                best_match = products[0]
                best_confidence = 0.3

            product = best_match

            # Extract title from best match
            title_elem = (
                product.find('div', class_='product-name') or
                product.find('span', class_='product__name') or
                product.find('h3', class_='product-name') or
                product.find('h2') or
                product.find('a', class_=re.compile(r'product.*title', re.I)) or
                product.find('span', class_=re.compile(r'product.*name', re.I))
            )
            title = title_elem.text.strip() if title_elem else ""

            # Extract price - Canadian Tire specific
            price_elem = (
                product.find('span', class_='price__value') or
                product.find('span', class_='price') or
                product.find('div', class_='price') or
                product.find('span', class_=re.compile(r'price', re.I)) or
                product.find('div', class_=re.compile(r'price', re.I))
            )

            if not price_elem:
                # Try to find any price in the product
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
            # Search with just the part number for better accuracy
            search_term = part_number.strip()
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

            # Find ALL products - not just the first one
            products = (
                soup.find_all('div', class_='product-pod') or
                soup.find_all('div', {'data-testid': 'product-pod'}) or
                soup.find_all('div', class_='product-card') or
                soup.find_all('div', class_='plp-pod') or
                soup.find_all('article', class_=re.compile(r'product', re.I)) or
                soup.find_all('div', class_=re.compile(r'product-item', re.I)) or
                soup.find_all('div', class_=re.compile(r'product-tile', re.I))
            )

            if not products:
                # Save debug HTML to help troubleshoot
                self.save_debug_html(driver.page_source, part_number, "no_products_found")
                return None, None, 0.0, "No products found in search results"

            # Search through ALL products to find the one matching our part number
            best_match = None
            best_confidence = 0.0

            for product in products[:10]:  # Check first 10 products
                # Extract title
                title_elem = (
                    product.find('span', class_='product-header__title') or
                    product.find('span', class_='product-identifier') or
                    product.find('h2', class_='sui-text-primary') or
                    product.find('h3') or
                    product.find('a', class_='sui-font-bold')
                )
                title = title_elem.text.strip() if title_elem else ""

                # Check if this product contains our exact part number
                if part_number.upper() in title.upper() or part_number.upper() in str(product).upper():
                    # Calculate confidence for this match
                    confidence = self.calculate_match_confidence(search_term, title)

                    # Keep track of best match
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = product

            # If no exact match found, fall back to first product with low confidence
            if not best_match:
                best_match = products[0]
                best_confidence = 0.3  # Low confidence for non-exact match

            product = best_match

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

            # Use the best confidence from our search
            final_confidence = best_confidence if best_confidence > 0 else 0.3

            return price, url, final_confidence, "Success"

        except TimeoutException:
            return None, None, 0.0, "Page load timeout"
        except Exception as e:
            return None, None, 0.0, f"Error: {str(e)}"
        finally:
            if driver:
                driver.quit()


class LowesScraper(BaseScraper):
    """Scraper for Lowes US (lowes.com) - Uses Selenium for JavaScript content"""

    def __init__(self, debug_mode: bool = False):
        super().__init__("Lowes", "https://www.lowes.com", debug_mode=debug_mode)

    def search_product(self, part_number: str, part_description: str) -> Tuple[Optional[float], Optional[str], float, str]:
        """Search Lowes US for a product using Selenium with exact part number matching"""
        driver = None
        try:
            search_term = f"{part_number} {part_description}".strip()
            search_url = f"{self.base_url}/search?searchTerm={requests.utils.quote(search_term)}"

            time.sleep(SCRAPE_DELAY)

            driver = self._get_selenium_driver()
            driver.get(search_url)

            # Give page time to load
            time.sleep(3)

            # Wait for products to load with longer timeout
            wait = WebDriverWait(driver, 15)
            try:
                wait.until(EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    "div.product-card, div[data-selector='productCard'], div.sc-product, article.product"
                )))
            except TimeoutException:
                self.save_debug_html(driver.page_source, part_number, "timeout_waiting_for_products")
                pass  # Continue anyway, might still parse something

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            self.save_debug_html(driver.page_source, part_number, "full_page")

            # Find ALL products - not just the first one
            products = (
                soup.find_all('div', class_='product-card') or
                soup.find_all('div', {'data-selector': 'productCard'}) or
                soup.find_all('div', class_='sc-product') or
                soup.find_all('article', class_='product') or
                soup.find_all('div', class_=re.compile(r'.*product.*card.*', re.I))
            )

            if not products:
                self.save_debug_html(driver.page_source, part_number, "no_products_found")
                return None, None, 0.0, "No products found in search results"

            # Search through ALL products to find the one matching our part number
            best_match = None
            best_confidence = 0.0

            for product in products[:10]:  # Check first 10 products
                # Extract title
                title_elem = (
                    product.find('h2', class_='product-title') or
                    product.find('div', class_='product-name') or
                    product.find('a', class_='product-title') or
                    product.find('span', {'data-selector': 'productTitle'}) or
                    product.find('h3') or
                    product.find('a', class_=re.compile(r'.*title.*', re.I))
                )
                title = title_elem.text.strip() if title_elem else ""

                # Check if this product contains our exact part number
                if part_number.upper() in title.upper() or part_number.upper() in str(product).upper():
                    confidence = self.calculate_match_confidence(search_term, title)
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = product

            # If no exact match found, fall back to first product with low confidence
            if not best_match:
                best_match = products[0]
                best_confidence = 0.3

            product = best_match

            # Extract title from best match
            title_elem = (
                product.find('h2', class_='product-title') or
                product.find('div', class_='product-name') or
                product.find('a', class_='product-title') or
                product.find('span', {'data-selector': 'productTitle'}) or
                product.find('h3') or
                product.find('a', class_=re.compile(r'.*title.*', re.I))
            )
            title = title_elem.text.strip() if title_elem else ""

            # Extract price
            price_elem = (
                product.find('span', class_='price-value') or
                product.find('span', {'data-selector': 'priceValue'}) or
                product.find('div', class_='price') or
                product.find('span', class_='price') or
                product.find('span', {'aria-label': re.compile(r'.*price.*', re.I)})
            )

            if not price_elem:
                price_text = product.find(string=re.compile(r'\$\s*\d+'))
                if price_text:
                    price = self.parse_price(price_text)
                else:
                    return None, None, 0.0, "Price not found"
            else:
                price = self.parse_price(price_elem.text)

            # Extract URL
            link_elem = product.find('a', href=True)
            url = link_elem.get('href') if link_elem else None
            if url and not url.startswith('http'):
                url = self.base_url + url

            return price, url, best_confidence, "Success"

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

            # Find ALL products - not just the first one
            products = (
                soup.find_all('div', class_='product-tile') or
                soup.find_all('div', class_='product-card') or
                soup.find_all('article', class_=re.compile(r'product', re.I)) or
                soup.find_all('div', class_=re.compile(r'product-item', re.I)) or
                soup.find_all('div', {'data-product': True})
            )

            if not products:
                self.save_debug_html(driver.page_source, part_number, "no_products_found")
                return None, None, 0.0, "No products found"

            # Search through ALL products to find the one matching our part number
            best_match = None
            best_confidence = 0.0

            for product in products[:10]:  # Check first 10 products
                # Extract title
                title_elem = (
                    product.find('div', class_='product-name') or
                    product.find('h3') or
                    product.find('h2', class_='product-title') or
                    product.find('a', class_=re.compile(r'product.*title', re.I)) or
                    product.find('span', class_=re.compile(r'product.*name', re.I))
                )
                title = title_elem.text.strip() if title_elem else ""

                # Check if this product contains our exact part number
                if part_number.upper() in title.upper() or part_number.upper() in str(product).upper():
                    # Calculate confidence for this match
                    confidence = self.calculate_match_confidence(search_term, title)

                    # Keep track of best match
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = product

            # If no exact match found, fall back to first product
            if not best_match:
                best_match = products[0]
                best_confidence = 0.3  # Low confidence for non-exact match

            product = best_match

            # Extract title from best match
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

            return price, url, best_confidence, "Success"

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
            # "Princess Auto": PrincessAutoScraper(),  # Disabled - unreliable scraping
            "Canadian Tire": CanadianTireScraper(),
            "Home Depot": HomeDepotScraper(),
            # "Lowes": LowesScraper(),  # Disabled - bot protection (Access Denied)
            # "Rona": RonaScraper()  # Disabled - unreliable scraping (Cloudflare issues)
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
