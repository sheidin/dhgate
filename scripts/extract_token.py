#!/usr/bin/env python3
"""
Helper script to extract the authorization token manually
This script will login and keep the browser open so you can extract the token
"""

import os
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    username = os.getenv('DHGATE_USERNAME')
    password = os.getenv('DHGATE_PASSWORD')
    
    if not username or not password:
        print("❌ Please set DHGATE_USERNAME and DHGATE_PASSWORD in your .env file")
        return
    
    print("🚀 Starting token extraction helper...")
    print("This will login and keep the browser open for you to extract the token")
    
    # Setup Chrome driver
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
    
    driver = uc.Chrome(options=options)
    
    try:
        # Navigate to login page
        print("📱 Navigating to DHGate affiliate center...")
        driver.get("https://aff.dhgate.com/affiliateCenter/affiliateOrders")
        time.sleep(3)
        
        # Login
        print("🔐 Attempting to login...")
        try:
            email_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder*="Email"]'))
            )
            password_input = driver.find_element(By.CSS_SELECTOR, 'input[placeholder*="password"]')
            
            email_input.clear()
            email_input.send_keys(username)
            password_input.clear()
            password_input.send_keys(password)
            
            # Try to find and click login button
            login_button = None
            button_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                '.login-btn',
                '.btn-login'
            ]
            
            for selector in button_selectors:
                try:
                    login_button = driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if login_button:
                login_button.click()
                print("✅ Login button clicked")
            else:
                from selenium.webdriver.common.keys import Keys
                password_input.send_keys(Keys.RETURN)
                print("✅ Login attempted by pressing Enter")
            
            time.sleep(5)  # Initial wait for login processing
            print("✅ Login completed!")
            
            # Wait for network activity to settle
            print("⏳ Waiting for network activity to settle...")
            time.sleep(3)  # Simple wait for network to settle
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return
        
        print("\n" + "="*60)
        print("🎯 TOKEN EXTRACTION INSTRUCTIONS:")
        print("="*60)
        print("1. Open browser developer tools (F12)")
        print("2. Go to the 'Network' tab")
        print("3. Look for requests to the API endpoint")
        print("4. Find the 'Authorization' header")
        print("5. Copy the token value (the long string after 'Authorization: ')")
        print("6. Add it to your .env file as: AUTH_TOKEN=your_token_here")
        print("7. Close this browser window when done")
        print("="*60)
        print("\n💡 The browser will stay open until you close it manually.")
        print("   You can now navigate around and make API calls to capture the token.")
        
        # Keep the browser open
        input("\nPress Enter to close the browser and exit...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()
        print("🔒 Browser closed")

if __name__ == "__main__":
    main()
