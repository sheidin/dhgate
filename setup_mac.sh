#!/bin/bash

echo "🚀 Setting up DHGate Scraper on macOS..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first:"
    echo "   brew install python3"
    echo "   or download from https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created."
else
    echo "ℹ️  Virtual environment already exists."
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install setuptools first (fixes Python 3.13 compatibility)
echo "🔧 Installing setuptools for Python 3.13 compatibility..."
pip install --upgrade setuptools

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env template file..."
    cp config/env.template .env
    echo "✅ .env file created. Please edit it with your credentials."
else
    echo "ℹ️  .env file already exists."
fi

# Create downloads directory
if [ ! -d "downloads" ]; then
    echo "📁 Creating downloads directory..."
    mkdir -p downloads
    echo "✅ downloads directory created."
else
    echo "ℹ️  downloads directory already exists."
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the scraper:"
echo "  python main.py"
echo ""
echo "Don't forget to edit the .env file with your DHGate credentials!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your DHGate username and password"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python main.py"

