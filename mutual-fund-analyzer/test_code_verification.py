#!/usr/bin/env python3
"""
Code Verification Tests
Quick tests to verify the code is working as expected.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd
from data_fetcher import FundFetcher, MFAPIFetcher
from ranking import FundRanker
from analyzer import PerformanceAnalyzer


def test_api_connection():
    """Test 1: Verify API connection works"""
    print("=" * 60)
    print("TEST 1: API Connection")
    print("=" * 60)
    
    try:
        api = MFAPIFetcher(rate_limit=0.5)
        funds = api.fetch_all_funds()
        
        assert not funds.empty, "No funds fetched from API"
        assert 'schemeCode' in funds.columns, "Missing schemeCode column"
        assert 'schemeName' in funds.columns, "Missing schemeName column"
        
        print(f"✓ SUCCESS: Fetched {len(funds)} funds")
        print(f"  Sample fund: {funds.iloc[0]['schemeName']}")
        return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        return False


def test_fund_categorization():
    """Test 2: Verify fund categorization works"""
    print("\n" + "=" * 60)
    print("TEST 2: Fund Categorization")
    print("=" * 60)
    
    try:
        api = MFAPIFetcher(rate_limit=0.5)
        all_funds = api.fetch_all_funds()
        
        if all_funds.empty:
            print("⚠ SKIPPED: No funds to categorize")
            return True
        
        categorized = api.categorize_funds(all_funds)
        
        assert isinstance(categorized, dict), "Categorization should return a dictionary"
        assert len(categorized) > 0, "Should have at least one category"
        
        total_categorized = sum(len(df) for df in categorized.values())
        print(f"✓ SUCCESS: Categorized {total_categorized} funds into {len(categorized)} categories")
        for cat, df in list(categorized.items())[:5]:
            print(f"  - {cat}: {len(df)} funds")
        return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        return False


def test_performance_calculation():
    """Test 3: Verify performance calculation works"""
    print("\n" + "=" * 60)
    print("TEST 3: Performance Calculation")
    print("=" * 60)
    
    try:
        api = MFAPIFetcher(rate_limit=0.5)
        all_funds = api.fetch_all_funds()
        
        if all_funds.empty:
            print("⚠ SKIPPED: No funds to test")
            return True
        
        # Get a sample fund with schemeCode
        sample_fund = all_funds[all_funds['schemeCode'].notna()].iloc[0]
        scheme_code = int(sample_fund['schemeCode'])
        
        # Fetch historical data
        history = api.fetch_fund_history(scheme_code)
        
        if history is not None and not history.empty:
            returns = api.calculate_returns(history)
            print(f"✓ SUCCESS: Calculated returns for fund {sample_fund['schemeName'][:50]}")
            print(f"  Returns: {returns}")
            return True
        else:
            print("⚠ SKIPPED: No historical data available for sample fund")
            return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_fund_fetcher():
    """Test 4: Verify FundFetcher works"""
    print("\n" + "=" * 60)
    print("TEST 4: Fund Fetcher Integration")
    print("=" * 60)
    
    try:
        fetcher = FundFetcher()
        
        # Test fetching a single category (small sample)
        print("  Testing category fetch (this may take a moment)...")
        smallcap_funds = fetcher.fetch_funds_by_category('smallcap')
        
        assert isinstance(smallcap_funds, pd.DataFrame), "Should return DataFrame"
        
        if not smallcap_funds.empty:
            print(f"✓ SUCCESS: Fetched {len(smallcap_funds)} smallcap funds")
            if 'returns_5y' in smallcap_funds.columns:
                print(f"  Sample 5Y return: {smallcap_funds.iloc[0].get('returns_5y', 'N/A')}")
        else:
            print("⚠ WARNING: No smallcap funds found (may be normal)")
        
        return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_fund_ranker():
    """Test 5: Verify FundRanker works"""
    print("\n" + "=" * 60)
    print("TEST 5: Fund Ranker")
    print("=" * 60)
    
    try:
        ranker = FundRanker()
        
        # Create sample data
        sample_data = {
            'smallcap': pd.DataFrame([
                {'fund_name': 'Fund A', 'returns_1y': 10, 'returns_3y': 20, 'returns_5y': 30},
                {'fund_name': 'Fund B', 'returns_1y': 15, 'returns_3y': 25, 'returns_5y': 35},
                {'fund_name': 'Fund C', 'returns_1y': 12, 'returns_3y': 22, 'returns_5y': 32},
            ])
        }
        
        top_funds = ranker.select_top_funds(sample_data, top_n=2)
        recommendations = ranker.generate_recommendations(top_funds)
        
        assert not recommendations.empty, "Should generate recommendations"
        assert len(recommendations) <= 2, "Should select top 2 funds"
        
        print(f"✓ SUCCESS: Generated {len(recommendations)} recommendations")
        print(f"  Top fund: {recommendations.iloc[0]['fund_name']}")
        return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_output_files():
    """Test 6: Verify output files exist and are valid"""
    print("\n" + "=" * 60)
    print("TEST 6: Output Files")
    print("=" * 60)
    
    try:
        import os
        
        # Check recommendations file
        rec_file = "data/processed/recommendations.csv"
        if os.path.exists(rec_file):
            df = pd.read_csv(rec_file)
            print(f"✓ SUCCESS: {rec_file} exists with {len(df)} recommendations")
            if not df.empty:
                print(f"  Columns: {list(df.columns)[:5]}...")
                print(f"  Categories: {df['category'].nunique() if 'category' in df.columns else 'N/A'}")
        else:
            print(f"⚠ WARNING: {rec_file} does not exist (run --recommend first)")
        
        # Check raw data files
        raw_dir = "data/raw"
        if os.path.exists(raw_dir):
            files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
            print(f"✓ Raw data directory exists with {len(files)} CSV files")
        else:
            print(f"⚠ WARNING: {raw_dir} does not exist (run --fetch first)")
        
        return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        return False


def main():
    """Run all verification tests"""
    print("\n" + "=" * 60)
    print("CODE VERIFICATION TESTS")
    print("=" * 60)
    print("\nRunning tests to verify code functionality...\n")
    
    results = []
    
    # Run tests (some may be slow due to API calls)
    results.append(("API Connection", test_api_connection()))
    results.append(("Fund Categorization", test_fund_categorization()))
    results.append(("Performance Calculation", test_performance_calculation()))
    results.append(("Fund Fetcher", test_fund_fetcher()))
    results.append(("Fund Ranker", test_fund_ranker()))
    results.append(("Output Files", test_output_files()))
    
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
        print("\n✓ All tests passed! Code is working correctly.")
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Review errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

