#!/bin/bash

# DHGate Scraper Virtual Environment Setup Script

echo "🚀 Setting up DHGate Scraper virtual environment..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7+ first."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

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
