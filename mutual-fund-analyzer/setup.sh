#!/bin/bash

# Setup script for Mutual Fund Analyzer

echo "=========================================="
echo "Mutual Fund Analyzer - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Python 3 is required but not found. Please install Python 3.8+"; exit 1; }

# Create virtual environment (optional but recommended)
read -p "Create virtual environment? (y/n): " create_venv
if [ "$create_venv" = "y" ] || [ "$create_venv" = "Y" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✓ Virtual environment created and activated"
    echo "  To activate later: source venv/bin/activate"
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "✗ Error installing dependencies"
    echo "  Try: pip3 install --user -r requirements.txt"
    exit 1
fi

# Create data directories
echo ""
echo "Creating data directories..."
mkdir -p data/raw
mkdir -p data/processed
echo "✓ Data directories created"

# Test imports
echo ""
echo "Testing imports..."
python3 -c "import pandas; import requests; import yaml; from bs4 import BeautifulSoup; print('✓ All core dependencies available')" 2>/dev/null

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "Setup Complete!"
    echo "=========================================="
    echo ""
    echo "To run the analyzer:"
    echo "  python3 src/main.py --fetch"
    echo "  python3 src/main.py --all"
    echo ""
else
    echo ""
    echo "⚠ Some dependencies may be missing"
    echo "  Run: pip3 install -r requirements.txt"
fi

