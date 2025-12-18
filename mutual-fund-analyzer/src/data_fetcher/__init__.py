"""
Data Fetcher Module
Handles fetching mutual fund data from MF API (api.mfapi.in).
"""

from .fund_fetcher import FundFetcher
from .mf_api_fetcher import MFAPIFetcher

__all__ = ['FundFetcher', 'MFAPIFetcher']

