#!/bin/bash

# Quick script to activate the virtual environment

if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
    echo "✅ Virtual environment activated!"
    echo ""
echo "To run the scraper:"
echo "  python main.py"
    echo ""
    echo "To deactivate:"
    echo "  deactivate"
else
    echo "❌ Virtual environment not found. Please run ./setup_venv.sh first."
    exit 1
fi
