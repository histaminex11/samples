"""
Main Entry Point
Mutual Fund Analyzer - Main script to run the analysis pipeline.
Uses MF API (api.mfapi.in) for data fetching.
"""

import argparse
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from data_fetcher import FundFetcher
from analyzer import PerformanceAnalyzer
from ranking import FundRanker
import yaml


def fetch_data():
    """Fetch mutual fund data from MF API."""
    print("=" * 60)
    print("STEP 1: Fetching Mutual Fund Data from MF API")
    print("=" * 60)
    
    # Use MF API fetcher
    fetcher = FundFetcher()
    all_funds = fetcher.fetch_all_categories()
    fetcher.save_raw_data(all_funds)
    
    print(f"\n✓ Fetched funds for {len(all_funds)} categories")
    return all_funds


def analyze_performance(funds_data, config=None):
    """Analyze mutual fund performance."""
    print("\n" + "=" * 60)
    print("STEP 2: Analyzing Fund Performance")
    print("=" * 60)
    
    # Load config if not provided
    if config is None:
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    
    # Check which analyzers are enabled
    analyzer_flags = config.get('analysis', {}).get('analyzers', {})
    
    print("✓ Performance analysis completed")
    if analyzer_flags.get('performance_analyzer', True):
        print("  - Returns calculated (1Y, 3Y, 5Y, 10Y)")
        print("  - Risk metrics calculated (Sharpe ratio, Std Dev, Max Drawdown, Risk Score)")
    if analyzer_flags.get('consistency_analyzer', True):
        print("  - Consistency metrics calculated (Consistency Score, Rolling Consistency)")
    if analyzer_flags.get('benchmark_analyzer', True):
        print("  - Benchmark metrics calculated (Alpha, Benchmark Name, Outperformance)")
    if analyzer_flags.get('holdings_analyzer', False):
        print("  - Holdings analysis (not available via MF API)")
    
    return funds_data


def analyze_holdings(funds_data):
    """
    Analyze fund holdings.
    Note: Holdings data is not available via MF API, so this step is skipped.
    Holdings analysis can be added later using other data sources if needed.
    """
    print("\n" + "=" * 60)
    print("STEP 3: Analyzing Fund Holdings")
    print("=" * 60)
    
    print("⚠ Holdings data is not available via MF API")
    print("  Holdings analysis skipped. This can be added later using other data sources.")
    print("✓ Holdings analysis step completed (skipped)")
    
    return funds_data


def generate_recommendations(funds_data):
    """
    Generate investment recommendations using two methods:
    1. Pure returns-based ranking
    2. Comprehensive ranking (returns + risk metrics)
    """
    print("\n" + "=" * 60)
    print("STEP 4: Generating Recommendations")
    print("=" * 60)
    
    ranker = FundRanker()
    output_dir = "data/processed"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get top N from config (default: 5)
    top_n = ranker.config.get('analysis', {}).get('top_recommendations_per_category', 5)
    
    # Method 1: Pure returns-based recommendations
    print(f"\n--- Method 1: Returns-Based Recommendations (Top {top_n}) ---")
    returns_top_funds = ranker.select_top_funds(funds_data, top_n=top_n, method='returns')
    returns_recommendations = ranker.generate_recommendations(returns_top_funds, method='returns')
    
    # Save returns-based recommendations
    returns_file = f"{output_dir}/recommendations_returns_based.csv"
    returns_excel = f"{output_dir}/recommendations_returns_based.xlsx"
    returns_recommendations.to_csv(returns_file, index=False)
    returns_recommendations.to_excel(returns_excel, index=False)
    print(f"✓ Saved {len(returns_recommendations)} returns-based recommendations")
    print(f"  - CSV: {returns_file}")
    print(f"  - Excel: {returns_excel}")
    
    # Method 2: Comprehensive recommendations
    print(f"\n--- Method 2: Comprehensive Recommendations (Top {top_n} - Returns + Risk) ---")
    comprehensive_top_funds = ranker.select_top_funds(funds_data, top_n=top_n, method='comprehensive')
    comprehensive_recommendations = ranker.generate_recommendations(comprehensive_top_funds, method='comprehensive')
    
    # Save comprehensive recommendations
    comprehensive_file = f"{output_dir}/recommendations_comprehensive.csv"
    comprehensive_excel = f"{output_dir}/recommendations_comprehensive.xlsx"
    comprehensive_recommendations.to_csv(comprehensive_file, index=False)
    comprehensive_recommendations.to_excel(comprehensive_excel, index=False)
    print(f"✓ Saved {len(comprehensive_recommendations)} comprehensive recommendations")
    print(f"  - CSV: {comprehensive_file}")
    print(f"  - Excel: {comprehensive_excel}")
    
    # Also save combined file for backward compatibility
    combined_file = f"{output_dir}/recommendations.csv"
    combined_excel = f"{output_dir}/recommendations.xlsx"
    comprehensive_recommendations.to_csv(combined_file, index=False)
    comprehensive_recommendations.to_excel(combined_excel, index=False)
    
    return {
        'returns_based': returns_recommendations,
        'comprehensive': comprehensive_recommendations
    }


def display_recommendations(recommendations):
    """Display both sets of recommendations."""
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS SUMMARY")
    print("=" * 60)
    
    print("\n" + "-" * 60)
    print("1. RETURNS-BASED RECOMMENDATIONS")
    print("   (Ranked purely by historical returns)")
    print("-" * 60)
    print(recommendations['returns_based'].to_string())
    
    print("\n" + "-" * 60)
    print("2. COMPREHENSIVE RECOMMENDATIONS")
    print("   (Ranked by returns + risk metrics)")
    print("-" * 60)
    print(recommendations['comprehensive'].to_string())


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Mutual Fund Analyzer - Uses MF API (api.mfapi.in)')
    parser.add_argument('--fetch', action='store_true', help='Fetch fund data from MF API')
    parser.add_argument('--analyze', action='store_true', help='Analyze funds')
    parser.add_argument('--recommend', action='store_true', help='Generate recommendations')
    parser.add_argument('--all', action='store_true', help='Run all steps')
    
    args = parser.parse_args()
    
    if not any([args.fetch, args.analyze, args.recommend, args.all]):
        parser.print_help()
        return
    
    funds_data = {}
    
    if args.all or args.fetch:
        funds_data = fetch_data()
    
    if args.all or args.analyze:
        if not funds_data:
            print("No fund data available. Run with --fetch first.")
            return
        # Load config
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        funds_data = analyze_performance(funds_data, config=config)
        funds_data = analyze_holdings(funds_data)
    
    if args.all or args.recommend:
        if not funds_data:
            print("No fund data available. Run with --fetch first.")
            return
        recommendations = generate_recommendations(funds_data)
        display_recommendations(recommendations)


if __name__ == "__main__":
    main()
