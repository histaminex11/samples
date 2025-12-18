"""
Consistency Analyzer
Analyzes fund performance consistency over time.
Uses existing NAV data to calculate consistency metrics.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from .base_analyzer import BaseAnalyzer


class ConsistencyAnalyzer(BaseAnalyzer):
    """Analyzes fund performance consistency."""
    
    def __init__(self, config: Dict = None):
        """Initialize the consistency analyzer."""
        super().__init__(config)
    
    def get_required_columns(self) -> list:
        """Get required columns for consistency analysis."""
        return ['nav', 'date']
    
    def analyze(self, fund_data: pd.DataFrame) -> pd.DataFrame:
        """
        Perform consistency analysis on fund data.
        Note: This requires NAV history which is already available.
        
        Args:
            fund_data: DataFrame with fund data
            
        Returns:
            DataFrame with consistency metrics added
        """
        if not self.validate_data(fund_data):
            return fund_data
        
        # Consistency metrics are calculated during data enrichment
        # This method can be extended for additional consistency analysis
        return fund_data
    
    def calculate_consistency_score(self, nav_data: pd.Series) -> float:
        """
        Calculate consistency score based on rolling returns.
        Higher score = more consistent performance.
        
        Args:
            nav_data: Series of NAV values over time
            
        Returns:
            Consistency score (0-100)
        """
        if nav_data is None or len(nav_data) < 12:
            return 0.0
        
        # Calculate monthly returns
        returns = nav_data.pct_change().dropna() * 100
        
        if len(returns) < 12:
            return 0.0
        
        # Calculate coefficient of variation (lower = more consistent)
        # Inverse relationship: lower CV = higher consistency score
        mean_return = returns.mean()
        std_return = returns.std()
        
        if mean_return == 0:
            return 0.0
        
        coefficient_of_variation = abs(std_return / mean_return) if mean_return != 0 else 100
        
        # Convert to score (0-100): lower CV = higher score
        # CV of 0.5 = very consistent, CV of 2.0+ = inconsistent
        consistency_score = max(0, 100 - (coefficient_of_variation * 50))
        
        return min(consistency_score, 100.0)
    
    def calculate_rolling_returns_consistency(self, nav_data: pd.Series, window_months: int = 12) -> float:
        """
        Calculate consistency of rolling returns.
        
        Args:
            nav_data: Series of NAV values
            window_months: Rolling window size in months
            
        Returns:
            Consistency score based on rolling returns variance
        """
        if nav_data is None or len(nav_data) < window_months * 2:
            return 0.0
        
        # Calculate monthly returns
        monthly_returns = nav_data.pct_change().dropna() * 100
        
        if len(monthly_returns) < window_months:
            return 0.0
        
        # Calculate rolling annualized returns
        rolling_returns = monthly_returns.rolling(window=window_months).apply(
            lambda x: ((1 + x/100).prod() - 1) * 100 * (12 / len(x)) if len(x) == window_months else np.nan
        ).dropna()
        
        if len(rolling_returns) < 2:
            return 0.0
        
        # Lower variance in rolling returns = higher consistency
        variance = rolling_returns.var()
        mean_return = abs(rolling_returns.mean())
        
        if mean_return == 0:
            return 0.0
        
        # Coefficient of variation of rolling returns
        cv = np.sqrt(variance) / mean_return if mean_return > 0 else 100
        
        # Convert to score: lower CV = higher consistency
        consistency_score = max(0, 100 - (cv * 30))
        
        return min(consistency_score, 100.0)
    
    def calculate_quartile_consistency(self, returns_series: pd.Series) -> float:
        """
        Calculate how consistently a fund ranks in top quartile.
        
        Args:
            returns_series: Series of period returns (e.g., monthly)
            
        Returns:
            Consistency score (0-100)
        """
        if returns_series is None or len(returns_series) < 12:
            return 0.0
        
        # For simplicity, use coefficient of variation as proxy
        # In full implementation, would compare against peer group
        mean_return = returns_series.mean()
        std_return = returns_series.std()
        
        if mean_return == 0:
            return 0.0
        
        cv = abs(std_return / mean_return) if mean_return != 0 else 100
        consistency_score = max(0, 100 - (cv * 50))
        
        return min(consistency_score, 100.0)
    
    def analyze_fund_consistency(self, nav_history: pd.DataFrame) -> Dict[str, float]:
        """
        Analyze consistency metrics for a fund.
        
        Args:
            nav_history: DataFrame with date and nav columns
            
        Returns:
            Dictionary with consistency metrics
        """
        if nav_history is None or nav_history.empty or 'nav' not in nav_history.columns:
            return {
                'consistency_score': 0.0,
                'rolling_consistency': 0.0,
                'coefficient_of_variation': 100.0
            }
        
        nav_series = nav_history.sort_values('date')['nav']
        
        # Calculate consistency score
        consistency_score = self.calculate_consistency_score(nav_series)
        rolling_consistency = self.calculate_rolling_returns_consistency(nav_series)
        
        # Calculate coefficient of variation
        returns = nav_series.pct_change().dropna() * 100
        if len(returns) > 0:
            mean_return = returns.mean()
            std_return = returns.std()
            cv = abs(std_return / mean_return) if mean_return != 0 else 100.0
        else:
            cv = 100.0
        
        return {
            'consistency_score': consistency_score,
            'rolling_consistency': rolling_consistency,
            'coefficient_of_variation': cv
        }

