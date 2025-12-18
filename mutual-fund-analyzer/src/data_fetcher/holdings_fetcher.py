"""
Holdings Fetcher
Fetches current stock holdings for mutual funds.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from typing import List, Dict, Optional
from .scraper import WebScraper


class HoldingsFetcher:
    """Fetches mutual fund holdings data."""
    
    def __init__(self):
        """Initialize the holdings fetcher."""
        self.scraper = WebScraper(rate_limit=2.0)
    
    def fetch_fund_holdings(self, fund_name: str, fund_url: Optional[str] = None) -> List[Dict]:
        """
        Fetch current holdings for a specific fund.
        
        Args:
            fund_name: Name of the mutual fund
            fund_url: Optional URL to the fund's page
            
        Returns:
            List of holding dictionaries with stock_name, weight, etc.
        """
        holdings = []
        
        # Try to construct URL if not provided
        if not fund_url:
            # Search for fund on Moneycontrol
            search_url = f"https://www.moneycontrol.com/mutual-funds/{self._sanitize_fund_name(fund_name)}"
            fund_url = search_url
        
        try:
            soup = self.scraper.scrape_url(fund_url)
            if not soup:
                return holdings
            
            # Look for holdings table
            holdings_table = soup.find('table', class_=re.compile(r'holdings|portfolio', re.I))
            if not holdings_table:
                # Try alternative selectors
                holdings_table = soup.find('div', class_=re.compile(r'holdings', re.I))
            
            if holdings_table:
                rows = holdings_table.find_all('tr')[1:]  # Skip header
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        try:
                            stock_name = cells[0].get_text(strip=True)
                            weight = self._parse_percentage(cells[1].get_text(strip=True))
                            
                            holding = {
                                'stock_name': stock_name,
                                'weight': weight,
                                'fund_name': fund_name
                            }
                            
                            # Try to extract additional info
                            if len(cells) > 2:
                                holding['sector'] = cells[2].get_text(strip=True)
                            if len(cells) > 3:
                                holding['quantity'] = self._parse_number(cells[3].get_text(strip=True))
                            
                            if stock_name and weight > 0:
                                holdings.append(holding)
                        except Exception:
                            continue
            
        except Exception as e:
            print(f"Error fetching holdings for {fund_name}: {str(e)}")
        
        return holdings
    
    def fetch_top_10_holdings(self, fund_name: str, fund_url: Optional[str] = None) -> List[Dict]:
        """
        Fetch top 10 holdings for a fund.
        
        Args:
            fund_name: Name of the mutual fund
            fund_url: Optional URL to the fund's page
            
        Returns:
            List of top 10 holdings
        """
        all_holdings = self.fetch_fund_holdings(fund_name, fund_url)
        
        # Sort by weight and return top 10
        sorted_holdings = sorted(all_holdings, key=lambda x: x.get('weight', 0), reverse=True)
        
        return sorted_holdings[:10]
    
    def fetch_holdings_batch(self, funds: List[Dict], max_funds: int = 50) -> Dict[str, List[Dict]]:
        """
        Fetch holdings for multiple funds.
        
        Args:
            funds: List of fund dictionaries with 'fund_name' and optionally 'url'
            max_funds: Maximum number of funds to process
            
        Returns:
            Dictionary mapping fund names to their holdings
        """
        all_holdings = {}
        
        for i, fund in enumerate(funds[:max_funds]):
            fund_name = fund.get('fund_name', '')
            fund_url = fund.get('url', '')
            
            if not fund_name:
                continue
            
            print(f"  Fetching holdings for {fund_name} ({i+1}/{min(len(funds), max_funds)})...")
            holdings = self.fetch_top_10_holdings(fund_name, fund_url)
            
            if holdings:
                all_holdings[fund_name] = holdings
                print(f"    ✓ Found {len(holdings)} holdings")
            
            time.sleep(1)  # Rate limiting
        
        return all_holdings
    
    def _sanitize_fund_name(self, fund_name: str) -> str:
        """Convert fund name to URL-friendly format."""
        # Remove special characters and convert to lowercase
        sanitized = re.sub(r'[^a-zA-Z0-9\s-]', '', fund_name)
        sanitized = re.sub(r'\s+', '-', sanitized.strip())
        return sanitized.lower()
    
    def _parse_percentage(self, text: str) -> float:
        """Parse percentage value from text."""
        if not text or text == 'N/A' or text == '-':
            return 0.0
        # Remove % and other characters
        cleaned = re.sub(r'[%,\s]', '', str(text))
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    def _parse_number(self, text: str) -> float:
        """Parse number from text."""
        if not text or text == 'N/A' or text == '-':
            return 0.0
        cleaned = re.sub(r'[,\s]', '', str(text))
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

