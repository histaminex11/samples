# Mutual Fund Analyzer

A comprehensive tool to analyze mutual funds, evaluate their performance, and identify the best investment opportunities across different fund categories.

**Uses MF API (api.mfapi.in) for all data fetching.**

## 🎯 Project Goals

1. **Fetch Top 100 Mutual Funds** from MF API across categories:
   - Small Cap Funds
   - Mid Cap Funds
   - Large Cap Funds
   - Index Funds
   - ELSS (Equity Linked Savings Scheme)
   - Hybrid Funds
   - Sectoral Funds
   - Note: Debt funds excluded (800+ funds, configurable)

2. **Analyze Mutual Fund Performance** - Historical returns (1Y, 3Y, 5Y, 10Y), risk metrics, Sharpe ratio, consistency analysis, benchmark comparison, etc.

3. **Select Top 5 Funds** from each category for potential investment (configurable in config.yaml)

4. **Maximize Profits/Growth** - Data-driven recommendations for optimal investment strategy

## 📁 Project Structure

```
mutual-fund-analyzer/
├── src/
│   ├── data_fetcher/      # MF API data fetching modules
│   │   ├── mf_api_fetcher.py  # Main API fetcher for api.mfapi.in
│   │   └── fund_fetcher.py    # Orchestrates data fetching
│   ├── analyzer/          # Performance analysis modules
│   ├── ranking/           # Fund ranking and selection logic
│   └── main.py            # Main entry point
├── data/
│   ├── raw/               # Raw fetched data
│   └── processed/         # Processed data and recommendations
├── config/                # Configuration files
│   └── config.yaml        # Main configuration
├── vmfanalyzer/           # Python virtual environment (created by setup.sh)
├── requirements.txt       # Python dependencies
├── setup.sh               # Setup script to create venv and install dependencies
└── show_recommendations.py # Script to display recommendations
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+ (python3, python3.9, or python3.11)
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mutual-fund-analyzer
```

2. Run the setup script to create virtual environment and install dependencies:
```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Create a virtual environment named `vmfanalyzer`
- Activate it
- Install all required dependencies from `requirements.txt`

3. Activate the virtual environment (if not already activated):
```bash
source vmfanalyzer/bin/activate
```

### Usage

```bash
# Activate virtual environment first
source vmfanalyzer/bin/activate

# Run the complete analysis pipeline (fetch, analyze, recommend)
python src/main.py --all

# Or run individual steps:
# Fetch mutual fund data from MF API
python src/main.py --fetch

# Analyze funds (performance metrics are calculated during fetch)
python src/main.py --analyze

# Generate top 5 recommendations per category (configurable)
python src/main.py --recommend

# Display recommendations in a formatted way
python show_recommendations.py
```

## 📊 Features

### Data Fetching (MF API)
- Fetches all mutual funds from `api.mfapi.in`
- Automatic categorization based on fund names
- Historical NAV data fetching for performance calculation
- Calculates returns for 1Y, 3Y, 5Y, 10Y periods
- Rate limiting to respect API constraints

### Performance Analysis
- Return calculations (1Y, 3Y, 5Y, 10Y)
- Risk metrics (Standard Deviation, Sharpe Ratio, Max Drawdown, Risk Score)
- Consistency analysis (Consistency Score, Rolling Consistency, Coefficient of Variation)
- Benchmark comparison (Alpha, Tracking Error, Benchmark Outperformance)
- Category-wise comparison
- Performance enrichment for top funds

### Ranking & Selection
- Multi-factor scoring system
- Two ranking methods:
  - Returns-based (pure historical performance)
  - Comprehensive (returns + risk + consistency + benchmark)
- Category-wise top 5 selection (configurable)
- Risk-adjusted returns consideration
- Generates CSV and Excel reports

## 🔧 Configuration

Edit `config/config.yaml` to customize:
- Fund categories to analyze (debt funds excluded by default)
- Number of top funds per category (default: 100)
- Number of top recommendations per category (default: 5)
- Performance periods to analyze
- Analyzer selection flags (enable/disable specific analyzers)
- Ranking weights for fund selection
- Output formats

### Analyzer Selection
You can enable/disable specific analyzers via config flags:
- `performance_analyzer`: Returns and risk metrics (default: true)
- `consistency_analyzer`: Consistency analysis (default: true)
- `benchmark_analyzer`: Benchmark comparison (default: true)
- `holdings_analyzer`: Holdings analysis (default: false - not available via MF API)

## 📈 Output

The tool generates:
- `data/raw/all_funds.csv` - All fetched funds
- `data/raw/funds_by_category/` - Category-wise fund data
- `data/processed/recommendations_returns_based.csv` - Returns-based recommendations (top 5 per category)
- `data/processed/recommendations_comprehensive.csv` - Comprehensive recommendations (top 5 per category)
- `data/processed/recommendations.csv` - Combined recommendations file
- `data/processed/recommendations_*.xlsx` - Excel format recommendations
- `data/cache/` - Cached data for faster subsequent runs (1-month freshness)
- `RECOMMENDATIONS.md` - Summary document with top recommendations

## 📝 Notes

- **Holdings Analysis**: Holdings data is not available via MF API. This feature is currently disabled but can be added later using other data sources.
- **Data Source**: This project exclusively uses the MF API (`api.mfapi.in`) for data fetching. No web scraping is performed.
- **Caching**: All fetched data is cached for 1 month to balance data freshness with performance. Cache is automatically refreshed after 30 days.
- **Rate Limiting**: The API fetcher includes rate limiting to respect API constraints and avoid overwhelming the service.
- **Debt Funds**: Excluded by default (800+ funds). Can be enabled by adding 'debt' to categories in config.yaml.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is for educational and research purposes.

---

**Created with Cursor AI**
