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
   - Debt Funds
   - Sectoral Funds

2. **Analyze Mutual Fund Performance** - Historical returns (1Y, 3Y, 5Y, 10Y), risk metrics, Sharpe ratio, etc.

3. **Select Top 3 Funds** from each category for potential investment

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

# Generate top 3 recommendations per category
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
- Risk metrics (Standard Deviation, Beta, Sharpe Ratio)
- Category-wise comparison
- Performance enrichment for top funds

### Ranking & Selection
- Multi-factor scoring system
- Category-wise top 3 selection
- Risk-adjusted returns consideration
- Generates CSV and Excel reports

## 🔧 Configuration

Edit `config/config.yaml` to customize:
- Fund categories to analyze
- Number of top funds per category
- Performance periods to analyze
- Ranking weights for fund selection
- Output formats

## 📈 Output

The tool generates:
- `data/raw/all_funds.csv` - All fetched funds
- `data/raw/funds_by_category/` - Category-wise fund data
- `data/processed/recommendations.csv` - Top 3 recommendations per category
- `data/processed/recommendations.xlsx` - Excel format recommendations
- `RECOMMENDATIONS.md` - Summary document with top recommendations

## 📝 Notes

- **Holdings Analysis**: Holdings data is not available via MF API. This feature is currently skipped but can be added later using other data sources.
- **Data Source**: This project exclusively uses the MF API (`api.mfapi.in`) for data fetching. No web scraping is performed.
- **Rate Limiting**: The API fetcher includes rate limiting to respect API constraints and avoid overwhelming the service.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is for educational and research purposes.

---

**Created with Cursor AI**
