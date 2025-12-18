#!/usr/bin/env python3
"""
Tests for Caching Mechanism
Verifies that caching works correctly with 1-month freshness.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from data_fetcher import CacheManager, MFAPIFetcher
import tempfile
import shutil
import os


def test_cache_manager_initialization():
    """Test 1: Cache Manager Initialization"""
    print("=" * 60)
    print("TEST 1: Cache Manager Initialization")
    print("=" * 60)
    
    try:
        # Test with default directory
        cache = CacheManager()
        assert cache.cache_dir.exists(), "Cache directory should be created"
        assert cache.metadata_dir.exists(), "Metadata directory should be created"
        assert cache.nav_data_dir.exists(), "NAV data directory should be created"
        assert cache.FRESHNESS_DAYS == 30, "Freshness should be 30 days"
        
        print("✓ SUCCESS: Cache manager initialized correctly")
        print(f"  Cache directory: {cache.cache_dir}")
        print(f"  Freshness: {cache.FRESHNESS_DAYS} days")
        return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_all_funds_caching():
    """Test 2: All Funds Caching"""
    print("\n" + "=" * 60)
    print("TEST 2: All Funds Caching")
    print("=" * 60)
    
    try:
        # Use temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = CacheManager(cache_dir=temp_dir)
            
            # Create sample funds data
            sample_funds = pd.DataFrame({
                'schemeCode': [100001, 100002, 100003],
                'schemeName': ['Fund A', 'Fund B', 'Fund C'],
                'isinGrowth': ['ISIN1', 'ISIN2', 'ISIN3']
            })
            
            # Test save
            cache.save_all_funds(sample_funds)
            assert cache.get_all_funds_cache_path().exists(), "Cache file should exist"
            assert cache.get_all_funds_metadata_path().exists(), "Metadata file should exist"
            
            # Test load
            loaded_funds = cache.load_all_funds()
            assert loaded_funds is not None, "Should load funds from cache"
            assert len(loaded_funds) == 3, "Should load all 3 funds"
            assert list(loaded_funds['schemeCode']) == [100001, 100002, 100003], "Data should match"
            
            print("✓ SUCCESS: All funds caching works")
            print(f"  Saved: {len(sample_funds)} funds")
            print(f"  Loaded: {len(loaded_funds)} funds")
            return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_nav_data_caching():
    """Test 3: NAV Data Caching"""
    print("\n" + "=" * 60)
    print("TEST 3: NAV Data Caching")
    print("=" * 60)
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = CacheManager(cache_dir=temp_dir)
            
            scheme_code = 100001
            dates = [datetime.now() - timedelta(days=x) for x in range(10, 0, -1)]
            navs = [100 + x * 0.5 for x in range(10)]
            
            sample_nav = pd.DataFrame({
                'date': dates,
                'nav': navs
            })
            
            # Test save
            cache.save_nav_data(scheme_code, sample_nav)
            assert cache.get_nav_cache_path(scheme_code).exists(), "NAV cache file should exist"
            assert cache.get_nav_metadata_path(scheme_code).exists(), "NAV metadata should exist"
            
            # Test load
            loaded_nav = cache.load_nav_data(scheme_code)
            assert loaded_nav is not None, "Should load NAV from cache"
            assert len(loaded_nav) == 10, "Should load all 10 NAV records"
            assert 'date' in loaded_nav.columns, "Should have date column"
            assert 'nav' in loaded_nav.columns, "Should have nav column"
            
            print("✓ SUCCESS: NAV data caching works")
            print(f"  Saved: {len(sample_nav)} NAV records for scheme {scheme_code}")
            print(f"  Loaded: {len(loaded_nav)} NAV records")
            return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_freshness_check():
    """Test 4: Freshness Check (1 Month)"""
    print("\n" + "=" * 60)
    print("TEST 4: Freshness Check (1 Month)")
    print("=" * 60)
    
    try:
        cache = CacheManager()
        
        # Test fresh data (today)
        fresh_timestamp = datetime.now()
        assert cache.is_fresh(fresh_timestamp) == True, "Today's data should be fresh"
        
        # Test fresh data (15 days ago)
        recent_timestamp = datetime.now() - timedelta(days=15)
        assert cache.is_fresh(recent_timestamp) == True, "15-day-old data should be fresh"
        
        # Test stale data (31 days ago)
        stale_timestamp = datetime.now() - timedelta(days=31)
        assert cache.is_fresh(stale_timestamp) == False, "31-day-old data should be stale"
        
        # Test stale data (exactly 30 days ago - should be fresh)
        exactly_30_days = datetime.now() - timedelta(days=30)
        assert cache.is_fresh(exactly_30_days) == True, "Exactly 30-day-old data should be fresh"
        
        print("✓ SUCCESS: Freshness check works correctly")
        print(f"  Fresh (today): {cache.is_fresh(fresh_timestamp)}")
        print(f"  Fresh (15 days): {cache.is_fresh(recent_timestamp)}")
        print(f"  Stale (31 days): {cache.is_fresh(stale_timestamp)}")
        return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_cache_expiration():
    """Test 5: Cache Expiration"""
    print("\n" + "=" * 60)
    print("TEST 5: Cache Expiration")
    print("=" * 60)
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = CacheManager(cache_dir=temp_dir)
            
            # Save data
            sample_funds = pd.DataFrame({
                'schemeCode': [100001],
                'schemeName': ['Test Fund']
            })
            cache.save_all_funds(sample_funds)
            
            # Verify it loads
            loaded = cache.load_all_funds()
            assert loaded is not None, "Should load fresh data"
            
            # Manually make metadata stale (31 days old)
            metadata_path = cache.get_all_funds_metadata_path()
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            stale_date = datetime.now() - timedelta(days=31)
            metadata['timestamp'] = stale_date.isoformat()
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f)
            
            # Should not load stale data
            stale_loaded = cache.load_all_funds()
            assert stale_loaded is None, "Should not load stale data"
            
            print("✓ SUCCESS: Cache expiration works")
            print("  Fresh data loads: ✓")
            print("  Stale data rejected: ✓")
            return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_integration_with_fetcher():
    """Test 6: Integration with MFAPIFetcher"""
    print("\n" + "=" * 60)
    print("TEST 6: Integration with MFAPIFetcher")
    print("=" * 60)
    
    try:
        # Test that fetcher uses cache
        api = MFAPIFetcher(rate_limit=0.5)
        
        # First fetch (should fetch from API and cache)
        print("  First fetch (from API)...")
        funds1 = api.fetch_all_funds()
        assert len(funds1) > 0, "Should fetch funds"
        
        # Second fetch (should use cache)
        print("  Second fetch (from cache)...")
        funds2 = api.fetch_all_funds()
        assert len(funds2) == len(funds1), "Should get same number of funds from cache"
        
        # Check cache stats
        stats = api.cache_manager.get_cache_stats()
        assert stats['all_funds_cached'] == True, "All funds should be cached"
        
        print("✓ SUCCESS: Integration with MFAPIFetcher works")
        print(f"  First fetch: {len(funds1)} funds")
        print(f"  Second fetch (cached): {len(funds2)} funds")
        print(f"  Cache stats: {stats['all_funds_cached']}")
        return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_cache_stats():
    """Test 7: Cache Statistics"""
    print("\n" + "=" * 60)
    print("TEST 7: Cache Statistics")
    print("=" * 60)
    
    try:
        cache = CacheManager()
        stats = cache.get_cache_stats()
        
        assert 'all_funds_cached' in stats, "Should have all_funds_cached"
        assert 'all_funds_age_days' in stats, "Should have all_funds_age_days"
        assert 'nav_data_cached_count' in stats, "Should have nav_data_cached_count"
        assert 'cache_dir' in stats, "Should have cache_dir"
        
        print("✓ SUCCESS: Cache statistics work")
        print(f"  All funds cached: {stats['all_funds_cached']}")
        print(f"  NAV data cached: {stats['nav_data_cached_count']} funds")
        print(f"  Cache directory: {stats['cache_dir']}")
        return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_no_limit_enforcement():
    """Test 8: No Fund Limit Enforcement"""
    print("\n" + "=" * 60)
    print("TEST 8: No Fund Limit Enforcement")
    print("=" * 60)
    
    try:
        from data_fetcher import FundFetcher
        
        fetcher = FundFetcher()
        # Check that top_funds_count is used (not hardcoded 50)
        assert fetcher.top_funds_count == 100, "Should use config value (100), not hardcoded 50"
        
        # Verify no min(50, ...) in the code
        import inspect
        source = inspect.getsource(fetcher.fetch_all_categories)
        assert 'min(50' not in source, "Should not have hardcoded 50 limit"
        
        print("✓ SUCCESS: No hardcoded limit")
        print(f"  top_funds_count from config: {fetcher.top_funds_count}")
        print("  No hardcoded 50 limit found: ✓")
        return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("CACHING MECHANISM TESTS")
    print("=" * 60)
    print("\nTesting cache functionality with 1-month freshness...\n")
    
    results = []
    
    results.append(("Cache Manager Initialization", test_cache_manager_initialization()))
    results.append(("All Funds Caching", test_all_funds_caching()))
    results.append(("NAV Data Caching", test_nav_data_caching()))
    results.append(("Freshness Check", test_freshness_check()))
    results.append(("Cache Expiration", test_cache_expiration()))
    results.append(("Integration with Fetcher", test_integration_with_fetcher()))
    results.append(("Cache Statistics", test_cache_stats()))
    results.append(("No Fund Limit", test_no_limit_enforcement()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! Caching mechanism works correctly.")
    else:
        print(f"\n⚠ {total - passed} test(s) failed.")
    
    return passed == total


if __name__ == "__main__":
    import json  # For test_cache_expiration
    success = main()
    sys.exit(0 if success else 1)

