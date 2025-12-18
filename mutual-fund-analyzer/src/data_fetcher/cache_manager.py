"""
Cache Manager
Manages caching of fetched mutual fund data to avoid re-fetching.
Data freshness: 1 month
"""

import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict


class CacheManager:
    """Manages caching of mutual fund data."""
    
    CACHE_DIR = "data/cache"
    FRESHNESS_DAYS = 30  # 1 month
    
    def __init__(self, cache_dir: str = None):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Optional custom cache directory
        """
        self.cache_dir = Path(cache_dir or self.CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Subdirectories
        self.metadata_dir = self.cache_dir / "metadata"
        self.nav_data_dir = self.cache_dir / "nav_data"
        self.metadata_dir.mkdir(exist_ok=True)
        self.nav_data_dir.mkdir(exist_ok=True)
    
    def is_fresh(self, timestamp: datetime) -> bool:
        """
        Check if data is fresh (less than 1 month old).
        
        Args:
            timestamp: Data timestamp
            
        Returns:
            True if fresh, False otherwise
        """
        if timestamp is None:
            return False
        
        age = datetime.now() - timestamp
        return age.days < self.FRESHNESS_DAYS
    
    def get_all_funds_cache_path(self) -> Path:
        """Get path for all funds cache."""
        return self.cache_dir / "all_funds.csv"
    
    def get_all_funds_metadata_path(self) -> Path:
        """Get path for all funds metadata (timestamp)."""
        return self.metadata_dir / "all_funds_metadata.json"
    
    def get_nav_cache_path(self, scheme_code: int) -> Path:
        """Get path for NAV data cache."""
        return self.nav_data_dir / f"{scheme_code}.csv"
    
    def get_nav_metadata_path(self, scheme_code: int) -> Path:
        """Get path for NAV metadata."""
        return self.metadata_dir / f"nav_{scheme_code}_metadata.json"
    
    def save_all_funds(self, funds_df: pd.DataFrame) -> None:
        """
        Save all funds data with timestamp.
        
        Args:
            funds_df: DataFrame with all funds
        """
        # Save data
        cache_path = self.get_all_funds_cache_path()
        funds_df.to_csv(cache_path, index=False)
        
        # Save metadata
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'count': len(funds_df),
            'columns': list(funds_df.columns)
        }
        metadata_path = self.get_all_funds_metadata_path()
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def load_all_funds(self) -> Optional[pd.DataFrame]:
        """
        Load all funds from cache if fresh.
        
        Returns:
            DataFrame if fresh cache exists, None otherwise
        """
        cache_path = self.get_all_funds_cache_path()
        metadata_path = self.get_all_funds_metadata_path()
        
        if not cache_path.exists() or not metadata_path.exists():
            return None
        
        try:
            # Check metadata
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            timestamp = datetime.fromisoformat(metadata['timestamp'])
            if not self.is_fresh(timestamp):
                return None
            
            # Load data
            funds_df = pd.read_csv(cache_path)
            return funds_df
        except Exception as e:
            # If any error, return None to force re-fetch
            return None
    
    def save_nav_data(self, scheme_code: int, nav_df: pd.DataFrame) -> None:
        """
        Save NAV data for a fund with timestamp.
        
        Args:
            scheme_code: Scheme code
            nav_df: DataFrame with NAV data
        """
        # Save data
        cache_path = self.get_nav_cache_path(scheme_code)
        nav_df.to_csv(cache_path, index=False)
        
        # Save metadata
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'scheme_code': scheme_code,
            'rows': len(nav_df),
            'date_range': {
                'start': nav_df['date'].min() if 'date' in nav_df.columns else None,
                'end': nav_df['date'].max() if 'date' in nav_df.columns else None
            }
        }
        metadata_path = self.get_nav_metadata_path(scheme_code)
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def load_nav_data(self, scheme_code: int) -> Optional[pd.DataFrame]:
        """
        Load NAV data from cache if fresh.
        
        Args:
            scheme_code: Scheme code
            
        Returns:
            DataFrame if fresh cache exists, None otherwise
        """
        cache_path = self.get_nav_cache_path(scheme_code)
        metadata_path = self.get_nav_metadata_path(scheme_code)
        
        if not cache_path.exists() or not metadata_path.exists():
            return None
        
        try:
            # Check metadata
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            timestamp = datetime.fromisoformat(metadata['timestamp'])
            if not self.is_fresh(timestamp):
                return None
            
            # Load data
            nav_df = pd.read_csv(cache_path)
            # Convert date column back to datetime
            if 'date' in nav_df.columns:
                nav_df['date'] = pd.to_datetime(nav_df['date'])
            return nav_df
        except Exception as e:
            # If any error, return None to force re-fetch
            return None
    
    def clear_cache(self, cache_type: str = 'all') -> None:
        """
        Clear cache.
        
        Args:
            cache_type: 'all', 'funds', or 'nav'
        """
        if cache_type in ['all', 'funds']:
            cache_path = self.get_all_funds_cache_path()
            metadata_path = self.get_all_funds_metadata_path()
            if cache_path.exists():
                cache_path.unlink()
            if metadata_path.exists():
                metadata_path.unlink()
        
        if cache_type in ['all', 'nav']:
            # Clear all NAV caches
            for nav_file in self.nav_data_dir.glob("*.csv"):
                nav_file.unlink()
            for meta_file in self.metadata_dir.glob("nav_*_metadata.json"):
                meta_file.unlink()
    
    def get_cache_stats(self) -> Dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        stats = {
            'all_funds_cached': False,
            'all_funds_age_days': None,
            'nav_data_cached_count': 0,
            'cache_dir': str(self.cache_dir)
        }
        
        # Check all funds cache
        metadata_path = self.get_all_funds_metadata_path()
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                timestamp = datetime.fromisoformat(metadata['timestamp'])
                age = datetime.now() - timestamp
                stats['all_funds_cached'] = True
                stats['all_funds_age_days'] = age.days
            except:
                pass
        
        # Count NAV caches
        nav_files = list(self.nav_data_dir.glob("*.csv"))
        stats['nav_data_cached_count'] = len(nav_files)
        
        return stats

