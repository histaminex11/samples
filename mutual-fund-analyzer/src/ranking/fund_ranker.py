"""
Fund Ranker
Ranks mutual funds and selects top N from each category (configurable).
Supports two ranking methods:
1. Pure returns-based ranking
2. Comprehensive ranking (returns + risk metrics)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import yaml
import os


class FundRanker:
    """Ranks funds and selects top performers using different strategies."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the fund ranker with configuration."""
        self.config = self._load_config(config_path)
        self.weights = self.config.get('ranking_weights', {})
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {}
    
    def calculate_returns_score(self, fund_data: Dict) -> float:
        """
        Calculate score based purely on historical returns.
        Uses weighted average of returns with higher weight on longer periods.
        
        Args:
            fund_data: Dictionary containing fund metrics
            
        Returns:
            Returns-based score (0-100)
        """
        score = 0.0
        total_weight = 0.0
        
        # Returns-based scoring only
        # Weight: 1Y = 0.15, 3Y = 0.20, 5Y = 0.25 (total = 0.60)
        if 'returns_1y' in fund_data and fund_data['returns_1y'] is not None:
            weight = self.weights.get('returns_1y', 0.15)
            score += fund_data['returns_1y'] * weight
            total_weight += weight
        
        if 'returns_3y' in fund_data and fund_data['returns_3y'] is not None:
            weight = self.weights.get('returns_3y', 0.20)
            score += fund_data['returns_3y'] * weight
            total_weight += weight
        
        if 'returns_5y' in fund_data and fund_data['returns_5y'] is not None:
            weight = self.weights.get('returns_5y', 0.25)
            score += fund_data['returns_5y'] * weight
            total_weight += weight
        
        # Normalize by total weight to get weighted average
        if total_weight > 0:
            score = score / total_weight
        
        # Cap at 100 (for very high returns)
        return min(score, 100.0)
    
    def calculate_comprehensive_score(self, fund_data: Dict) -> float:
        """
        Calculate comprehensive score including returns and risk metrics.
        
        Args:
            fund_data: Dictionary containing fund metrics
            
        Returns:
            Comprehensive score (0-100)
        """
        score = 0.0
        
        # Returns-based scoring
        if 'returns_1y' in fund_data and fund_data['returns_1y']:
            score += (fund_data['returns_1y'] / 100) * self.weights.get('returns_1y', 0.15) * 100
        
        if 'returns_3y' in fund_data and fund_data['returns_3y']:
            score += (fund_data['returns_3y'] / 100) * self.weights.get('returns_3y', 0.20) * 100
        
        if 'returns_5y' in fund_data and fund_data['returns_5y']:
            score += (fund_data['returns_5y'] / 100) * self.weights.get('returns_5y', 0.25) * 100
        
        # Risk-adjusted returns
        if 'sharpe_ratio' in fund_data and fund_data['sharpe_ratio']:
            normalized_sharpe = min(fund_data['sharpe_ratio'] / 2.0, 1.0)  # Normalize to 0-1
            score += normalized_sharpe * self.weights.get('sharpe_ratio', 0.20) * 100
        
        # Consistency (lower volatility is better)
        if 'standard_deviation' in fund_data and fund_data['standard_deviation']:
            # Inverse relationship - lower std dev = higher score
            normalized_consistency = max(0, 1 - (fund_data['standard_deviation'] / 30))
            score += normalized_consistency * self.weights.get('consistency', 0.10) * 100
        
        # Risk score (inverse - lower risk = higher score)
        if 'risk_score' in fund_data:
            risk_factor = 1 - (fund_data['risk_score'] / 100)
            score += risk_factor * self.weights.get('risk_score', 0.10) * 100
        
        return min(score, 100.0)  # Cap at 100
    
    def rank_funds(self, funds_df: pd.DataFrame, method: str = 'comprehensive') -> pd.DataFrame:
        """
        Rank funds in a DataFrame using specified method.
        
        Args:
            funds_df: DataFrame with fund data
            method: 'returns' for pure returns-based, 'comprehensive' for full analysis
            
        Returns:
            DataFrame with added 'score' and 'rank' columns
        """
        if funds_df.empty:
            return funds_df
        
        # Choose scoring method
        if method == 'returns':
            score_func = self.calculate_returns_score
        else:
            score_func = self.calculate_comprehensive_score
        
        # Calculate scores for each fund
        scores = []
        for _, fund in funds_df.iterrows():
            score = score_func(fund.to_dict())
            scores.append(score)
        
        funds_df = funds_df.copy()
        funds_df['score'] = scores
        funds_df = funds_df.sort_values('score', ascending=False)
        funds_df['rank'] = range(1, len(funds_df) + 1)
        
        return funds_df
    
    def select_top_funds(self, funds_by_category: Dict[str, pd.DataFrame], 
                        top_n: int = 3, method: str = 'comprehensive') -> Dict[str, pd.DataFrame]:
        """
        Select top N funds from each category using specified method.
        
        Args:
            funds_by_category: Dictionary mapping categories to fund DataFrames
            top_n: Number of top funds to select per category
            method: 'returns' or 'comprehensive'
            
        Returns:
            Dictionary with top N funds per category
        """
        top_funds = {}
        
        for category, funds_df in funds_by_category.items():
            if funds_df.empty:
                top_funds[category] = pd.DataFrame()
                continue
            
            ranked_funds = self.rank_funds(funds_df, method=method)
            top_funds[category] = ranked_funds.head(top_n)
            method_label = "returns-based" if method == 'returns' else "comprehensive"
            print(f"✓ Selected top {min(top_n, len(ranked_funds))} funds for {category} ({method_label})")
        
        return top_funds
    
    def generate_recommendations(self, top_funds: Dict[str, pd.DataFrame], 
                                method: str = 'comprehensive') -> pd.DataFrame:
        """
        Generate investment recommendations report.
        
        Args:
            top_funds: Dictionary with top funds per category
            method: 'returns' or 'comprehensive' (for labeling)
            
        Returns:
            DataFrame with recommendations
        """
        all_recommendations = []
        
        for category, funds_df in top_funds.items():
            if not funds_df.empty:
                for _, fund in funds_df.iterrows():
                    recommendation = {
                        'category': category,
                        'fund_name': fund.get('fund_name', ''),
                        'rank': fund.get('rank', 0),
                        'score': fund.get('score', 0),
                        'returns_1y': fund.get('returns_1y', 0),
                        'returns_3y': fund.get('returns_3y', 0),
                        'returns_5y': fund.get('returns_5y', 0),
                        'sharpe_ratio': fund.get('sharpe_ratio', 0),
                        'standard_deviation': fund.get('standard_deviation', 0),
                        'max_drawdown': fund.get('max_drawdown', 0),
                        'risk_score': fund.get('risk_score', 0),
                        'method': method
                    }
                    all_recommendations.append(recommendation)
        
        recommendations_df = pd.DataFrame(all_recommendations)
        return recommendations_df.sort_values(['category', 'rank'])
