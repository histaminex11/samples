"""
Fund Ranker
Ranks mutual funds and selects top 3 from each category.
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import yaml
import os


class FundRanker:
    """Ranks funds and selects top performers."""
    
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
    
    def calculate_score(self, fund_data: Dict) -> float:
        """
        Calculate overall score for a fund based on multiple factors.
        
        Args:
            fund_data: Dictionary containing fund metrics
            
        Returns:
            Overall score (0-100)
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
    
    def rank_funds(self, funds_df: pd.DataFrame) -> pd.DataFrame:
        """
        Rank funds in a DataFrame.
        
        Args:
            funds_df: DataFrame with fund data
            
        Returns:
            DataFrame with added 'score' and 'rank' columns
        """
        if funds_df.empty:
            return funds_df
        
        # Calculate scores for each fund
        scores = []
        for _, fund in funds_df.iterrows():
            score = self.calculate_score(fund.to_dict())
            scores.append(score)
        
        funds_df = funds_df.copy()
        funds_df['score'] = scores
        funds_df = funds_df.sort_values('score', ascending=False)
        funds_df['rank'] = range(1, len(funds_df) + 1)
        
        return funds_df
    
    def select_top_funds(self, funds_by_category: Dict[str, pd.DataFrame], top_n: int = 3) -> Dict[str, pd.DataFrame]:
        """
        Select top N funds from each category.
        
        Args:
            funds_by_category: Dictionary mapping categories to fund DataFrames
            top_n: Number of top funds to select per category
            
        Returns:
            Dictionary with top N funds per category
        """
        top_funds = {}
        
        for category, funds_df in funds_by_category.items():
            if funds_df.empty:
                top_funds[category] = pd.DataFrame()
                continue
            
            ranked_funds = self.rank_funds(funds_df)
            top_funds[category] = ranked_funds.head(top_n)
            print(f"✓ Selected top {min(top_n, len(ranked_funds))} funds for {category}")
        
        return top_funds
    
    def generate_recommendations(self, top_funds: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Generate investment recommendations report.
        
        Args:
            top_funds: Dictionary with top funds per category
            
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
                    }
                    all_recommendations.append(recommendation)
        
        recommendations_df = pd.DataFrame(all_recommendations)
        return recommendations_df.sort_values(['category', 'rank'])

