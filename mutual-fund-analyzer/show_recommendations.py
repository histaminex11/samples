#!/usr/bin/env python3
"""
Display top N recommendations for each category (configurable via config.yaml).
"""

import pandas as pd
import sys
import os
import yaml
from pathlib import Path

def load_config():
    """Load configuration to get number of recommendations."""
    config_path = "config/config.yaml"
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            return config.get('analysis', {}).get('top_recommendations_per_category', 5)
    except:
        return 5  # Default

def show_recommendations():
    """Display top recommendations."""
    recommendations_file = "data/processed/recommendations.csv"
    
    if not os.path.exists(recommendations_file):
        print("Recommendations file not found. Run the analyzer first:")
        print("  python3 src/main.py --all")
        return
    
    df = pd.read_csv(recommendations_file)
    
    if df.empty:
        print("No recommendations found.")
        return
    
    # Get number of recommendations from config
    top_n = load_config()
    
    print("=" * 100)
    print(f"TOP {top_n} MUTUAL FUND RECOMMENDATIONS BY CATEGORY")
    print("=" * 100)
    print()
    
    categories = df['category'].unique()
    
    for category in sorted(categories):
        cat_df = df[df['category'] == category].head(top_n)
        
        if cat_df.empty:
            continue
        
        print(f"\n{'='*100}")
        print(f"CATEGORY: {category.upper()}")
        print(f"{'='*100}")
        print()
        
        for idx, (_, fund) in enumerate(cat_df.iterrows(), 1):
            print(f"Rank {fund['rank']}: {fund['fund_name']}")
            print(f"  Score: {fund['score']:.2f}")
            print(f"  Returns - 1Y: {fund.get('returns_1y', 0):.2f}% | 3Y: {fund.get('returns_3y', 0):.2f}% | 5Y: {fund.get('returns_5y', 0):.2f}%")
            if 'scheme_code' in fund:
                print(f"  Scheme Code: {fund['scheme_code']}")
            print()
    
    print("=" * 100)
    print(f"\nTotal recommendations: {len(df)}")
    print(f"Categories: {len(categories)}")
    print("\nFull data saved to: data/processed/recommendations.csv")

if __name__ == "__main__":
    show_recommendations()

