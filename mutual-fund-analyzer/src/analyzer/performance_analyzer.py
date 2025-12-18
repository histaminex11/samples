"""
Performance Analyzer
Analyzes mutual fund performance metrics.
"""

import pandas as pd
import numpy as np
from typing import Dict, List


class PerformanceAnalyzer:
    """Analyzes mutual fund performance metrics."""
    
    def __init__(self):
        """Initialize the performance analyzer."""
        pass
    
    def calculate_returns(self, nav_data: pd.Series, periods: List[int] = [1, 3, 5, 10]) -> Dict[str, float]:
        """
        Calculate returns for different periods.
        
        Args:
            nav_data: Series of NAV values over time
            periods: List of periods in years
            
        Returns:
            Dictionary with returns for each period
        """
        returns = {}
        
        for period in periods:
            if len(nav_data) > period * 12:  # Assuming monthly data
                start_nav = nav_data.iloc[-(period * 12)]
                end_nav = nav_data.iloc[-1]
                returns[f'returns_{period}y'] = ((end_nav / start_nav) - 1) * 100
            else:
                returns[f'returns_{period}y'] = None
        
        return returns
    
    def calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 6.0) -> float:
        """
        Calculate Sharpe ratio.
        
        Args:
            returns: Series of returns
            risk_free_rate: Risk-free rate (default 6% for India)
            
        Returns:
            Sharpe ratio
        """
        if len(returns) == 0 or returns.std() == 0:
            return 0.0
        
        excess_returns = returns - (risk_free_rate / 12)  # Monthly risk-free rate
        sharpe = (excess_returns.mean() / returns.std()) * np.sqrt(12)  # Annualized
        return sharpe
    
    def calculate_sortino_ratio(self, returns: pd.Series, risk_free_rate: float = 6.0) -> float:
        """
        Calculate Sortino ratio (downside risk only).
        
        Args:
            returns: Series of returns
            risk_free_rate: Risk-free rate
            
        Returns:
            Sortino ratio
        """
        if len(returns) == 0:
            return 0.0
        
        excess_returns = returns - (risk_free_rate / 12)
        downside_returns = returns[returns < 0]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0
        
        sortino = (excess_returns.mean() / downside_returns.std()) * np.sqrt(12)
        return sortino
    
    def calculate_beta(self, fund_returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """
        Calculate beta (sensitivity to market movements).
        
        Args:
            fund_returns: Fund returns
            benchmark_returns: Benchmark returns (e.g., Nifty 50)
            
        Returns:
            Beta value
        """
        if len(fund_returns) != len(benchmark_returns) or len(fund_returns) == 0:
            return 1.0
        
        covariance = np.cov(fund_returns, benchmark_returns)[0][1]
        benchmark_variance = np.var(benchmark_returns)
        
        if benchmark_variance == 0:
            return 1.0
        
        beta = covariance / benchmark_variance
        return beta
    
    def calculate_max_drawdown(self, nav_data: pd.Series) -> float:
        """
        Calculate maximum drawdown.
        
        Args:
            nav_data: Series of NAV values
            
        Returns:
            Maximum drawdown percentage
        """
        if len(nav_data) == 0:
            return 0.0
        
        peak = nav_data.expanding().max()
        drawdown = (nav_data - peak) / peak * 100
        max_drawdown = drawdown.min()
        
        return abs(max_drawdown)
    
    def analyze_fund(self, fund_data: Dict) -> Dict:
        """
        Perform comprehensive analysis on a fund.
        
        Args:
            fund_data: Dictionary containing fund information
            
        Returns:
            Dictionary with analysis results
        """
        analysis = {
            'fund_name': fund_data.get('fund_name', ''),
            'category': fund_data.get('category', ''),
        }
        
        # Add performance metrics if available
        for metric in ['returns_1y', 'returns_3y', 'returns_5y', 'returns_10y']:
            if metric in fund_data:
                analysis[metric] = fund_data[metric]
        
        return analysis

