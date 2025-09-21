# DHGate Affiliate Orders Scraper

This Python script automates the login process to DHGate affiliate center, extracts necessary authentication headers, and downloads order data.

## Features

- Automated login using undetected Chrome driver
- Automatic extraction of authentication cookies and headers
- Header caching to avoid repeated browser automation
- API request to fetch order data
- CSV processing and file downloading
- Local file storage with duplicate checking
- Environment variable support for secure credential management
- Virtual environment setup for isolated dependencies
- Cross-platform support (macOS, Windows, Linux)

## Requirements

- Python 3.7+ (Python 3.13+ supported with automatic compatibility fixes)
- Chrome browser installed
- Valid DHGate affiliate account credentials

## Quick Setup

### macOS

1. **Run the setup script:**
```bash
./setup_mac.sh
```

2. **Edit your credentials** in the `.env` file that was created:
```bash
nano .env
```

3. **Activate the virtual environment and run:**
```bash
./activate_mac.sh
python main.py
```

### Windows

1. **Run the setup script:**
```cmd
setup_windows.bat
```

2. **Edit your credentials** in the `.env` file that was created
3. **Activate the virtual environment and run:**
```cmd
activate_windows.bat
python main.py
```

### Linux

1. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Create .env file:**
```bash
cp config/env.template .env
# Edit .env with your credentials
```

4. **Run the scraper:**
```bash
python main.py
```

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# DHGate Login Credentials
DHGATE_USERNAME=your_email@example.com
DHGATE_PASSWORD=your_password

# Optional: Manual Auth Token (if automatic extraction fails)
# AUTH_TOKEN=your_manual_auth_token_here

# Download Configuration
DOWNLOAD_DIR=./downloads

# Optional: Custom User Agent
# USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36

# Optional: Custom Chrome options (comma-separated)
# CHROME_OPTIONS=--headless,--disable-images,--disable-plugins

# Optional: Request timeout in seconds
# REQUEST_TIMEOUT=30

# Optional: Network idle timeout in seconds
# NETWORK_IDLE_TIMEOUT=30

# Optional: Log level (DEBUG, INFO, WARNING, ERROR)
# LOG_LEVEL=INFO
```

## Usage

### Basic Usage

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the scraper
python main.py
```

### Command Line Options

```bash
python main.py --help
```

Available options:
- `--username`: Override username from .env
- `--password`: Override password from .env
- `--download-dir`: Override download directory
- `--headless`: Run Chrome in headless mode
- `--force-login`: Force browser login and refresh cached headers

### Examples

```bash
# Run with custom credentials
python main.py --username user@example.com --password mypassword

# Run in headless mode
python main.py --headless

# Force login (refresh cached headers)
python main.py --force-login

# Custom download directory
python main.py --download-dir /path/to/downloads
```

## How It Works

1. **Login Process**: The script uses undetected Chrome driver to log into DHGate affiliate center
2. **Header Extraction**: Extracts authentication cookies and headers from the browser session
3. **Header Caching**: Saves headers to `headers_cache.txt` for future use (24-hour expiration)
4. **API Request**: Makes a POST request to the DHGate API to fetch order data
5. **CSV Processing**: Processes the CSV response to extract order details
6. **File Download**: Downloads files from izeeto.com based on order details
7. **Local Storage**: Saves downloaded files locally with duplicate checking

## Troubleshooting

### Common Issues

1. **Chrome Driver Issues**:
   - Ensure Chrome browser is installed
   - The script automatically downloads the correct ChromeDriver version

2. **Login Failures**:
   - Check your credentials in the .env file
   - Try running with `--force-login` to refresh cached headers
   - Check if DHGate has changed their login process

3. **Token Extraction Issues**:
   - Use the manual token extraction script: `python scripts/extract_token.py`
   - Add the extracted token to your .env file as `AUTH_TOKEN`

4. **Network Issues**:
   - Check your internet connection
   - Increase timeout values in .env file
   - Try running without headless mode for debugging

### Debug Mode

Run with debug logging to see detailed information:

```bash
# Set debug level in .env
echo "LOG_LEVEL=DEBUG" >> .env

# Or run with debug output
python main.py --headless
```

## Project Structure

```
get_reports/
├── main.py               # Main scraper script
├── requirements.txt      # Python dependencies
├── setup_mac.sh          # macOS setup script
├── setup_windows.bat     # Windows setup script
├── activate_mac.sh       # macOS activation script
├── activate_windows.bat  # Windows activation script
├── .gitignore            # Git ignore file
├── .env                  # Your credentials (created after setup)
├── headers_cache.txt     # Cached authentication headers
├── venv/                 # Virtual environment (created after setup)
├── downloads/            # Downloaded files (created when running)
├── scripts/              # Utility scripts
│   ├── example_usage.py  # Example usage script
│   ├── test_setup.py     # Setup verification script
│   ├── extract_token.py  # Token extraction helper script
│   ├── setup_venv.sh     # Virtual environment setup script
│   └── activate_venv.sh  # Quick activation script
├── config/               # Configuration templates
│   └── env.template      # Environment variables template
└── docs/                 # Documentation
    └── README.md         # This documentation
```

## Scripts

### Setup Scripts

- **`setup_mac.sh`**: Complete setup for macOS
- **`setup_windows.bat`**: Complete setup for Windows
- **`activate_mac.sh`**: Quick activation for macOS
- **`activate_windows.bat`**: Quick activation for Windows

### Utility Scripts

- **`scripts/example_usage.py`**: Example of how to use the scraper programmatically
- **`scripts/test_setup.py`**: Verify that your setup is working correctly
- **`scripts/extract_token.py`**: Helper script to manually extract authentication tokens

## Security Notes

- Never commit your `.env` file to version control
- The script stores authentication headers locally in `headers_cache.txt`
- Headers expire after 24 hours for security
- Use environment variables for sensitive information

## License

This script is provided as-is for educational and automation purposes. Please ensure you comply with DHGate's terms of service when using this script.

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Run the test setup script: `python scripts/test_setup.py`
3. Check the logs for error messages
4. Ensure you have the latest version of Chrome browser