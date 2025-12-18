"""
Analyzer Module
Handles performance analysis of mutual funds.
Modular design for easy extension.
"""

from .performance_analyzer import PerformanceAnalyzer
from .base_analyzer import BaseAnalyzer

__all__ = ['PerformanceAnalyzer', 'BaseAnalyzer']
