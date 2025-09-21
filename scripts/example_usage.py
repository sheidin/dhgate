#!/usr/bin/env python3
"""
Example usage of the DHGate scraper with environment variables
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import DHGateScraper

def main():
    # The scraper will automatically load credentials from .env file
    # Make sure you have created a .env file with your credentials
    
    # Create scraper instance (credentials loaded from .env)
    scraper = DHGateScraper()
    
    # Run the scraper
    print("🚀 Starting DHGate scraper...")
    print("📋 Loading credentials from .env file...")
    
    success = scraper.run()
    
    if success:
        print("✅ Scraping completed successfully!")
        print(f"📁 Files saved to: {scraper.download_dir}")
    else:
        print("❌ Scraping failed. Check the logs for details.")
        print("💡 Make sure your .env file contains valid credentials:")

if __name__ == "__main__":
    main()
