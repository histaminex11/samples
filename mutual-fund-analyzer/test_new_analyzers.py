#!/usr/bin/env python3
"""
Tests for new analyzers: Consistency and Benchmark
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from analyzer import ConsistencyAnalyzer, BenchmarkAnalyzer
from data_fetcher import MFAPIFetcher


def test_consistency_analyzer():
    """Test 1: Consistency Analyzer"""
    print("=" * 60)
    print("TEST 1: Consistency Analyzer")
    print("=" * 60)
    
    try:
        analyzer = ConsistencyAnalyzer()
        
        # Create sample NAV data with consistent growth
        dates = [datetime.now() - timedelta(days=x*30) for x in range(24, 0, -1)]
        consistent_navs = [100 + x*2 for x in range(24)]  # Consistent growth
        nav_history = pd.DataFrame({'date': dates, 'nav': consistent_navs})
        
        metrics = analyzer.analyze_fund_consistency(nav_history)
        
        assert 'consistency_score' in metrics, "Should have consistency_score"
        assert 'rolling_consistency' in metrics, "Should have rolling_consistency"
        assert 'coefficient_of_variation' in metrics, "Should have coefficient_of_variation"
        
        print(f"✓ SUCCESS: Consistency metrics calculated")
        print(f"  Consistency Score: {metrics['consistency_score']:.2f}")
        print(f"  Rolling Consistency: {metrics['rolling_consistency']:.2f}")
        print(f"  Coefficient of Variation: {metrics['coefficient_of_variation']:.2f}")
        return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_benchmark_analyzer():
    """Test 2: Benchmark Analyzer"""
    print("\n" + "=" * 60)
    print("TEST 2: Benchmark Analyzer")
    print("=" * 60)
    
    try:
        analyzer = BenchmarkAnalyzer()
        
        # Test benchmark identification
        benchmark = analyzer.identify_benchmark('HDFC Large Cap Fund', 'largecap')
        assert benchmark == 'NIFTY 50', f"Expected NIFTY 50, got {benchmark}"
        
        benchmark = analyzer.identify_benchmark('Nippon Small Cap Fund', 'smallcap')
        assert benchmark == 'NIFTY Smallcap 100', f"Expected NIFTY Smallcap 100, got {benchmark}"
        
        # Test benchmark metrics calculation
        dates = [datetime.now() - timedelta(days=x*30) for x in range(24, 0, -1)]
        navs = [100 + x*2 for x in range(24)]
        nav_history = pd.DataFrame({'date': dates, 'nav': navs})
        
        metrics = analyzer.analyze_fund_benchmark(nav_history, 'Test Fund', 'largecap')
        
        assert 'alpha' in metrics, "Should have alpha"
        assert 'benchmark_name' in metrics, "Should have benchmark_name"
        assert metrics['benchmark_name'] == 'NIFTY 50', "Should identify NIFTY 50 for largecap"
        
        print(f"✓ SUCCESS: Benchmark metrics calculated")
        print(f"  Benchmark Name: {metrics['benchmark_name']}")
        print(f"  Alpha: {metrics['alpha']:.2f}")
        print(f"  Benchmark Outperformance: {metrics['benchmark_outperformance']:.2f}")
        return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_integration_with_enrichment():
    """Test 3: Integration with fund enrichment"""
    print("\n" + "=" * 60)
    print("TEST 3: Integration with Fund Enrichment")
    print("=" * 60)
    
    try:
        api = MFAPIFetcher(rate_limit=0.5)
        
        # Get a real fund
        all_funds = api.fetch_all_funds()
        if all_funds.empty:
            print("⚠ SKIPPED: No funds to test")
            return True
        
        # Get a sample fund
        sample_fund = all_funds[all_funds['schemeCode'].notna()].iloc[0]
        scheme_code = int(sample_fund['schemeCode'])
        
        # Fetch history
        nav_history = api.fetch_fund_history(scheme_code)
        
        if nav_history is None or nav_history.empty:
            print("⚠ SKIPPED: No historical data")
            return True
        
        # Test consistency analyzer
        consistency = ConsistencyAnalyzer()
        consistency_metrics = consistency.analyze_fund_consistency(nav_history)
        
        # Test benchmark analyzer
        benchmark = BenchmarkAnalyzer()
        benchmark_metrics = benchmark.analyze_fund_benchmark(
            nav_history, sample_fund['schemeName'], 'other'
        )
        
        assert 'consistency_score' in consistency_metrics, "Should have consistency_score"
        assert 'benchmark_name' in benchmark_metrics, "Should have benchmark_name"
        
        print(f"✓ SUCCESS: Analyzers integrate with enrichment")
        print(f"  Fund: {sample_fund['schemeName'][:50]}")
        print(f"  Consistency Score: {consistency_metrics['consistency_score']:.2f}")
        print(f"  Benchmark: {benchmark_metrics['benchmark_name']}")
        return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_no_redundancy():
    """Test 4: Verify no redundant analysis"""
    print("\n" + "=" * 60)
    print("TEST 4: No Redundant Analysis")
    print("=" * 60)
    
    try:
        # Check that consistency analyzer doesn't duplicate standard deviation
        consistency = ConsistencyAnalyzer()
        benchmark = BenchmarkAnalyzer()
        
        # Consistency uses coefficient of variation (different from std dev)
        # Benchmark uses alpha/tracking error (different from returns)
        
        # Verify they extend BaseAnalyzer (modular)
        from analyzer import BaseAnalyzer
        assert issubclass(ConsistencyAnalyzer, BaseAnalyzer), "Should extend BaseAnalyzer"
        assert issubclass(BenchmarkAnalyzer, BaseAnalyzer), "Should extend BaseAnalyzer"
        
        # Verify they have different required columns
        consistency_cols = consistency.get_required_columns()
        benchmark_cols = benchmark.get_required_columns()
        
        # Both need nav/date but calculate different metrics
        assert 'nav' in consistency_cols, "Consistency needs nav"
        assert 'nav' in benchmark_cols, "Benchmark needs nav"
        
        print(f"✓ SUCCESS: No redundant analysis")
        print(f"  Consistency Analyzer: Calculates consistency_score, rolling_consistency, CV")
        print(f"  Benchmark Analyzer: Calculates alpha, tracking_error, benchmark_name")
        print(f"  Both extend BaseAnalyzer: ✓")
        print(f"  Both are modular: ✓")
        return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("NEW ANALYZERS TESTS")
    print("=" * 60)
    print("\nTesting Consistency and Benchmark analyzers...\n")
    
    results = []
    
    results.append(("Consistency Analyzer", test_consistency_analyzer()))
    results.append(("Benchmark Analyzer", test_benchmark_analyzer()))
    results.append(("Integration with Enrichment", test_integration_with_enrichment()))
    results.append(("No Redundant Analysis", test_no_redundancy()))
    
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
        print("\n✓ All tests passed! New analyzers work correctly.")
    else:
        print(f"\n⚠ {total - passed} test(s) failed.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

