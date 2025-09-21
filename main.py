#!/usr/bin/env python3
"""
DHGate Affiliate Orders Scraper

This script automates the login process to DHGate affiliate center,
extracts necessary authentication headers, and downloads order data.
"""

import os
import time
import json
import csv
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from urllib.parse import urljoin
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DHGateScraper:
    def __init__(self, username=None, password=None, download_dir=None):
        # Load environment variables
        load_dotenv()
        
        # Get credentials from environment variables or parameters
        self.username = username or os.getenv('DHGATE_USERNAME')
        self.password = password or os.getenv('DHGATE_PASSWORD')
        self.download_dir = download_dir or os.getenv('DOWNLOAD_DIR', './downloads')
        
        # Get optional configuration from environment
        self.user_agent = os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
        self.chrome_options = os.getenv('CHROME_OPTIONS', '').split(',') if os.getenv('CHROME_OPTIONS') else []
        self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', '30'))
        self.network_idle_timeout = int(os.getenv('NETWORK_IDLE_TIMEOUT', '30'))
        self.manual_auth_token = os.getenv('AUTH_TOKEN')
        
        # Set log level from environment
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        logging.getLogger().setLevel(getattr(logging, log_level, logging.INFO))
        
        self.driver = None
        self.session = requests.Session()
        self.headers_file = 'headers_cache.txt'  # Store in project root
        
        # Create download directory if it doesn't exist
        os.makedirs(self.download_dir, exist_ok=True)
        
        # Validate credentials
        if not self.username or not self.password:
            logger.warning("Username or password not provided. Please set DHGATE_USERNAME and DHGATE_PASSWORD in .env file or pass as parameters.")
    
    def wait_for_network_idle(self, timeout=None, idle_time=2):
        """Wait for network activity to settle by monitoring page load state"""
        try:
            if timeout is None:
                timeout = self.network_idle_timeout
                
            start_time = time.time()
            last_activity_time = start_time
            
            while time.time() - start_time < timeout:
                try:
                    # Check if page is still loading
                    ready_state = self.driver.execute_script("return document.readyState")
                    
                    if ready_state == "complete":
                        # Check if there are any pending network requests by looking at performance timing
                        performance_timing = self.driver.execute_script("""
                            return window.performance.timing.loadEventEnd - window.performance.timing.navigationStart;
                        """)
                        
                        # If load event has ended, check if we've been idle
                        current_time = time.time()
                        if current_time - last_activity_time >= idle_time:
                            logger.info("Network activity has settled")
                            return True
                    else:
                        # Page is still loading, reset idle timer
                        last_activity_time = time.time()
                    
                    # Small delay before next check
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.debug(f"Network monitoring check failed: {e}")
                    # If we can't check, assume it's settled after a short wait
                    time.sleep(1)
                    return True
            
            logger.info("Network activity timeout reached, proceeding anyway")
            return True
            
        except Exception as e:
            logger.debug(f"Network monitoring failed: {e}")
            # Fallback to a simple wait
            time.sleep(3)
            return True
    
    def load_cached_headers(self):
        """Load headers from cache file if it exists"""
        try:
            if os.path.exists(self.headers_file):
                with open(self.headers_file, 'r') as f:
                    headers_data = json.load(f)
                
                # Check if headers are recent (less than 24 hours old)
                if 'timestamp' in headers_data:
                    import datetime
                    cache_time = datetime.datetime.fromisoformat(headers_data['timestamp'])
                    current_time = datetime.datetime.now()
                    time_diff = current_time - cache_time
                    
                    if time_diff.total_seconds() < 24 * 60 * 60:  # 24 hours
                        logger.info("Found cached headers, checking if they're still valid...")
                        return headers_data.get('headers', {})
                    else:
                        logger.info("Cached headers are too old, will refresh")
                        return None
                else:
                    logger.info("Found cached headers without timestamp, will refresh")
                    return None
            else:
                logger.info("No cached headers found")
                return None
        except Exception as e:
            logger.debug(f"Error loading cached headers: {e}")
            return None
    
    def save_headers_to_cache(self, headers):
        """Save headers to cache file"""
        try:
            import datetime
            headers_data = {
                'timestamp': datetime.datetime.now().isoformat(),
                'headers': headers
            }
            
            with open(self.headers_file, 'w') as f:
                json.dump(headers_data, f, indent=2)
            
            logger.info(f"Headers saved to cache file: {self.headers_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving headers to cache: {e}")
            return False
    
    def test_headers_validity(self, headers):
        """Test if cached headers are still valid by making a test API call"""
        try:
            # Make a test request to check if headers are valid
            test_url = 'https://aff.dhgate.com/api/affiliate/order/exportOrders'
            test_data = {
                "beginDate": "2024-01-01",
                "endDate": "2024-01-02",
                "pageNum": 1,
                "veriStatus": "",
                "mediaId": "",
                "trackingSourceId": ""
            }
            
            response = requests.post(test_url, headers=headers, json=test_data, timeout=10)
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('success', False):
                    logger.info("✅ Cached headers are still valid")
                    return True
                elif 'Token invalid' in response_data.get('msg', ''):
                    logger.info("❌ Cached headers are invalid (token expired)")
                    return False
                else:
                    logger.info("✅ Cached headers are valid (API responded successfully)")
                    return True
            else:
                logger.info(f"❌ Cached headers test failed with status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.debug(f"Error testing headers validity: {e}")
            return False
        
    def setup_driver(self):
        """Initialize undetected Chrome driver"""
        try:
            options = uc.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-first-run')
            options.add_argument('--disable-default-apps')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            
            # Add custom Chrome options from environment
            for option in self.chrome_options:
                if option.strip():
                    options.add_argument(option.strip())
            
            self.driver = uc.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logger.info("Chrome driver initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            return False
    
    def login(self):
        """Login to DHGate affiliate center and extract authentication headers"""
        if not self.driver:
            if not self.setup_driver():
                return False
        
        try:
            # Navigate to the login page
            login_url = "https://aff.dhgate.com/affiliateCenter/affiliateOrders"
            logger.info(f"Navigating to: {login_url}")
            self.driver.get(login_url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Check if we need to login
            try:
                # Look for email input field
                email_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder*="Email"]'))
                )
                
                # Look for password input field
                password_input = self.driver.find_element(By.CSS_SELECTOR, 'input[placeholder*="password"]')
                
                logger.info("Login form detected, attempting to login...")
                
                # Enter credentials
                if self.username:
                    email_input.clear()
                    email_input.send_keys(self.username)
                    logger.info("Username entered")
                
                if self.password:
                    password_input.clear()
                    password_input.send_keys(self.password)
                    logger.info("Password entered")
                
                # Find and click login button - try multiple selectors
                login_button = None
                button_selectors = [
                    'button[type="submit"]',
                    'input[type="submit"]',
                    '.login-btn',
                    '.btn-login',
                    'button:contains("Login")',
                    'button:contains("Sign In")',
                    'input[value*="Login"]',
                    'input[value*="Sign"]',
                    'button',
                    'input[type="button"]'
                ]
                
                for selector in button_selectors:
                    try:
                        if ':contains(' in selector:
                            # Use XPath for text-based selectors
                            xpath = f"//button[contains(text(), '{selector.split(':contains(')[1].split(')')[0]}')]"
                            login_button = self.driver.find_element(By.XPATH, xpath)
                        else:
                            login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except:
                        continue
                
                if login_button:
                    login_button.click()
                    logger.info("Login button clicked")
                else:
                    # Debug: log available buttons on the page
                    try:
                        all_buttons = self.driver.find_elements(By.TAG_NAME, 'button')
                        all_inputs = self.driver.find_elements(By.TAG_NAME, 'input')
                        logger.info(f"Found {len(all_buttons)} buttons and {len(all_inputs)} inputs on the page")
                        for i, btn in enumerate(all_buttons[:5]):  # Log first 5 buttons
                            try:
                                btn_text = btn.text or btn.get_attribute('value') or btn.get_attribute('class')
                                logger.info(f"Button {i+1}: {btn_text}")
                            except:
                                pass
                    except Exception as e:
                        logger.info(f"Could not debug buttons: {e}")
                    
                    # Try pressing Enter on the password field
                    from selenium.webdriver.common.keys import Keys
                    password_input.send_keys(Keys.RETURN)
                    logger.info("Login attempted by pressing Enter")
                
                # Wait for login to complete
                logger.info("Waiting for login to complete...")
                time.sleep(5)  # Initial wait for login processing
                
                # Check if login was successful by looking for the orders page
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'body'))
                )
                
                # Wait for network activity to settle
                logger.info("Waiting for network activity to settle...")
                self.wait_for_network_idle()
                
                logger.info("Login successful, extracting authentication headers...")
                
            except TimeoutException:
                logger.info("No login form found, might already be logged in")
            
            # Wait for network activity to settle before extracting tokens
            logger.info("Waiting for network activity to settle before extracting tokens...")
            self.wait_for_network_idle()
            
            # Extract cookies and headers
            if self.extract_auth_headers():
                # Save headers to cache for future use
                self.save_headers_to_cache(self.headers)
                return True
            else:
                return False
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    def extract_auth_headers(self):
        """Extract authentication headers from the browser session"""
        try:
            # Get cookies
            cookies = self.driver.get_cookies()
            cookie_string = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
            
            # Get authorization header from network requests
            # We'll need to intercept network requests or extract from page
            auth_token = self.extract_auth_token()
            
            # Use manual token if provided
            if self.manual_auth_token:
                auth_token = self.manual_auth_token
                logger.info("Using manual auth token from .env file")
            
            if not auth_token or auth_token == "YOUR_AUTH_TOKEN_HERE":
                logger.warning("Could not extract authorization token")
                return False
            
            # Store headers for later use
            self.headers = {
                'Cookie': cookie_string,
                'User-Agent': self.user_agent,
                'Authorization': auth_token,
                'Content-Type': 'application/json'
            }
            
            logger.info("Authentication headers extracted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to extract auth headers: {e}")
            return False
    
    def extract_auth_token(self):
        """Extract authorization token from the page or network requests"""
        try:
            # Try to find the token in localStorage or sessionStorage
            token = self.driver.execute_script("""
                return localStorage.getItem('Authorization') ||
                       localStorage.getItem('auth_token') || 
                       sessionStorage.getItem('auth_token') ||
                       localStorage.getItem('token') ||
                       sessionStorage.getItem('token') ||
                       localStorage.getItem('authorization') ||
                       sessionStorage.getItem('authorization') ||
                       localStorage.getItem('access_token') ||
                       sessionStorage.getItem('access_token');
            """)
            
            if token:
                logger.info("Found token in browser storage")
                return token
            
            # Try to extract from page source or global variables
            token = self.driver.execute_script("""
                if (window.authToken) return window.authToken;
                if (window.token) return window.token;
                if (window.AUTH_TOKEN) return window.AUTH_TOKEN;
                if (window.authorization) return window.authorization;
                if (window.accessToken) return window.accessToken;
                return null;
            """)
            
            if token:
                logger.info("Found token in global variables")
                return token
            
            # Try to extract from meta tags
            try:
                meta_token = self.driver.find_element(By.CSS_SELECTOR, 'meta[name="csrf-token"], meta[name="token"], meta[name="authorization"]')
                token = meta_token.get_attribute('content')
                if token:
                    logger.info("Found token in meta tags")
                    return token
            except:
                pass
            
            # Try to extract from script tags that might contain the token
            try:
                scripts = self.driver.find_elements(By.TAG_NAME, 'script')
                for script in scripts:
                    script_content = script.get_attribute('innerHTML')
                    if script_content and ('token' in script_content.lower() or 'authorization' in script_content.lower()):
                        # Look for token patterns in the script
                        import re
                        patterns = [
                            r'token["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                            r'authorization["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                            r'authToken["\']?\s*[:=]\s*["\']([^"\']+)["\']'
                        ]
                        for pattern in patterns:
                            match = re.search(pattern, script_content, re.IGNORECASE)
                            if match:
                                token = match.group(1)
                                logger.info("Found token in script content")
                                return token
            except Exception as e:
                logger.debug(f"Error searching scripts: {e}")
            
            # Debug: Log what we found in the page
            try:
                logger.info("Debug: Checking page content for tokens...")
                
                # Check if there are any script tags with token-like content
                scripts = self.driver.find_elements(By.TAG_NAME, 'script')
                logger.info(f"Found {len(scripts)} script tags on the page")
                
                # Check localStorage and sessionStorage
                storage_info = self.driver.execute_script("""
                    return {
                        localStorage: Object.keys(localStorage),
                        sessionStorage: Object.keys(sessionStorage)
                    };
                """)
                logger.info(f"localStorage keys: {storage_info['localStorage']}")
                logger.info(f"sessionStorage keys: {storage_info['sessionStorage']}")
                
                # Check if there are any network requests we can intercept
                logger.info("Page URL after login: " + self.driver.current_url)
                
            except Exception as e:
                logger.debug(f"Debug info error: {e}")
            
            # If we can't find the token, we'll need to make a request and capture it
            # For now, return a placeholder that should be replaced
            logger.warning("Could not automatically extract auth token. You may need to manually provide it.")
            logger.info("To manually extract the token:")
            logger.info("1. Open browser developer tools (F12)")
            logger.info("2. Go to Network tab")
            logger.info("3. Look for requests to the API endpoint")
            logger.info("4. Copy the Authorization header value")
            logger.info("5. Set it in your .env file as AUTH_TOKEN=your_token_here")
            return "YOUR_AUTH_TOKEN_HERE"
            
        except Exception as e:
            logger.error(f"Failed to extract auth token: {e}")
            return None
    
    def fetch_orders(self):
        """Fetch order data using the extracted headers"""
        if not hasattr(self, 'headers'):
            logger.error("No authentication headers available. Please login first.")
            return False
        
        try:
            # Calculate date range (7 days ago to tomorrow)
            from datetime import datetime, timedelta
            end_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            begin_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            # Prepare request data
            url = 'https://aff.dhgate.com/api/affiliate/order/exportOrders'
            data = {
                "beginDate": begin_date,
                "endDate": end_date,
                "pageNum": 1,
                "veriStatus": "",
                "mediaId": "",
                "trackingSourceId": ""
            }
            
            logger.info(f"Fetching orders from {begin_date} to {end_date}")
            
            # Make the request
            response = requests.post(url, headers=self.headers, json=data, timeout=self.request_timeout)
            
            if response.status_code == 200:
                logger.info("Orders fetched successfully")
                return self.process_orders_response(response.text)
            else:
                logger.error(f"Failed to fetch orders. Status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            return False
    
    def process_orders_response(self, response_text):
        """Process the orders response and download files"""
        try:
            # Parse the response
            response_data = json.loads(response_text)
            
            if not response_data.get('success', False):
                error_msg = response_data.get('msg', 'Unknown error')
                if 'no data to export' in error_msg.lower():
                    logger.info("✅ No orders found for the specified date range. This is normal if you don't have any orders.")
                    logger.info("The script is working correctly - it successfully logged in and accessed the API.")
                    return True
                else:
                    logger.error(f"API returned error: {error_msg}")
                    return False
            
            # Extract CSV data
            csv_data = response_data.get('data', '')
            if not csv_data:
                logger.warning("No CSV data found in response")
                return False
            
            # Parse CSV
            csv_lines = csv_data.strip().split('\n')
            csv_reader = csv.reader(csv_lines)
            orders = list(csv_reader)
            
            # Sort orders (rsort equivalent in Python)
            orders.sort(reverse=True)
            
            logger.info(f"Processing {len(orders)} orders")
            
            # Process each order
            for row in orders:
                if len(row) >= 12:  # Ensure we have enough columns
                    order_id = row[0]
                    amount = row[2] if len(row) > 2 else "0"
                    subid = row[11] if len(row) > 11 else ""
                    
                    # Check if file already exists
                    file_path = os.path.join(self.download_dir, order_id)
                    if not os.path.exists(file_path):
                        try:
                            # Download the file
                            download_url = f"https://izeeto.com/conv?subid={subid}&tid={order_id}&amount={amount}"
                            logger.info(f"Downloading file for order {order_id}")
                            
                            response = requests.get(download_url, timeout=self.request_timeout)
                            if response.status_code == 200:
                                with open(file_path, 'wb') as f:
                                    f.write(response.content)
                                logger.info(f"File saved: {file_path}")
                            else:
                                logger.warning(f"Failed to download file for order {order_id}")
                                
                        except Exception as e:
                            logger.error(f"Error downloading file for order {order_id}: {e}")
                    else:
                        logger.info(f"File already exists for order {order_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing orders response: {e}")
            return False
    
    def run(self):
        """Main execution method"""
        try:
            logger.info("Starting DHGate scraper...")
            
            # Try to load cached headers first
            cached_headers = self.load_cached_headers()
            
            if cached_headers:
                # Test if cached headers are still valid
                if self.test_headers_validity(cached_headers):
                    logger.info("Using cached headers - no browser needed!")
                    self.headers = cached_headers
                else:
                    logger.info("Cached headers are invalid, will login with browser...")
                    # Login and extract headers
                    if not self.login():
                        logger.error("Login failed. Exiting.")
                        return False
            else:
                logger.info("No cached headers found, will login with browser...")
                # Login and extract headers
                if not self.login():
                    logger.error("Login failed. Exiting.")
                    return False
            
            # Fetch orders
            if not self.fetch_orders():
                logger.error("Failed to fetch orders. Exiting.")
                return False
            
            logger.info("Scraping completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("Browser closed")

def main():
    """Main function"""
    import argparse
    
    # Load environment variables first
    load_dotenv()
    
    parser = argparse.ArgumentParser(description='DHGate Affiliate Orders Scraper')
    parser.add_argument('--username', help='DHGate username/email (overrides .env)')
    parser.add_argument('--password', help='DHGate password (overrides .env)')
    parser.add_argument('--download-dir', help='Download directory (overrides .env)')
    parser.add_argument('--headless', action='store_true', help='Run Chrome in headless mode')
    parser.add_argument('--force-login', action='store_true', help='Force browser login and refresh cached headers')
    
    args = parser.parse_args()
    
    # Create scraper instance
    scraper = DHGateScraper(
        username=args.username,
        password=args.password,
        download_dir=args.download_dir
    )
    
    # Override Chrome options if headless mode is requested
    if args.headless:
        scraper.chrome_options.append('--headless')
    
    # Force login if requested
    if args.force_login:
        print("Force login requested, will refresh cached headers")
        # Remove cached headers file to force fresh login
        if os.path.exists(scraper.headers_file):
            os.remove(scraper.headers_file)
            print("Removed cached headers file")
    
    # Run the scraper
    success = scraper.run()
    
    if success:
        print("✅ Scraping completed successfully!")
        print(f"📁 Files saved to: {scraper.download_dir}")
    else:
        print("❌ Scraping failed. Check the logs for details.")
        exit(1)

if __name__ == "__main__":
    main()
