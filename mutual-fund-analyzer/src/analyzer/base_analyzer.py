"""
Base Analyzer
Base class for all analyzers to ensure modularity and extensibility.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import pandas as pd


class BaseAnalyzer(ABC):
    """Base class for all fund analyzers."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the analyzer.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
    
    @abstractmethod
    def analyze(self, fund_data: pd.DataFrame) -> pd.DataFrame:
        """
        Perform analysis on fund data.
        
        Args:
            fund_data: DataFrame with fund information
            
        Returns:
            DataFrame with analysis results
        """
        pass
    
    def validate_data(self, fund_data: pd.DataFrame) -> bool:
        """
        Validate input data.
        
        Args:
            fund_data: DataFrame to validate
            
        Returns:
            True if valid, False otherwise
        """
        if fund_data is None or fund_data.empty:
            return False
        return True
    
    def get_required_columns(self) -> list:
        """
        Get list of required columns for this analyzer.
        
        Returns:
            List of required column names
        """
        return []

