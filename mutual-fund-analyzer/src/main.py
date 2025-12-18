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


def analyze_performance(funds_data):
    """Analyze mutual fund performance."""
    print("\n" + "=" * 60)
    print("STEP 2: Analyzing Fund Performance")
    print("=" * 60)
    
    analyzer = PerformanceAnalyzer()
    # Performance metrics are already calculated during data fetching
    # Additional analysis can be added here if needed
    print("✓ Performance analysis completed")
    
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
    """Generate investment recommendations."""
    print("\n" + "=" * 60)
    print("STEP 4: Generating Recommendations")
    print("=" * 60)
    
    ranker = FundRanker()
    top_funds = ranker.select_top_funds(funds_data, top_n=3)
    recommendations = ranker.generate_recommendations(top_funds)
    
    # Save recommendations
    output_dir = "data/processed"
    os.makedirs(output_dir, exist_ok=True)
    recommendations.to_csv(f"{output_dir}/recommendations.csv", index=False)
    recommendations.to_excel(f"{output_dir}/recommendations.xlsx", index=False)
    
    print(f"\n✓ Generated recommendations for {len(recommendations)} funds")
    print(f"✓ Saved to {output_dir}/recommendations.csv")
    
    return recommendations


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
        funds_data = analyze_performance(funds_data)
        funds_data = analyze_holdings(funds_data)
    
    if args.all or args.recommend:
        if not funds_data:
            print("No fund data available. Run with --fetch first.")
            return
        recommendations = generate_recommendations(funds_data)
        print("\n" + "=" * 60)
        print("TOP RECOMMENDATIONS")
        print("=" * 60)
        print(recommendations.to_string())


if __name__ == "__main__":
    main()
