#!/usr/bin/env python3
"""
Test analyzer flags in config.yaml
Verifies that analyzers can be enabled/disabled via config.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from data_fetcher import MFAPIFetcher, FundFetcher


def test_analyzer_flags():
    """Test that analyzer flags work correctly"""
    print("=" * 60)
    print("TEST: Analyzer Flags Configuration")
    print("=" * 60)
    
    try:
        # Test 1: All analyzers enabled (default)
        print("\n1. Testing with all analyzers enabled...")
        config_all_enabled = {
            'analysis': {
                'analyzers': {
                    'performance_analyzer': True,
                    'consistency_analyzer': True,
                    'benchmark_analyzer': True,
                    'holdings_analyzer': False
                }
            }
        }
        
        api = MFAPIFetcher(rate_limit=0.5, config=config_all_enabled)
        
        # Create sample data
        dates = [datetime.now() - timedelta(days=x*30) for x in range(24, 0, -1)]
        navs = [100 + x*2 for x in range(24)]
        nav_history = pd.DataFrame({'date': dates, 'nav': navs})
        
        sample_fund = pd.DataFrame([{
            'schemeCode': 123456,
            'schemeName': 'Test Fund - Direct Plan - Growth',
            'category': 'largecap'
        }])
        
        api.fetch_fund_history = lambda code, days=3650: nav_history
        enriched = api.enrich_funds_with_performance(sample_fund, max_funds=1)
        
        if not enriched.empty:
            fund = enriched.iloc[0]
            assert fund.get('returns_1y', 0) != 0, "Performance analyzer should run"
            assert fund.get('consistency_score', 0) != 0, "Consistency analyzer should run"
            assert fund.get('benchmark_name', 'N/A') != 'N/A', "Benchmark analyzer should run"
            print("  ✓ All enabled analyzers ran correctly")
        
        # Test 2: Consistency analyzer disabled
        print("\n2. Testing with consistency_analyzer disabled...")
        config_no_consistency = {
            'analysis': {
                'analyzers': {
                    'performance_analyzer': True,
                    'consistency_analyzer': False,  # Disabled
                    'benchmark_analyzer': True,
                    'holdings_analyzer': False
                }
            }
        }
        
        api2 = MFAPIFetcher(rate_limit=0.5, config=config_no_consistency)
        api2.fetch_fund_history = lambda code, days=3650: nav_history
        enriched2 = api2.enrich_funds_with_performance(sample_fund, max_funds=1)
        
        if not enriched2.empty:
            fund2 = enriched2.iloc[0]
            assert fund2.get('returns_1y', 0) != 0, "Performance analyzer should still run"
            assert fund2.get('consistency_score', 0) == 0.0, "Consistency analyzer should be disabled"
            assert fund2.get('benchmark_name', 'N/A') != 'N/A', "Benchmark analyzer should still run"
            print("  ✓ Consistency analyzer correctly disabled")
        
        # Test 3: Benchmark analyzer disabled
        print("\n3. Testing with benchmark_analyzer disabled...")
        config_no_benchmark = {
            'analysis': {
                'analyzers': {
                    'performance_analyzer': True,
                    'consistency_analyzer': True,
                    'benchmark_analyzer': False,  # Disabled
                    'holdings_analyzer': False
                }
            }
        }
        
        api3 = MFAPIFetcher(rate_limit=0.5, config=config_no_benchmark)
        api3.fetch_fund_history = lambda code, days=3650: nav_history
        enriched3 = api3.enrich_funds_with_performance(sample_fund, max_funds=1)
        
        if not enriched3.empty:
            fund3 = enriched3.iloc[0]
            assert fund3.get('returns_1y', 0) != 0, "Performance analyzer should still run"
            assert fund3.get('consistency_score', 0) != 0, "Consistency analyzer should still run"
            assert fund3.get('alpha', 0) == 0.0, "Benchmark analyzer should be disabled"
            print("  ✓ Benchmark analyzer correctly disabled")
        
        # Test 4: Only performance analyzer enabled
        print("\n4. Testing with only performance_analyzer enabled...")
        config_only_performance = {
            'analysis': {
                'analyzers': {
                    'performance_analyzer': True,
                    'consistency_analyzer': False,
                    'benchmark_analyzer': False,
                    'holdings_analyzer': False
                }
            }
        }
        
        api4 = MFAPIFetcher(rate_limit=0.5, config=config_only_performance)
        api4.fetch_fund_history = lambda code, days=3650: nav_history
        enriched4 = api4.enrich_funds_with_performance(sample_fund, max_funds=1)
        
        if not enriched4.empty:
            fund4 = enriched4.iloc[0]
            assert fund4.get('returns_1y', 0) != 0, "Performance analyzer should run"
            assert fund4.get('consistency_score', 0) == 0.0, "Consistency analyzer should be disabled"
            assert fund4.get('alpha', 0) == 0.0, "Benchmark analyzer should be disabled"
            print("  ✓ Only performance analyzer ran correctly")
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED: Analyzer flags work correctly")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_config_loading():
    """Test that config.yaml is loaded correctly"""
    print("\n" + "=" * 60)
    print("TEST: Config Loading")
    print("=" * 60)
    
    try:
        fetcher = FundFetcher()
        analyzer_flags = fetcher.config.get('analysis', {}).get('analyzers', {})
        
        assert 'performance_analyzer' in analyzer_flags, "Should have performance_analyzer flag"
        assert 'consistency_analyzer' in analyzer_flags, "Should have consistency_analyzer flag"
        assert 'benchmark_analyzer' in analyzer_flags, "Should have benchmark_analyzer flag"
        assert 'holdings_analyzer' in analyzer_flags, "Should have holdings_analyzer flag"
        
        print("✓ Config loaded successfully")
        print(f"  performance_analyzer: {analyzer_flags.get('performance_analyzer')}")
        print(f"  consistency_analyzer: {analyzer_flags.get('consistency_analyzer')}")
        print(f"  benchmark_analyzer: {analyzer_flags.get('benchmark_analyzer')}")
        print(f"  holdings_analyzer: {analyzer_flags.get('holdings_analyzer')}")
        
        return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("ANALYZER FLAGS TESTS")
    print("=" * 60)
    
    results = []
    results.append(("Config Loading", test_config_loading()))
    results.append(("Analyzer Flags", test_analyzer_flags()))
    
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
        print("\n✓ All tests passed! Analyzer flags work correctly.")
    else:
        print(f"\n⚠ {total - passed} test(s) failed.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

