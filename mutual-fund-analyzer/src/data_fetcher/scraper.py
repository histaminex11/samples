"""
Web Scraper
Handles web scraping from various mutual fund data sources.
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from typing import Dict, List, Optional
import pandas as pd
import json


class WebScraper:
    """Web scraper for mutual fund data sources."""
    
    # Category to URL mapping for Moneycontrol Performance Tracker
    MONEYCONTROL_CATEGORIES = {
        'smallcap': 'small-cap-funds',
        'midcap': 'mid-cap-funds',
        'largecap': 'large-cap-funds',
        'index_funds': 'index-fundsetfs',
        'elss': 'elss-funds',
        'hybrid': 'hybrid-funds',
        'debt': 'debt-funds',
        'sectoral': 'sectoral-funds'
    }
    
    # Category mapping for Value Research
    VALUERESEARCH_CATEGORIES = {
        'smallcap': 'equity-small-cap',
        'midcap': 'equity-mid-cap',
        'largecap': 'equity-large-cap',
        'index_funds': 'equity-index',
        'elss': 'equity-elss',
        'hybrid': 'hybrid',
        'debt': 'debt',
        'sectoral': 'equity-sectoral'
    }
    
    def __init__(self, rate_limit: float = 2.0):
        """
        Initialize web scraper.
        
        Args:
            rate_limit: Minimum seconds between requests
        """
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'https://www.moneycontrol.com/',
            'DNT': '1',
        })
    
    def _rate_limit_check(self):
        """Enforce rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last)
        
        self.last_request_time = time.time()
    
    def scrape_url(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """
        Scrape a URL and return parsed HTML.
        
        Args:
            url: URL to scrape
            retries: Number of retry attempts
            
        Returns:
            BeautifulSoup object or None
        """
        self._rate_limit_check()
        
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except requests.RequestException as e:
                if attempt < retries - 1:
                    print(f"Retry {attempt + 1}/{retries} for {url}")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    print(f"Error scraping {url}: {str(e)}")
                    return None
        return None
    
    def _parse_number(self, text: str) -> float:
        """Parse number from text, handling percentages and commas."""
        if not text or text == 'N/A' or text == '-':
            return 0.0
        # Remove commas, %, and other characters
        cleaned = re.sub(r'[%,₹,\s]', '', str(text))
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    def scrape_moneycontrol_funds(self, category: str, max_funds: int = 100) -> pd.DataFrame:
        """
        Scrape mutual funds from Moneycontrol.
        
        Args:
            category: Fund category
            max_funds: Maximum number of funds to fetch
            
        Returns:
            DataFrame with fund data
        """
        print(f"Scraping Moneycontrol for {category} funds...")
        
        category_url = self.MONEYCONTROL_CATEGORIES.get(category, category)
        # Use performance-tracker URL structure (as per user's specification)
        base_url = f"https://www.moneycontrol.com/mutual-funds/performance-tracker/returns/{category_url}.html"
        
        funds_data = []
        
        try:
            soup = self.scrape_url(base_url)
            if not soup:
                return pd.DataFrame()
            
            # Moneycontrol performance tracker uses tables with fund data
            # Look for the main data table - avoid ad tables by checking for data patterns
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                if len(rows) < 2:  # Need at least header + 1 data row
                    continue
                
                # Check if this looks like a fund data table (has fund names, NAV, returns)
                first_data_row = rows[1] if len(rows) > 1 else None
                if first_data_row:
                    cells = first_data_row.find_all(['td', 'th'])
                    # Skip if it looks like an ad table (very few cells or no meaningful data)
                    if len(cells) < 2:
                        continue
                
                # Process rows (skip header)
                for row in rows[1:max_funds+1]:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) < 2:
                        continue
                    
                    try:
                        # Extract fund name (usually first column)
                        fund_name_cell = cells[0]
                        fund_name = fund_name_cell.get_text(strip=True)
                        
                        # Clean up fund name (remove extra whitespace, newlines)
                        fund_name = ' '.join(fund_name.split())
                        
                        # Skip if name is too short or looks like header/ad
                        if not fund_name or len(fund_name) < 3 or fund_name.upper() in ['FUND NAME', 'SCHEME NAME', 'NAV']:
                            continue
                        
                        fund_data = {
                            'fund_name': fund_name,
                            'category': category,
                            'nav': 0.0,
                            'source': 'moneycontrol',
                            'url': base_url
                        }
                        
                        # Extract data from cells - be flexible with column positions
                        for i, cell in enumerate(cells[1:], start=1):
                            cell_text = cell.get_text(strip=True)
                            
                            # Skip empty cells or cells that look like ads/headers
                            if not cell_text or len(cell_text) > 100:  # Skip very long text (likely ads)
                                continue
                            
                            # Look for NAV (usually a decimal number, often in early columns)
                            if i <= 3 and re.search(r'^\d+\.\d+$', cell_text):
                                try:
                                    nav_val = float(cell_text)
                                    if 1.0 <= nav_val <= 100000.0:  # Reasonable NAV range
                                        fund_data['nav'] = nav_val
                                except ValueError:
                                    pass
                            
                            # Look for returns (percentage values with % or negative signs)
                            if '%' in cell_text or (cell_text.startswith('-') and '.' in cell_text):
                                return_val = self._parse_number(cell_text)
                                if return_val != 0.0 and -100 <= return_val <= 100:  # Reasonable return range
                                    # Assign returns based on position (approximate mapping)
                                    if 'returns_1y' not in fund_data or fund_data['returns_1y'] == 0.0:
                                        fund_data['returns_1y'] = return_val
                                    elif 'returns_3y' not in fund_data or fund_data['returns_3y'] == 0.0:
                                        fund_data['returns_3y'] = return_val
                                    elif 'returns_5y' not in fund_data or fund_data['returns_5y'] == 0.0:
                                        fund_data['returns_5y'] = return_val
                            
                            # Look for AUM (large numbers, often with 'Cr' or 'L')
                            if 'Cr' in cell_text or 'L' in cell_text or ('AUM' in cell_text.upper()):
                                aum_val = self._parse_number(cell_text.replace('Cr', '').replace('L', ''))
                                if aum_val > 0:
                                    fund_data['aum'] = aum_val
                        
                        if fund_name and fund_name != 'N/A':
                            funds_data.append(fund_data)
                            
                    except Exception as e:
                        # Silently skip problematic rows (likely ads or malformed data)
                        continue
                
                # If we found funds in this table, break (found the right table)
                if funds_data:
                    break
            
            # If no funds found in tables, try alternative: look for fund name links
            if not funds_data:
                fund_links = soup.find_all('a', href=re.compile(r'/mutual-funds/.*fund', re.I))
                for link in fund_links[:max_funds]:
                    fund_name = link.get_text(strip=True)
                    if fund_name and len(fund_name) > 3:
                        funds_data.append({
                            'fund_name': fund_name,
                            'category': category,
                            'nav': 0.0,
                            'source': 'moneycontrol',
                            'url': link.get('href', '')
                        })
            
        except Exception as e:
            print(f"Error scraping Moneycontrol {category}: {str(e)}")
        
        return pd.DataFrame(funds_data)
    
    def scrape_valueresearch_funds(self, category: str, max_funds: int = 100) -> pd.DataFrame:
        """
        Scrape mutual funds from Value Research.
        
        Args:
            category: Fund category
            max_funds: Maximum number of funds to fetch
            
        Returns:
            DataFrame with fund data
        """
        print(f"Scraping Value Research for {category} funds...")
        
        category_url = self.VALUERESEARCH_CATEGORIES.get(category, category)
        base_url = f"https://www.valueresearchonline.com/funds/selector/category/{category_url}"
        
        funds_data = []
        
        try:
            soup = self.scrape_url(base_url)
            if not soup:
                return pd.DataFrame()
            
            # Value Research often has fund data in structured format
            # Look for fund listings
            fund_rows = soup.find_all(['tr', 'div'], class_=re.compile(r'fund|row|item'))
            
            for row in fund_rows[:max_funds]:
                try:
                    # Try to extract fund name
                    name_elem = row.find(['a', 'span', 'td'], class_=re.compile(r'name|fund-name', re.I))
                    if not name_elem:
                        name_elem = row.find('a')
                    
                    if name_elem:
                        fund_name = name_elem.get_text(strip=True)
                        
                        if fund_name and len(fund_name) > 3:
                            fund_data = {
                                'fund_name': fund_name,
                                'category': category,
                                'nav': 0.0,
                                'source': 'valueresearch',
                                'url': base_url
                            }
                            
                            # Try to extract returns
                            return_elems = row.find_all(['td', 'span'], class_=re.compile(r'return|nav', re.I))
                            for i, elem in enumerate(return_elems[:3]):
                                value = self._parse_number(elem.get_text(strip=True))
                                if i == 0:
                                    fund_data['returns_1y'] = value
                                elif i == 1:
                                    fund_data['returns_3y'] = value
                                elif i == 2:
                                    fund_data['returns_5y'] = value
                            
                            funds_data.append(fund_data)
                except Exception as e:
                    continue
            
            # Alternative: Look for JSON data in script tags
            if not funds_data:
                scripts = soup.find_all('script', type='application/json')
                for script in scripts:
                    try:
                        data = json.loads(script.string)
                        if isinstance(data, list):
                            for item in data[:max_funds]:
                                if 'name' in item or 'fundName' in item:
                                    fund_name = item.get('name') or item.get('fundName')
                                    funds_data.append({
                                        'fund_name': fund_name,
                                        'category': category,
                                        'nav': item.get('nav', 0.0),
                                        'returns_1y': item.get('returns1y', 0.0),
                                        'returns_3y': item.get('returns3y', 0.0),
                                        'returns_5y': item.get('returns5y', 0.0),
                                        'source': 'valueresearch',
                                        'url': base_url
                                    })
                    except (json.JSONDecodeError, KeyError):
                        continue
            
        except Exception as e:
            print(f"Error scraping Value Research {category}: {str(e)}")
        
        return pd.DataFrame(funds_data)
    
    def fetch_amfi_data(self, category: str) -> pd.DataFrame:
        """
        Fetch data from AMFI (Association of Mutual Funds in India).
        AMFI provides NAV data via CSV/API.
        
        Args:
            category: Fund category
            
        Returns:
            DataFrame with fund data
        """
        print(f"Fetching AMFI data for {category} funds...")
        
        # AMFI NAV data URL (this is a public endpoint)
        amfi_url = "https://www.amfiindia.com/spages/NAVAll.txt"
        
        funds_data = []
        
        try:
            self._rate_limit_check()
            response = self.session.get(amfi_url, timeout=30)
            response.raise_for_status()
            
            # Parse AMFI NAV text format
            lines = response.text.split('\n')
            current_scheme = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # AMFI format: Scheme Code;ISIN Div Payout/ ISIN Growth / ISIN Div Reinv;Scheme Name;Net Asset Value;Date
                if ';' in line and not line.startswith('Open Ended Schemes'):
                    parts = line.split(';')
                    if len(parts) >= 4:
                        try:
                            scheme_name = parts[2].strip()
                            nav = self._parse_number(parts[3].strip())
                            
                            # Filter by category keywords
                            category_keywords = {
                                'smallcap': ['small', 'small cap'],
                                'midcap': ['mid', 'mid cap'],
                                'largecap': ['large', 'large cap'],
                                'elss': ['elss', 'tax'],
                                'index_funds': ['index', 'nifty', 'sensex']
                            }
                            
                            keywords = category_keywords.get(category, [category])
                            if any(keyword.lower() in scheme_name.lower() for keyword in keywords):
                                funds_data.append({
                                    'fund_name': scheme_name,
                                    'category': category,
                                    'nav': nav,
                                    'source': 'amfi',
                                    'url': amfi_url
                                })
                        except (IndexError, ValueError):
                            continue
            
        except Exception as e:
            print(f"Error fetching AMFI data: {str(e)}")
        
        return pd.DataFrame(funds_data)

