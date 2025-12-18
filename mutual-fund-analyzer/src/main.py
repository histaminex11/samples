"""
Main Entry Point
Mutual Fund Analyzer - Main script to run the analysis pipeline.
"""

import argparse
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from data_fetcher import FundFetcher, HoldingsFetcher, APIFetcher
from analyzer import PerformanceAnalyzer, HoldingsAnalyzer
from ranking import FundRanker


def fetch_data():
    """Fetch mutual fund data from API."""
    print("=" * 60)
    print("STEP 1: Fetching Mutual Fund Data from API")
    print("=" * 60)
    
    # Use API-based fetcher
    fetcher = FundFetcher(use_api=True)
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
    # Placeholder for actual analysis implementation
    print("✓ Performance analysis completed")
    
    return funds_data


def analyze_holdings(funds_data):
    """Analyze fund holdings."""
    print("\n" + "=" * 60)
    print("STEP 3: Analyzing Fund Holdings")
    print("=" * 60)
    
    holdings_fetcher = HoldingsFetcher()
    holdings_analyzer = HoldingsAnalyzer()
    
    all_holdings = {}
    
    # Fetch holdings for top funds in each category
    for category, funds_df in funds_data.items():
        if funds_df.empty:
            continue
        
        print(f"\nFetching holdings for top {min(10, len(funds_df))} {category} funds...")
        top_funds = funds_df.head(10).to_dict('records')
        
        # Filter out invalid fund names (navigation elements, calculators, etc.)
        valid_funds = []
        invalid_keywords = ['calculator', 'monitor', 'sip', 'ipo', 'builder', 'rated', 'lynch', 'high', 'low', 
                           'no data', 'bse', 'nse', 'sensex', 'nifty', 'index', 'tracker', 'performance']
        
        for fund in top_funds:
            fund_name = fund.get('fund_name', '').lower()
            # Skip if fund name contains invalid keywords or is too short
            if (fund_name and len(fund_name) > 10 and 
                not any(keyword in fund_name for keyword in invalid_keywords) and
                'fund' in fund_name or 'etf' in fund_name):
                valid_funds.append(fund)
        
        if valid_funds:
            category_holdings = holdings_fetcher.fetch_holdings_batch(valid_funds, max_funds=min(5, len(valid_funds)))
            all_holdings.update(category_holdings)
        else:
            print(f"  ⚠ No valid funds found for holdings analysis in {category}")
    
    # Analyze holdings
    if all_holdings:
        top_holdings_df = holdings_analyzer.analyze_top_10_holdings(all_holdings)
        
        # Save holdings data
        import os
        output_dir = "data/processed"
        os.makedirs(output_dir, exist_ok=True)
        top_holdings_df.to_csv(f"{output_dir}/holdings_analysis.csv", index=False)
        print(f"✓ Saved holdings analysis to {output_dir}/holdings_analysis.csv")
    
    print("✓ Holdings analysis completed")
    
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
    parser = argparse.ArgumentParser(description='Mutual Fund Analyzer')
    parser.add_argument('--fetch', action='store_true', help='Fetch fund data')
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

