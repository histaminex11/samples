"""
Benchmark Analyzer
Analyzes fund performance against its benchmark.
Calculates alpha, tracking error, and benchmark comparison metrics.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
import requests
import time
from datetime import datetime, timedelta
from .base_analyzer import BaseAnalyzer


class BenchmarkAnalyzer(BaseAnalyzer):
    """Analyzes fund performance against benchmarks."""
    
    # Common benchmark indices and their identifiers
    BENCHMARK_MAPPING = {
        'nifty 50': 'NIFTY 50',
        'nifty': 'NIFTY 50',
        'sensex': 'S&P BSE SENSEX',
        'bse sensex': 'S&P BSE SENSEX',
        'nifty 100': 'NIFTY 100',
        'nifty midcap': 'NIFTY Midcap 100',
        'nifty smallcap': 'NIFTY Smallcap 100',
        'nifty next 50': 'NIFTY Next 50',
    }
    
    def __init__(self, config: Dict = None):
        """Initialize the benchmark analyzer."""
        super().__init__(config)
        self.risk_free_rate = self.config.get('risk_free_rate', 6.0)
        self.benchmark_cache = {}  # Cache for benchmark data
    
    def get_required_columns(self) -> list:
        """Get required columns for benchmark analysis."""
        return ['nav', 'date']
    
    def analyze(self, fund_data: pd.DataFrame) -> pd.DataFrame:
        """
        Perform benchmark analysis on fund data.
        
        Args:
            fund_data: DataFrame with fund data
            
        Returns:
            DataFrame with benchmark metrics added
        """
        if not self.validate_data(fund_data):
            return fund_data
        
        # Benchmark analysis requires benchmark data which needs to be fetched
        # This method can be extended for batch analysis
        return fund_data
    
    def identify_benchmark(self, fund_name: str, category: str) -> Optional[str]:
        """
        Identify benchmark for a fund based on name and category.
        
        Args:
            fund_name: Name of the fund
            category: Fund category
            
        Returns:
            Benchmark name or None
        """
        fund_name_lower = fund_name.lower()
        
        # Check fund name for benchmark indicators
        for keyword, benchmark in self.BENCHMARK_MAPPING.items():
            if keyword in fund_name_lower:
                return benchmark
        
        # Category-based default benchmarks
        category_benchmarks = {
            'largecap': 'NIFTY 50',
            'midcap': 'NIFTY Midcap 100',
            'smallcap': 'NIFTY Smallcap 100',
            'index_funds': 'NIFTY 50',  # Default, but index funds have specific benchmarks
            'elss': 'NIFTY 500',
            'hybrid': 'NIFTY 50 Hybrid Composite Debt 50:50',
            'debt': 'CRISIL Composite Bond Fund Index',
            'sectoral': 'NIFTY 500',
        }
        
        return category_benchmarks.get(category, 'NIFTY 50')
    
    def fetch_benchmark_data(self, benchmark_name: str, days: int = 3650) -> Optional[pd.DataFrame]:
        """
        Fetch benchmark index data.
        Note: This is a placeholder - actual implementation would fetch from index data provider.
        
        Args:
            benchmark_name: Name of the benchmark index
            days: Number of days of historical data
            
        Returns:
            DataFrame with date and index value, or None if not available
        """
        # For now, return None as we don't have a direct API for index data
        # In production, this would fetch from NSE/BSE APIs or financial data providers
        # This can be implemented later when index data source is available
        
        # Placeholder: Would fetch from index API
        # For now, we'll calculate relative metrics without benchmark data
        return None
    
    def calculate_alpha(self, fund_returns: pd.Series, benchmark_returns: pd.Series, 
                       risk_free_rate: float = None) -> float:
        """
        Calculate alpha (excess return over benchmark).
        
        Args:
            fund_returns: Fund returns series
            benchmark_returns: Benchmark returns series
            risk_free_rate: Risk-free rate (defaults to config)
            
        Returns:
            Alpha value (annualized percentage)
        """
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
        
        if len(fund_returns) != len(benchmark_returns) or len(fund_returns) < 2:
            return 0.0
        
        # Calculate excess returns
        fund_excess = fund_returns - (risk_free_rate / 12)  # Monthly risk-free rate
        benchmark_excess = benchmark_returns - (risk_free_rate / 12)
        
        # Alpha = Fund excess return - (Beta * Benchmark excess return)
        # For simplicity, if beta not available, use: Alpha = Fund return - Benchmark return
        alpha_monthly = fund_excess.mean() - benchmark_excess.mean()
        alpha_annualized = alpha_monthly * 12
        
        return alpha_annualized
    
    def calculate_tracking_error(self, fund_returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """
        Calculate tracking error (standard deviation of difference).
        
        Args:
            fund_returns: Fund returns series
            benchmark_returns: Benchmark returns series
            
        Returns:
            Tracking error (annualized percentage)
        """
        if len(fund_returns) != len(benchmark_returns) or len(fund_returns) < 2:
            return 0.0
        
        # Calculate difference between fund and benchmark returns
        difference = fund_returns - benchmark_returns
        
        # Tracking error = standard deviation of difference (annualized)
        tracking_error = difference.std() * np.sqrt(12)
        
        return tracking_error
    
    def calculate_benchmark_metrics(self, nav_history: pd.DataFrame, 
                                   benchmark_name: Optional[str] = None) -> Dict[str, float]:
        """
        Calculate benchmark comparison metrics.
        Note: Without benchmark data, calculates relative consistency metrics.
        
        Args:
            nav_history: DataFrame with date and nav columns
            benchmark_name: Optional benchmark name
            
        Returns:
            Dictionary with benchmark metrics
        """
        if nav_history is None or nav_history.empty or 'nav' not in nav_history.columns:
            return {
                'alpha': 0.0,
                'tracking_error': 0.0,
                'benchmark_outperformance': 0.0,
                'benchmark_name': benchmark_name or 'N/A'
            }
        
        # For now, without benchmark data, we calculate relative metrics
        # In production, would fetch benchmark data and calculate actual alpha/tracking error
        
        nav_series = nav_history.sort_values('date')['nav']
        returns = nav_series.pct_change().dropna() * 100
        
        if len(returns) < 12:
            return {
                'alpha': 0.0,
                'tracking_error': 0.0,
                'benchmark_outperformance': 0.0,
                'benchmark_name': benchmark_name or 'N/A'
            }
        
        # Calculate annualized return as proxy for comparison
        # (In production, would compare against actual benchmark)
        annualized_return = ((1 + returns/100).prod() ** (12/len(returns)) - 1) * 100
        
        return {
            'alpha': 0.0,  # Would be calculated with benchmark data
            'tracking_error': 0.0,  # Would be calculated with benchmark data
            'benchmark_outperformance': annualized_return,  # Proxy metric
            'benchmark_name': benchmark_name or 'N/A',
            'fund_annualized_return': annualized_return
        }
    
    def analyze_fund_benchmark(self, nav_history: pd.DataFrame, fund_name: str, 
                              category: str) -> Dict[str, float]:
        """
        Analyze fund against its benchmark.
        
        Args:
            nav_history: DataFrame with date and nav columns
            fund_name: Fund name
            category: Fund category
            
        Returns:
            Dictionary with benchmark analysis metrics
        """
        benchmark_name = self.identify_benchmark(fund_name, category)
        metrics = self.calculate_benchmark_metrics(nav_history, benchmark_name)
        
        return metrics

