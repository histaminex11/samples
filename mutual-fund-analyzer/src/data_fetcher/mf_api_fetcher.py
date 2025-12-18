"""
MF API Fetcher
Fetches mutual fund data from api.mfapi.in API.
"""

import requests
import pandas as pd
import numpy as np
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import re


class MFAPIFetcher:
    """Fetches mutual fund data from api.mfapi.in."""
    
    BASE_URL = "https://api.mfapi.in/mf"
    
    # Category keywords for classification
    CATEGORY_KEYWORDS = {
        'smallcap': ['small cap', 'smallcap', 'small-cap'],
        'midcap': ['mid cap', 'midcap', 'mid-cap'],
        'largecap': ['large cap', 'largecap', 'large-cap'],
        'index_funds': ['index', 'nifty', 'sensex', 'etf', 'bse'],
        'elss': ['elss', 'tax saving', 'tax saver'],
        'hybrid': ['hybrid', 'balanced', 'equity savings', 'arbitrage'],
        'debt': ['debt', 'liquid', 'gilt', 'bond', 'income', 'overnight'],
        'sectoral': ['sector', 'banking', 'pharma', 'technology', 'infrastructure', 
                     'consumption', 'energy', 'healthcare', 'financial']
    }
    
    def __init__(self, rate_limit: float = 0.5):
        """
        Initialize the API fetcher.
        
        Args:
            rate_limit: Minimum seconds between API requests
        """
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _rate_limit_check(self):
        """Enforce rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last)
        
        self.last_request_time = time.time()
    
    def fetch_all_funds(self) -> pd.DataFrame:
        """
        Fetch all mutual funds from the API.
        
        Returns:
            DataFrame with all funds
        """
        print("Fetching all mutual funds from API...")
        self._rate_limit_check()
        
        try:
            response = self.session.get(self.BASE_URL, timeout=30)
            response.raise_for_status()
            funds_data = response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame(funds_data)
            
            # Filter out funds without schemeCode
            df = df[df['schemeCode'].notna()]
            
            print(f"✓ Fetched {len(df)} funds from API")
            return df
            
        except Exception as e:
            print(f"Error fetching funds: {str(e)}")
            return pd.DataFrame()
    
    def classify_fund_category(self, scheme_name: str) -> str:
        """
        Classify fund into category based on scheme name.
        
        Args:
            scheme_name: Name of the mutual fund scheme
            
        Returns:
            Category name
        """
        scheme_name_lower = scheme_name.lower()
        
        # Check each category
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(keyword in scheme_name_lower for keyword in keywords):
                return category
        
        # Default to 'other' if no match
        return 'other'
    
    def categorize_funds(self, funds_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Categorize funds into different categories.
        
        Args:
            funds_df: DataFrame with all funds
            
        Returns:
            Dictionary mapping categories to fund DataFrames
        """
        print("Categorizing funds...")
        
        categorized = {}
        
        for category in self.CATEGORY_KEYWORDS.keys():
            mask = funds_df['schemeName'].apply(
                lambda x: self.classify_fund_category(x) == category
            )
            category_funds = funds_df[mask].copy()
            category_funds['category'] = category
            
            # Filter to only Direct Plan funds (strict filtering)
            # Must contain "direct" and must NOT contain IDCW, Bonus, Periodic, Dividend
            direct_plan_funds = category_funds[
                category_funds['schemeName'].str.contains('direct', case=False, na=False) &
                ~category_funds['schemeName'].str.contains('idcw', case=False, na=False) &
                ~category_funds['schemeName'].str.contains('bonus', case=False, na=False) &
                ~category_funds['schemeName'].str.contains('periodic', case=False, na=False) &
                ~category_funds['schemeName'].str.contains('dividend', case=False, na=False)
            ]
            
            # Only include Direct Plan funds (no fallback to other options)
            if len(direct_plan_funds) > 0:
                categorized[category] = direct_plan_funds
            else:
                # Return empty DataFrame if no Direct Plan funds found
                categorized[category] = pd.DataFrame()
            
            print(f"  ✓ {category}: {len(categorized[category])} funds")
        
        return categorized
    
    def fetch_fund_history(self, scheme_code: int, days: int = 3650) -> Optional[pd.DataFrame]:
        """
        Fetch historical NAV data for a fund.
        
        Args:
            scheme_code: Scheme code of the fund
            days: Number of days of history to fetch (default 10 years)
            
        Returns:
            DataFrame with date and NAV, or None if error
        """
        self._rate_limit_check()
        
        try:
            url = f"{self.BASE_URL}/{scheme_code}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'SUCCESS' or 'data' not in data:
                return None
            
            nav_data = data['data']
            
            # Convert to DataFrame
            df = pd.DataFrame(nav_data)
            
            # Convert date and NAV
            df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
            df['nav'] = pd.to_numeric(df['nav'], errors='coerce')
            
            # Sort by date
            df = df.sort_values('date')
            
            # Limit to requested days
            if len(df) > 0:
                cutoff_date = df['date'].max() - timedelta(days=days)
                df = df[df['date'] >= cutoff_date]
            
            return df
            
        except Exception as e:
            print(f"Error fetching history for scheme {scheme_code}: {str(e)}")
            return None
    
    def calculate_returns(self, nav_df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate returns for different periods.
        
        Args:
            nav_df: DataFrame with date and nav columns
            
        Returns:
            Dictionary with returns for different periods
        """
        if nav_df is None or len(nav_df) == 0:
            return {
                'returns_1y': 0.0,
                'returns_3y': 0.0,
                'returns_5y': 0.0,
                'returns_10y': 0.0
            }
        
        returns = {}
        latest_date = nav_df['date'].max()
        latest_nav = nav_df[nav_df['date'] == latest_date]['nav'].iloc[0]
        
        # Calculate returns for different periods
        periods = {
            'returns_1y': 365,
            'returns_3y': 365 * 3,
            'returns_5y': 365 * 5,
            'returns_10y': 365 * 10
        }
        
        for period_name, days in periods.items():
            target_date = latest_date - timedelta(days=days)
            past_data = nav_df[nav_df['date'] <= target_date]
            
            if len(past_data) > 0:
                past_nav = past_data.iloc[-1]['nav']
                if past_nav > 0:
                    returns[period_name] = ((latest_nav / past_nav) - 1) * 100
                else:
                    returns[period_name] = 0.0
            else:
                returns[period_name] = 0.0
        
        return returns
    
    def calculate_risk_metrics(self, nav_df: pd.DataFrame, risk_free_rate: float = 6.0) -> Dict[str, float]:
        """
        Calculate risk metrics from NAV data.
        
        Args:
            nav_df: DataFrame with date and nav columns
            risk_free_rate: Risk-free rate (default 6% for India)
            
        Returns:
            Dictionary with risk metrics
        """
        if nav_df is None or len(nav_df) < 2:
            return {
                'sharpe_ratio': 0.0,
                'standard_deviation': 0.0,
                'max_drawdown': 0.0,
                'risk_score': 0.0
            }
        
        # Calculate monthly returns
        nav_df = nav_df.sort_values('date')
        nav_df['returns'] = nav_df['nav'].pct_change() * 100  # Percentage returns
        
        # Remove first row (NaN)
        returns_series = nav_df['returns'].dropna()
        
        if len(returns_series) < 2:
            return {
                'sharpe_ratio': 0.0,
                'standard_deviation': 0.0,
                'max_drawdown': 0.0,
                'risk_score': 0.0
            }
        
        # Calculate standard deviation (annualized)
        std_dev = returns_series.std() * np.sqrt(12)  # Annualized
        
        # Calculate Sharpe ratio
        if std_dev > 0:
            excess_returns = returns_series - (risk_free_rate / 12)
            sharpe = (excess_returns.mean() / std_dev) * np.sqrt(12)  # Annualized
        else:
            sharpe = 0.0
        
        # Calculate maximum drawdown
        nav_series = nav_df['nav']
        peak = nav_series.expanding().max()
        drawdown = (nav_series - peak) / peak * 100
        max_drawdown = abs(drawdown.min())
        
        # Calculate risk score (0-100, higher = riskier)
        # Based on standard deviation and max drawdown
        risk_score = min(100, (std_dev * 2) + (max_drawdown * 0.5))
        
        return {
            'sharpe_ratio': sharpe,
            'standard_deviation': std_dev,
            'max_drawdown': max_drawdown,
            'risk_score': risk_score
        }
    
    def enrich_funds_with_performance(self, funds_df: pd.DataFrame, max_funds: int = 100) -> pd.DataFrame:
        """
        Enrich funds DataFrame with performance data.
        
        Args:
            funds_df: DataFrame with fund information
            max_funds: Maximum number of funds to process
            
        Returns:
            Enriched DataFrame
        """
        print(f"Enriching {min(len(funds_df), max_funds)} funds with performance data...")
        
        enriched_data = []
        
        for idx, fund in funds_df.head(max_funds).iterrows():
            scheme_code = int(fund['schemeCode'])
            scheme_name = fund['schemeName']
            
            if (idx + 1) % 10 == 0:
                print(f"  Processed {idx+1}/{min(len(funds_df), max_funds)} funds...")
            
            # Fetch historical data
            nav_history = self.fetch_fund_history(scheme_code)
            
            # Calculate returns
            returns = self.calculate_returns(nav_history)
            
            # Calculate risk metrics
            risk_metrics = self.calculate_risk_metrics(nav_history)
            
            # Get current NAV
            current_nav = 0.0
            if nav_history is not None and len(nav_history) > 0:
                current_nav = nav_history.iloc[-1]['nav']
            
            # Create enriched fund data
            fund_data = {
                'scheme_code': scheme_code,
                'fund_name': scheme_name,
                'category': fund.get('category', 'other'),
                'nav': current_nav,
                'returns_1y': returns.get('returns_1y', 0.0),
                'returns_3y': returns.get('returns_3y', 0.0),
                'returns_5y': returns.get('returns_5y', 0.0),
                'returns_10y': returns.get('returns_10y', 0.0),
                'sharpe_ratio': risk_metrics.get('sharpe_ratio', 0.0),
                'standard_deviation': risk_metrics.get('standard_deviation', 0.0),
                'max_drawdown': risk_metrics.get('max_drawdown', 0.0),
                'risk_score': risk_metrics.get('risk_score', 0.0),
                'source': 'mfapi',
                'isin_growth': fund.get('isinGrowth', ''),
            }
            
            enriched_data.append(fund_data)
        
        return pd.DataFrame(enriched_data)
    
    def fetch_funds_by_category(self, category: str, all_funds_df: pd.DataFrame, max_funds: int = 100) -> pd.DataFrame:
        """
        Fetch funds for a specific category with performance data.
        
        Args:
            category: Fund category
            all_funds_df: DataFrame with all funds
            max_funds: Maximum number of funds to process
            
        Returns:
            DataFrame with fund data and performance metrics
        """
        print(f"Processing {category} funds...")
        
        # Filter funds for this category
        category_funds = all_funds_df[
            all_funds_df['schemeName'].apply(
                lambda x: self.classify_fund_category(x) == category
            )
        ].copy()
        
        # Filter to only Direct Plan funds (strict filtering)
        # Must contain "direct" and must NOT contain IDCW, Bonus, Periodic, Dividend
        direct_plan_funds = category_funds[
            category_funds['schemeName'].str.contains('direct', case=False, na=False) &
            ~category_funds['schemeName'].str.contains('idcw', case=False, na=False) &
            ~category_funds['schemeName'].str.contains('bonus', case=False, na=False) &
            ~category_funds['schemeName'].str.contains('periodic', case=False, na=False) &
            ~category_funds['schemeName'].str.contains('dividend', case=False, na=False)
        ]
        
        if len(direct_plan_funds) > 0:
            funds_to_process = direct_plan_funds.head(max_funds)
        else:
            # If no direct plan funds found, return empty (don't fall back to other options)
            funds_to_process = category_funds.head(0)  # Empty DataFrame
        
        # Enrich with performance data
        enriched_funds = self.enrich_funds_with_performance(funds_to_process, max_funds=max_funds)
        
        # Add category
        enriched_funds['category'] = category
        
        print(f"  ✓ Processed {len(enriched_funds)} {category} funds with performance data")
        return enriched_funds

