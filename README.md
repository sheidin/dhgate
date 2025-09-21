# DHGate Affiliate Orders Scraper

This Python script automates the login process to DHGate affiliate center, extracts necessary authentication headers, and downloads order data.

## Quick Start

### macOS Setup

1. **Setup the environment:**
   ```bash
   ./setup_mac.sh
   ```

2. **Edit your credentials:**
   ```bash
   nano .env
   ```

3. **Activate virtual environment and run:**
   ```bash
   ./activate_mac.sh
   python main.py
   ```

### Windows Setup

1. **Setup the environment:**
   ```cmd
   setup_windows.bat
   ```

2. **Edit your credentials:**
   - Open `.env` file in any text editor
   - Add your DHGate username and password

3. **Activate virtual environment and run:**
   ```cmd
   activate_windows.bat
   python main.py
   ```

### Manual Setup (Any OS)

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
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

## Documentation

For detailed documentation, see [docs/README.md](docs/README.md)

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
    └── README.md         # Detailed documentation
```

## Features

- Automated login using undetected Chrome driver
- Header caching to avoid repeated browser automation
- Network activity monitoring for reliable token extraction
- Environment variable support for secure credential management
- Virtual environment setup for isolated dependencies
- Cross-platform support (macOS, Windows, Linux)
- Easy setup scripts for quick installation

## License

This script is provided as-is for educational and automation purposes. Please ensure you comply with DHGate's terms of service when using this script.