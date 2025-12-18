"""
Analyzer Module
Handles performance analysis of mutual funds.
Modular design for easy extension.
"""

from .performance_analyzer import PerformanceAnalyzer
from .consistency_analyzer import ConsistencyAnalyzer
from .benchmark_analyzer import BenchmarkAnalyzer
from .base_analyzer import BaseAnalyzer

__all__ = ['PerformanceAnalyzer', 'ConsistencyAnalyzer', 'BenchmarkAnalyzer', 'BaseAnalyzer']
