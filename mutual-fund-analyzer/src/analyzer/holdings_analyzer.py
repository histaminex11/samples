"""
Holdings Analyzer
Analyzes current stock holdings in mutual funds.
"""

import pandas as pd
from typing import Dict, List
from collections import Counter


class HoldingsAnalyzer:
    """Analyzes mutual fund holdings and stock positions."""
    
    def __init__(self):
        """Initialize the holdings analyzer."""
        pass
    
    def get_top_holdings(self, holdings_data: List[Dict], top_n: int = 10) -> pd.DataFrame:
        """
        Get top N holdings from a fund.
        
        Args:
            holdings_data: List of holding dictionaries with 'stock_name' and 'weight'
            top_n: Number of top holdings to return
            
        Returns:
            DataFrame with top holdings
        """
        if not holdings_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(holdings_data)
        df_sorted = df.sort_values('weight', ascending=False).head(top_n)
        
        return df_sorted
    
    def analyze_holdings_composition(self, holdings_data: List[Dict]) -> Dict:
        """
        Analyze the composition of fund holdings.
        
        Args:
            holdings_data: List of holding dictionaries
            
        Returns:
            Dictionary with composition analysis
        """
        if not holdings_data:
            return {}
        
        df = pd.DataFrame(holdings_data)
        
        analysis = {
            'total_holdings': len(df),
            'top_10_weight': df.nlargest(10, 'weight')['weight'].sum() if len(df) >= 10 else df['weight'].sum(),
            'concentration_risk': self._calculate_concentration_risk(df),
        }
        
        if 'sector' in df.columns:
            analysis['sector_allocation'] = df.groupby('sector')['weight'].sum().to_dict()
        
        return analysis
    
    def _calculate_concentration_risk(self, holdings_df: pd.DataFrame) -> float:
        """
        Calculate concentration risk (Herfindahl-Hirschman Index).
        
        Args:
            holdings_df: DataFrame with holdings
            
        Returns:
            HHI score (higher = more concentrated)
        """
        if 'weight' not in holdings_df.columns or len(holdings_df) == 0:
            return 0.0
        
        weights = holdings_df['weight'] / 100  # Convert percentage to decimal
        hhi = (weights ** 2).sum() * 10000  # Scale to 0-10000
        
        return hhi
    
    def analyze_top_10_holdings(self, fund_holdings: Dict[str, List[Dict]]) -> pd.DataFrame:
        """
        Analyze top 10 holdings across multiple funds.
        
        Args:
            fund_holdings: Dictionary mapping fund names to their holdings
            
        Returns:
            DataFrame with aggregated top holdings analysis
        """
        all_top_holdings = []
        
        for fund_name, holdings in fund_holdings.items():
            top_10 = self.get_top_holdings(holdings, top_n=10)
            if not top_10.empty:
                top_10['fund_name'] = fund_name
                all_top_holdings.append(top_10)
        
        if not all_top_holdings:
            return pd.DataFrame()
        
        combined_df = pd.concat(all_top_holdings, ignore_index=True)
        return combined_df
    
    def find_common_holdings(self, funds_holdings: Dict[str, List[Dict]], min_funds: int = 2) -> List[str]:
        """
        Find stocks that are held by multiple funds.
        
        Args:
            funds_holdings: Dictionary mapping fund names to their holdings
            min_funds: Minimum number of funds that should hold a stock
            
        Returns:
            List of common stock names
        """
        stock_fund_count = Counter()
        
        for fund_name, holdings in funds_holdings.items():
            if holdings:
                stocks = [h.get('stock_name') for h in holdings if h.get('stock_name')]
                stock_fund_count.update(stocks)
        
        common_stocks = [
            stock for stock, count in stock_fund_count.items()
            if count >= min_funds
        ]
        
        return common_stocks

