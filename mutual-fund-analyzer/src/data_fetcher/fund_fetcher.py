"""
Fund Fetcher
Fetches mutual funds from various categories using MF API (api.mfapi.in).
"""

import pandas as pd
import time
from typing import List, Dict, Optional
import yaml
import os
from .mf_api_fetcher import MFAPIFetcher


class FundFetcher:
    """Fetches mutual fund data from MF API (api.mfapi.in)."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize the fund fetcher with configuration.
        Uses MF API (api.mfapi.in) for data fetching.
        
        Args:
            config_path: Path to config file
        """
        self.config = self._load_config(config_path)
        self.categories = self.config.get('categories', [])
        self.top_funds_count = self.config.get('analysis', {}).get('top_funds_per_category', 100)
        self.api_fetcher = MFAPIFetcher(rate_limit=0.5, config=self.config)
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Config file not found: {config_path}")
            return {}
    
    def fetch_funds_by_category(self, category: str, all_funds_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Fetch top mutual funds for a specific category using MF API.
        
        Args:
            category: Fund category (smallcap, midcap, largecap, etc.)
            all_funds_df: Optional pre-fetched all funds DataFrame
            
        Returns:
            DataFrame with fund information
        """
        # Use API-based fetching
        if all_funds_df is None:
            all_funds_df = self.api_fetcher.fetch_all_funds()
        
        if all_funds_df.empty:
            return pd.DataFrame()
        
        # Fetch funds for this category with performance data
        funds_df = self.api_fetcher.fetch_funds_by_category(
            category, 
            all_funds_df, 
            max_funds=self.top_funds_count
        )
        
        # Sort by returns
        if not funds_df.empty:
            if 'returns_5y' in funds_df.columns:
                funds_df = funds_df.sort_values('returns_5y', ascending=False, na_position='last')
            elif 'returns_3y' in funds_df.columns:
                funds_df = funds_df.sort_values('returns_3y', ascending=False, na_position='last')
            elif 'returns_1y' in funds_df.columns:
                funds_df = funds_df.sort_values('returns_1y', ascending=False, na_position='last')
            
            funds_df = funds_df.head(self.top_funds_count)
        
        return funds_df
    
    def fetch_all_categories(self) -> Dict[str, pd.DataFrame]:
        """
        Fetch funds for all configured categories.
        
        Returns:
            Dictionary mapping category names to DataFrames
        """
        all_funds = {}
        
        # Fetch all funds once, then process by category
        print("Fetching all mutual funds from API...")
        all_funds_df = self.api_fetcher.fetch_all_funds()
        
        if all_funds_df.empty:
            print("✗ Failed to fetch funds from API")
            return {cat: pd.DataFrame() for cat in self.categories}
        
        # Categorize funds first
        categorized_funds = self.api_fetcher.categorize_funds(all_funds_df)
        
        # Get unique categories found in the data
        available_categories = list(categorized_funds.keys())
        print(f"\nFound categories in data: {', '.join(available_categories)}")
        
        # Process each requested category
        for category in self.categories:
            try:
                if category in categorized_funds and not categorized_funds[category].empty:
                    # Get funds for this category and enrich with performance
                    category_funds = categorized_funds[category].head(self.top_funds_count)
                    funds_df = self.api_fetcher.enrich_funds_with_performance(
                        category_funds, 
                        max_funds=min(50, self.top_funds_count)  # Limit for speed
                    )
                    
                    # Sort by returns
                    if 'returns_5y' in funds_df.columns:
                        funds_df = funds_df.sort_values('returns_5y', ascending=False, na_position='last')
                    elif 'returns_3y' in funds_df.columns:
                        funds_df = funds_df.sort_values('returns_3y', ascending=False, na_position='last')
                    
                    all_funds[category] = funds_df
                    print(f"✓ Fetched {len(funds_df)} funds for {category}")
                else:
                    print(f"⚠ No funds found for {category}")
                    all_funds[category] = pd.DataFrame()
            except Exception as e:
                print(f"✗ Error fetching {category}: {str(e)}")
                all_funds[category] = pd.DataFrame()
        
        return all_funds
    
    def save_raw_data(self, funds_data: Dict[str, pd.DataFrame], output_dir: str = "data/raw"):
        """Save raw fetched data to CSV files."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save all funds combined
        all_funds_list = []
        for category, df in funds_data.items():
            if not df.empty:
                all_funds_list.append(df)
        
        if all_funds_list:
            all_funds_df = pd.concat(all_funds_list, ignore_index=True)
            all_funds_path = os.path.join(output_dir, "all_funds.csv")
            all_funds_df.to_csv(all_funds_path, index=False)
            print(f"Saved {len(all_funds_df)} total funds to {all_funds_path}")
        
        # Save by category
        category_dir = os.path.join(output_dir, "funds_by_category")
        os.makedirs(category_dir, exist_ok=True)
        
        for category, df in funds_data.items():
            if not df.empty:
                filepath = os.path.join(category_dir, f"{category}_funds.csv")
                df.to_csv(filepath, index=False)
                print(f"Saved {len(df)} {category} funds to {filepath}")

