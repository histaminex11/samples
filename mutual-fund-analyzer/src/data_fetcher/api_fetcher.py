"""
API Fetcher
Fetches mutual fund data from mfapi.in API.
"""

import requests
import pandas as pd
import time
from typing import Dict, List, Optional
import json


class APIFetcher:
    """Fetches mutual fund data from mfapi.in API."""
    
    BASE_URL = "https://api.mfapi.in/mf"
    
    # Category keywords for classification
    CATEGORY_KEYWORDS = {
        'smallcap': ['small cap', 'smallcap', 'small-cap'],
        'midcap': ['mid cap', 'midcap', 'mid-cap'],
        'largecap': ['large cap', 'largecap', 'large-cap'],
        'index_funds': ['index', 'nifty', 'sensex', 'etf', 'bse', 'nse'],
        'elss': ['elss', 'tax', 'tax saving', 'tax-saving'],
        'hybrid': ['hybrid', 'balanced', 'aggressive', 'conservative', 'equity hybrid', 'debt hybrid'],
        'debt': ['debt', 'income', 'gilt', 'liquid', 'money market', 'corporate bond', 'government'],
        'sectoral': ['sector', 'infrastructure', 'banking', 'pharma', 'technology', 'healthcare', 'consumption', 'f&o']
    }
    
    def __init__(self, rate_limit: float = 0.5):
        """
        Initialize API fetcher.
        
        Args:
            rate_limit: Minimum seconds between requests
        """
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
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
            
            # Classify funds into categories
            df['category'] = df['schemeName'].apply(self._classify_fund)
            
            print(f"✓ Fetched {len(df)} funds from API")
            return df
            
        except Exception as e:
            print(f"Error fetching funds from API: {str(e)}")
            return pd.DataFrame()
    
    def _classify_fund(self, scheme_name: str) -> str:
        """
        Classify a fund into a category based on its name.
        
        Args:
            scheme_name: Name of the scheme
            
        Returns:
            Category name
        """
        if not scheme_name:
            return 'other'
        
        scheme_lower = scheme_name.lower()
        
        # Check each category
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(keyword in scheme_lower for keyword in keywords):
                return category
        
        # Default to 'other' if no match
        return 'other'
    
    def fetch_fund_history(self, scheme_code: int, days: int = 365) -> Optional[Dict]:
        """
        Fetch historical NAV data for a fund.
        
        Args:
            scheme_code: Scheme code from the API
            days: Number of days of history to fetch
            
        Returns:
            Dictionary with historical data or None
        """
        self._rate_limit_check()
        
        url = f"{self.BASE_URL}/{scheme_code}"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data and len(data['data']) > 0:
                # Get recent data (last N days)
                recent_data = data['data'][-days:] if len(data['data']) > days else data['data']
                
                # Extract NAV values
                nav_values = [float(item.get('nav', 0)) for item in recent_data if item.get('nav')]
                
                if nav_values:
                    return {
                        'scheme_code': scheme_code,
                        'nav_data': nav_values,
                        'current_nav': nav_values[-1],
                        'data_points': len(nav_values)
                    }
            
            return None
            
        except Exception as e:
            print(f"Error fetching history for scheme {scheme_code}: {str(e)}")
            return None
    
    def calculate_returns(self, nav_data: List[float], periods: List[int] = [365, 1095, 1825]) -> Dict[str, float]:
        """
        Calculate returns for different periods from NAV data.
        
        Args:
            nav_data: List of NAV values (most recent last)
            periods: List of periods in days (365=1Y, 1095=3Y, 1825=5Y)
            
        Returns:
            Dictionary with returns for each period
        """
        returns = {}
        
        if not nav_data or len(nav_data) < 30:
            return {f'returns_{p//365}y': 0.0 for p in periods}
        
        current_nav = nav_data[-1]
        
        for period_days in periods:
            period_years = period_days // 365
            if len(nav_data) >= period_days:
                past_nav = nav_data[-period_days]
                if past_nav > 0:
                    return_pct = ((current_nav / past_nav) - 1) * 100
                    returns[f'returns_{period_years}y'] = return_pct
                else:
                    returns[f'returns_{period_years}y'] = 0.0
            else:
                returns[f'returns_{period_years}y'] = 0.0
        
        return returns
    
    def fetch_funds_by_category(self, category: str, all_funds_df: pd.DataFrame, max_funds: int = 100) -> pd.DataFrame:
        """
        Get funds for a specific category and fetch their performance data.
        
        Args:
            category: Fund category
            all_funds_df: DataFrame with all funds
            max_funds: Maximum number of funds to process
            
        Returns:
            DataFrame with fund data including returns
        """
        print(f"\nProcessing {category} funds...")
        
        # Filter funds by category
        category_funds = all_funds_df[all_funds_df['category'] == category].copy()
        
        if category_funds.empty:
            print(f"  No funds found for category: {category}")
            return pd.DataFrame()
        
        # Limit to max_funds
        category_funds = category_funds.head(max_funds)
        
        funds_data = []
        
        for idx, fund in category_funds.iterrows():
            scheme_code = fund.get('schemeCode')
            scheme_name = fund.get('schemeName', '')
            
            if not scheme_code:
                continue
            
            # Fetch historical data
            history = self.fetch_fund_history(scheme_code, days=1825)  # 5 years
            
            if history:
                # Calculate returns
                returns = self.calculate_returns(history['nav_data'])
                
                fund_data = {
                    'scheme_code': scheme_code,
                    'fund_name': scheme_name,
                    'category': category,
                    'nav': history['current_nav'],
                    'returns_1y': returns.get('returns_1y', 0.0),
                    'returns_3y': returns.get('returns_3y', 0.0),
                    'returns_5y': returns.get('returns_5y', 0.0),
                    'data_points': history['data_points'],
                    'source': 'mfapi.in'
                }
                
                funds_data.append(fund_data)
            
            # Progress indicator
            if len(funds_data) % 10 == 0:
                print(f"  Processed {len(funds_data)}/{len(category_funds)} funds...")
        
        print(f"  ✓ Processed {len(funds_data)} {category} funds with performance data")
        
        return pd.DataFrame(funds_data)

