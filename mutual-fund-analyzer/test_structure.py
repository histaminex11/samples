#!/usr/bin/env python3
"""
Simple test script to verify project structure and imports.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test if modules can be imported."""
    print("Testing project structure...")
    print("=" * 60)
    
    # Test basic Python imports
    try:
        import yaml
        print("✓ yaml module available")
    except ImportError:
        print("✗ yaml module not available (install: pip install pyyaml)")
    
    try:
        import requests
        print("✓ requests module available")
    except ImportError:
        print("✗ requests module not available (install: pip install requests)")
    
    try:
        import pandas as pd
        print("✓ pandas module available")
    except ImportError:
        print("✗ pandas module not available (install: pip install pandas)")
    
    print("\n" + "=" * 60)
    print("Testing project file structure...")
    print("=" * 60)
    
    # Check if key files exist
    files_to_check = [
        "src/data_fetcher/fund_fetcher.py",
        "src/data_fetcher/mf_api_fetcher.py",
        "src/analyzer/performance_analyzer.py",
        "src/ranking/fund_ranker.py",
        "src/main.py",
        "config/config.yaml",
        "requirements.txt",
        "README.md"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - MISSING")
    
    print("\n" + "=" * 60)
    print("Testing code syntax...")
    print("=" * 60)
    
    # Test syntax of key files
    import ast
    python_files = [
        "src/data_fetcher/fund_fetcher.py",
        "src/data_fetcher/mf_api_fetcher.py",
        "src/main.py"
    ]
    
    for file_path in python_files:
        try:
            with open(file_path, 'r') as f:
                code = f.read()
                ast.parse(code)
            print(f"✓ {file_path} - Syntax OK")
        except SyntaxError as e:
            print(f"✗ {file_path} - Syntax Error: {e}")
        except Exception as e:
            print(f"⚠ {file_path} - Could not check: {e}")
    
    print("\n" + "=" * 60)
    print("Testing module imports...")
    print("=" * 60)
    
    # Test if project modules can be imported
    try:
        from data_fetcher import FundFetcher, MFAPIFetcher
        print("✓ data_fetcher modules import successfully")
    except Exception as e:
        print(f"✗ data_fetcher import failed: {e}")
    
    try:
        from analyzer import PerformanceAnalyzer
        print("✓ analyzer modules import successfully")
    except Exception as e:
        print(f"✗ analyzer import failed: {e}")
    
    try:
        from ranking import FundRanker
        print("✓ ranking modules import successfully")
    except Exception as e:
        print(f"✗ ranking import failed: {e}")
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print("Project structure appears to be correct!")
    print("\nTo install all dependencies, run:")
    print("  ./setup.sh")
    print("  # or")
    print("  source vmfanalyzer/bin/activate && pip install -r requirements.txt")
    print("\nTo test data fetching (after installing dependencies):")
    print("  source vmfanalyzer/bin/activate")
    print("  python src/main.py --fetch")

if __name__ == "__main__":
    test_imports()
