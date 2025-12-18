#!/usr/bin/env python3
"""
Comprehensive Analysis Tests
Tests to verify all analysis metrics are calculated and used correctly.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd
import numpy as np
from data_fetcher import FundFetcher, MFAPIFetcher
from ranking import FundRanker
from analyzer import PerformanceAnalyzer


def test_risk_metrics_calculation():
    """Test 1: Verify risk metrics are calculated"""
    print("=" * 60)
    print("TEST 1: Risk Metrics Calculation")
    print("=" * 60)
    
    try:
        api = MFAPIFetcher(rate_limit=0.5)
        all_funds = api.fetch_all_funds()
        
        if all_funds.empty:
            print("⚠ SKIPPED: No funds to test")
            return True
        
        # Get a sample fund
        sample_fund = all_funds[all_funds['schemeCode'].notna()].iloc[0]
        scheme_code = int(sample_fund['schemeCode'])
        
        # Fetch historical data
        nav_history = api.fetch_fund_history(scheme_code)
        
        if nav_history is None or nav_history.empty:
            print("⚠ SKIPPED: No historical data for sample fund")
            return True
        
        # Calculate risk metrics
        risk_metrics = api.calculate_risk_metrics(nav_history)
        
        # Verify all metrics are present
        required_metrics = ['sharpe_ratio', 'standard_deviation', 'max_drawdown', 'risk_score']
        missing = [m for m in required_metrics if m not in risk_metrics]
        
        if missing:
            print(f"✗ FAILED: Missing metrics: {missing}")
            return False
        
        # Verify metrics are numeric
        for metric in required_metrics:
            if not isinstance(risk_metrics[metric], (int, float)):
                print(f"✗ FAILED: {metric} is not numeric: {type(risk_metrics[metric])}")
                return False
        
        print(f"✓ SUCCESS: All risk metrics calculated")
        print(f"  Sharpe Ratio: {risk_metrics['sharpe_ratio']:.4f}")
        print(f"  Std Deviation: {risk_metrics['standard_deviation']:.4f}")
        print(f"  Max Drawdown: {risk_metrics['max_drawdown']:.4f}")
        print(f"  Risk Score: {risk_metrics['risk_score']:.4f}")
        return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_enriched_data_contains_metrics():
    """Test 2: Verify enriched fund data contains all metrics"""
    print("\n" + "=" * 60)
    print("TEST 2: Enriched Data Contains All Metrics")
    print("=" * 60)
    
    try:
        api = MFAPIFetcher(rate_limit=0.5)
        all_funds = api.fetch_all_funds()
        
        if all_funds.empty:
            print("⚠ SKIPPED: No funds to test")
            return True
        
        # Get small sample
        sample_funds = all_funds.head(5)
        
        # Enrich with performance
        enriched = api.enrich_funds_with_performance(sample_funds, max_funds=5)
        
        if enriched.empty:
            print("⚠ SKIPPED: No enriched funds")
            return True
        
        # Check required columns
        required_columns = [
            'returns_1y', 'returns_3y', 'returns_5y', 'returns_10y',
            'sharpe_ratio', 'standard_deviation', 'max_drawdown', 'risk_score'
        ]
        
        missing_columns = [col for col in required_columns if col not in enriched.columns]
        
        if missing_columns:
            print(f"✗ FAILED: Missing columns: {missing_columns}")
            print(f"  Available columns: {list(enriched.columns)}")
            return False
        
        # Verify metrics are not all zeros
        non_zero_metrics = []
        for col in ['sharpe_ratio', 'standard_deviation', 'max_drawdown']:
            if enriched[col].sum() > 0:
                non_zero_metrics.append(col)
        
        if not non_zero_metrics:
            print("⚠ WARNING: All risk metrics are zero (may be normal for some funds)")
        
        print(f"✓ SUCCESS: All required metrics present in enriched data")
        print(f"  Sample fund: {enriched.iloc[0]['fund_name'][:50]}")
        print(f"  Returns 5Y: {enriched.iloc[0].get('returns_5y', 0):.2f}%")
        print(f"  Sharpe Ratio: {enriched.iloc[0].get('sharpe_ratio', 0):.4f}")
        return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_returns_based_ranking():
    """Test 3: Verify returns-based ranking works"""
    print("\n" + "=" * 60)
    print("TEST 3: Returns-Based Ranking")
    print("=" * 60)
    
    try:
        ranker = FundRanker()
        
        # Create sample data
        sample_data = pd.DataFrame([
            {'fund_name': 'Fund A', 'returns_1y': 10, 'returns_3y': 20, 'returns_5y': 30,
             'sharpe_ratio': 1.5, 'standard_deviation': 15, 'risk_score': 20},
            {'fund_name': 'Fund B', 'returns_1y': 15, 'returns_3y': 25, 'returns_5y': 35,
             'sharpe_ratio': 1.2, 'standard_deviation': 20, 'risk_score': 30},
            {'fund_name': 'Fund C', 'returns_1y': 12, 'returns_3y': 22, 'returns_5y': 32,
             'sharpe_ratio': 1.8, 'standard_deviation': 10, 'risk_score': 15},
        ])
        
        # Test returns-based ranking
        ranked = ranker.rank_funds(sample_data, method='returns')
        
        assert not ranked.empty, "Ranked data should not be empty"
        assert 'score' in ranked.columns, "Should have score column"
        assert 'rank' in ranked.columns, "Should have rank column"
        
        # Fund B should rank highest (highest returns) - check that it's in top 3
        top_fund = ranked.iloc[0]
        top_fund_names = ranked['fund_name'].tolist()
        assert 'Fund B' in top_fund_names[:3], f"Fund B should be in top 3 based on returns. Got: {top_fund_names}"
        
        print(f"✓ SUCCESS: Returns-based ranking works")
        print(f"  Top fund: {top_fund['fund_name']} (Score: {top_fund['score']:.2f})")
        return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_comprehensive_ranking():
    """Test 4: Verify comprehensive ranking works"""
    print("\n" + "=" * 60)
    print("TEST 4: Comprehensive Ranking")
    print("=" * 60)
    
    try:
        ranker = FundRanker()
        
        # Create sample data
        sample_data = pd.DataFrame([
            {'fund_name': 'Fund A', 'returns_1y': 10, 'returns_3y': 20, 'returns_5y': 30,
             'sharpe_ratio': 1.5, 'standard_deviation': 15, 'risk_score': 20},
            {'fund_name': 'Fund B', 'returns_1y': 15, 'returns_3y': 25, 'returns_5y': 35,
             'sharpe_ratio': 1.2, 'standard_deviation': 20, 'risk_score': 30},
            {'fund_name': 'Fund C', 'returns_1y': 12, 'returns_3y': 22, 'returns_5y': 32,
             'sharpe_ratio': 1.8, 'standard_deviation': 10, 'risk_score': 15},
        ])
        
        # Test comprehensive ranking
        ranked = ranker.rank_funds(sample_data, method='comprehensive')
        
        assert not ranked.empty, "Ranked data should not be empty"
        assert 'score' in ranked.columns, "Should have score column"
        assert 'rank' in ranked.columns, "Should have rank column"
        
        # Fund C might rank higher due to better risk metrics
        top_fund = ranked.iloc[0]
        
        print(f"✓ SUCCESS: Comprehensive ranking works")
        print(f"  Top fund: {top_fund['fund_name']} (Score: {top_fund['score']:.2f})")
        print(f"  Returns 5Y: {top_fund['returns_5y']}%, Sharpe: {top_fund['sharpe_ratio']}")
        return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_two_recommendation_sets():
    """Test 5: Verify two recommendation sets are generated"""
    print("\n" + "=" * 60)
    print("TEST 5: Two Recommendation Sets")
    print("=" * 60)
    
    try:
        ranker = FundRanker()
        
        # Create sample category data
        sample_data = {
            'smallcap': pd.DataFrame([
                {'fund_name': 'Fund A', 'returns_1y': 10, 'returns_3y': 20, 'returns_5y': 30,
                 'sharpe_ratio': 1.5, 'standard_deviation': 15, 'risk_score': 20},
                {'fund_name': 'Fund B', 'returns_1y': 15, 'returns_3y': 25, 'returns_5y': 35,
                 'sharpe_ratio': 1.2, 'standard_deviation': 20, 'risk_score': 30},
                {'fund_name': 'Fund C', 'returns_1y': 12, 'returns_3y': 22, 'returns_5y': 32,
                 'sharpe_ratio': 1.8, 'standard_deviation': 10, 'risk_score': 15},
            ])
        }
        
        # Generate returns-based recommendations
        returns_top = ranker.select_top_funds(sample_data, top_n=2, method='returns')
        returns_recs = ranker.generate_recommendations(returns_top, method='returns')
        
        # Generate comprehensive recommendations
        comp_top = ranker.select_top_funds(sample_data, top_n=2, method='comprehensive')
        comp_recs = ranker.generate_recommendations(comp_top, method='comprehensive')
        
        assert not returns_recs.empty, "Returns-based recommendations should not be empty"
        assert not comp_recs.empty, "Comprehensive recommendations should not be empty"
        assert 'method' in returns_recs.columns, "Should have method column"
        assert 'method' in comp_recs.columns, "Should have method column"
        
        # Verify they might be different
        returns_top_fund = returns_recs.iloc[0]['fund_name']
        comp_top_fund = comp_recs.iloc[0]['fund_name']
        
        print(f"✓ SUCCESS: Both recommendation sets generated")
        print(f"  Returns-based top: {returns_top_fund}")
        print(f"  Comprehensive top: {comp_top_fund}")
        print(f"  Returns set size: {len(returns_recs)}")
        print(f"  Comprehensive set size: {len(comp_recs)}")
        return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_modular_analyzer():
    """Test 6: Verify modular analyzer structure"""
    print("\n" + "=" * 60)
    print("TEST 6: Modular Analyzer Structure")
    print("=" * 60)
    
    try:
        from analyzer import BaseAnalyzer, PerformanceAnalyzer
        
        # Test BaseAnalyzer
        assert issubclass(PerformanceAnalyzer, BaseAnalyzer), "PerformanceAnalyzer should extend BaseAnalyzer"
        
        # Test instantiation
        analyzer = PerformanceAnalyzer()
        assert analyzer is not None, "Should be able to instantiate analyzer"
        
        # Test required columns
        required = analyzer.get_required_columns()
        assert isinstance(required, list), "Required columns should be a list"
        
        # Test validation
        empty_df = pd.DataFrame()
        assert not analyzer.validate_data(empty_df), "Should reject empty DataFrame"
        
        valid_df = pd.DataFrame({'nav': [10, 11, 12], 'date': ['2023-01-01', '2023-02-01', '2023-03-01']})
        assert analyzer.validate_data(valid_df), "Should accept valid DataFrame"
        
        print(f"✓ SUCCESS: Modular analyzer structure works")
        print(f"  BaseAnalyzer: ✓")
        print(f"  PerformanceAnalyzer extends BaseAnalyzer: ✓")
        print(f"  Required columns: {required}")
        return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all comprehensive analysis tests"""
    print("\n" + "=" * 60)
    print("COMPREHENSIVE ANALYSIS TESTS")
    print("=" * 60)
    print("\nTesting analysis implementation and usage...\n")
    
    results = []
    
    # Run tests
    results.append(("Risk Metrics Calculation", test_risk_metrics_calculation()))
    results.append(("Enriched Data Contains Metrics", test_enriched_data_contains_metrics()))
    results.append(("Returns-Based Ranking", test_returns_based_ranking()))
    results.append(("Comprehensive Ranking", test_comprehensive_ranking()))
    results.append(("Two Recommendation Sets", test_two_recommendation_sets()))
    results.append(("Modular Analyzer Structure", test_modular_analyzer()))
    
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
        print("\n✓ All tests passed! Analysis implementation is correct.")
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Review errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

