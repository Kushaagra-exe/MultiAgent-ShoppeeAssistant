from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
import urllib.parse
import re
import time
import random
import json 
class ShoppingLinkScraper:
    def __init__(self):
        # Set up Chrome options
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")  # Run in headless mode
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920,1080")
        self.chrome_options.add_argument("--disable-notifications")
        self.chrome_options.add_argument("--disable-extensions")
        self.chrome_driver_path = r"C:\chromedriver\chromedriver-win64\chromedriver.exe" 
        self.service = Service(self.chrome_driver_path)

        # Set user agent
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
        self.chrome_options.add_argument(f"user-agent={self.user_agent}")
        
        # Initialize the driver as None initially
        self.driver = None
    
    async def initialize_driver(self):
        """Initialize the Chrome driver if not already initialized - async wrapper"""
        if self.driver is None:
            # Run the browser initialization in a thread pool
            self.driver = await asyncio.to_thread(
                webdriver.Chrome, 
                service=self.service, 
                options=self.chrome_options
            )
    
    async def close_driver(self):
        """Close the Chrome driver asynchronously"""
        if self.driver:
            await asyncio.to_thread(self.driver.quit)
            self.driver = None
    
    def clean_price(self, price_str):
        """Clean and convert price string to a float"""
        if not price_str:
            return 'Price not available'
        
        # Remove currency symbols, commas, and convert to float
        try:
            clean_price = re.sub(r'[^\d.]', '', price_str)
            return float(clean_price)
        except (ValueError, TypeError):
            return 'Price not available'
    
    async def wait_for_element(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """Wait for an element to be present asynchronously"""
        try:
            element = await asyncio.to_thread(
                lambda: WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, selector))
                )
            )
            return element
        except TimeoutException:
            return None
    
    async def wait_for_elements(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """Wait for elements to be present asynchronously"""
        try:
            elements = await asyncio.to_thread(
                lambda: WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_all_elements_located((by, selector))
                )
            )
            return elements
        except TimeoutException:
            return []
    
    async def scrape_google_shopping(self, query):
        """Scrape Google Shopping links using Selenium asynchronously"""
        await self.initialize_driver()
        
        base_url = 'https://www.google.com/search?q='
        encoded_query = urllib.parse.quote(query + " shopping")
        url = base_url + encoded_query + "&tbm=shop"
        
        try:
            # Navigate to URL using thread pool
            await asyncio.to_thread(self.driver.get, url)
            
            # Add a longer wait to ensure page is fully loaded
            await asyncio.sleep(3)
            
            # Try to find the products container first
            container = await self.wait_for_element('.sh-pr__product-results-grid')
            
            products = []
            if container:
                # Now find individual product elements within the container
                products = await asyncio.to_thread(
                    container.find_elements, By.CSS_SELECTOR, '.sh-pr__product-results'
                )
                
                if not products:
                    # Try alternative selectors for individual products
                    products = await asyncio.to_thread(
                        container.find_elements, By.CSS_SELECTOR, 'div[data-docid]'
                    )
            else:
                # If container not found, try finding products directly
                products = await self.wait_for_elements('.sh-pr__product-results')
                
                if not products:
                    products = await self.wait_for_elements('div[data-docid]')
            
            links = []
            
            # Process all found products up to 5
            for product in products[:5]:
                try:
                    # Look for title, properly handling potential missing elements
                    title_elem = None
                    for selector in ['.tAxDx', 'h3', '.sh-dgr__product-title', '.Xjkr3b']:
                        try:
                            title_elem = await asyncio.to_thread(
                                product.find_element, By.CSS_SELECTOR, selector
                            )
                            if title_elem and await asyncio.to_thread(
                                lambda: title_elem.text.strip()
                            ):
                                break
                        except Exception:
                            continue
                    
                    # Look for price
                    price_elem = None
                    for selector in ['.a8Pemb', '.kHxwFf span', '.QIrs8 span', '.kHxwFf', '.QIrs8']:
                        try:
                            price_elem = await asyncio.to_thread(
                                product.find_element, By.CSS_SELECTOR, selector
                            )
                            if price_elem and await asyncio.to_thread(
                                lambda: price_elem.text.strip()
                            ):
                                break
                        except Exception:
                            continue
                    
                    # Look for link
                    link_elem = None
                    for selector in ['a.shntl', 'a.iXEZD', 'a[href*="shopping"]', 'a']:
                        try:
                            link_elem = await asyncio.to_thread(
                                product.find_element, By.CSS_SELECTOR, selector
                            )
                            if link_elem and await asyncio.to_thread(
                                link_elem.get_attribute, 'href'
                            ):
                                break
                        except Exception:
                            continue
                    
                    if title_elem and link_elem:
                        title = await asyncio.to_thread(lambda: title_elem.text.strip())
                        link = await asyncio.to_thread(link_elem.get_attribute, 'href')
                        
                        price_text = ''
                        if price_elem:
                            price_text = await asyncio.to_thread(lambda: price_elem.text)
                        
                        price = self.clean_price(price_text)
                        
                        links.append({
                            'title': title,
                            'url': link,
                            'price': price,
                            'source': 'Google Shopping'
                        })
                
                except Exception as e:
                    pass
            
            return links
        
        except Exception as e:
            return []
        
        finally:
            # Don't close driver here - we'll close it in the main method
            pass
    
    async def async_get_shopping_links(self, query):
        """Aggregate shopping links from multiple sources asynchronously"""
        try:
            await self.initialize_driver()
            
            # Add a small delay to avoid overwhelming servers
            await asyncio.sleep(random.uniform(1, 3))
            
            google_links = await self.scrape_google_shopping(query)
            
            # Sort by price, handling 'Price not available'
            def price_sort_key(item):
                price = item['price']
                return float(price) if isinstance(price, (int, float)) else float('inf')
            
            google_links.sort(key=price_sort_key)
            
            return google_links
            
        finally:
            # Always close the driver when done
            await self.close_driver()

