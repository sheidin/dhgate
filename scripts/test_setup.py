#!/usr/bin/env python3
"""
Test script to verify the DHGate scraper setup is working correctly
"""

def test_imports():
    """Test if all required modules can be imported"""
    try:
        import undetected_chromedriver as uc
        print("✅ undetected_chromedriver imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import undetected_chromedriver: {e}")
        return False
    
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        print("✅ Selenium modules imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import selenium modules: {e}")
        return False
    
    try:
        import requests
        print("✅ requests imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import requests: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import python-dotenv: {e}")
        return False
    
    return True

def test_dhgate_scraper():
    """Test if DHGateScraper can be instantiated and Chrome driver setup works"""
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from main import DHGateScraper
        scraper = DHGateScraper()
        print("✅ DHGateScraper instantiated successfully")
        print(f"   - Download directory: {scraper.download_dir}")
        print(f"   - User agent: {scraper.user_agent[:50]}...")
        
        # Test Chrome driver setup
        print("   - Testing Chrome driver setup...")
        if scraper.setup_driver():
            print("   ✅ Chrome driver setup successful")
            scraper.driver.quit()
            return True
        else:
            print("   ❌ Chrome driver setup failed")
            return False
            
    except Exception as e:
        print(f"❌ Failed to instantiate DHGateScraper: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing DHGate Scraper Setup")
    print("=" * 40)
    
    # Test imports
    print("\n📦 Testing imports...")
    imports_ok = test_imports()
    
    # Test DHGateScraper
    print("\n🔧 Testing DHGateScraper...")
    scraper_ok = test_dhgate_scraper()
    
    # Summary
    print("\n" + "=" * 40)
    if imports_ok and scraper_ok:
        print("🎉 All tests passed! The setup is working correctly.")
        print("\nNext steps:")
        print("1. Edit your .env file with your DHGate credentials")
        print("2. Run: python main.py")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
