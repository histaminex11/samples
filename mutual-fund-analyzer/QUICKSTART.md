# Quick Start Guide

## Installation

### Option 1: Automated Setup (Recommended)

```bash
./setup.sh
```

This will:
- Check Python version
- Create a virtual environment named `vmfanalyzer`
- Install all dependencies
- Create necessary directories

### Option 2: Manual Setup

```bash
# Create virtual environment
python3 -m venv vmfanalyzer

# Activate virtual environment
source vmfanalyzer/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Activate Virtual Environment

Always activate the virtual environment first:

```bash
source vmfanalyzer/bin/activate
```

### 1. Fetch Mutual Fund Data

Fetch funds from MF API (api.mfapi.in):

```bash
python src/main.py --fetch
```

This will:
- Fetch all mutual funds from MF API
- Automatically categorize funds (smallcap, midcap, largecap, index_funds, elss, hybrid, sectoral)
- Note: Debt funds excluded by default (can be enabled in config.yaml)
- Calculate performance metrics (1Y, 3Y, 5Y, 10Y returns)
- Save raw data to `data/raw/` directory
- Create CSV files for each category

### 2. Analyze Funds

Analyze performance metrics:

```bash
python src/main.py --analyze
```

This requires fetched data first. It will:
- Analyze fund performance metrics (already calculated during fetch)
- Note: Holdings analysis is skipped (not available via MF API)

### 3. Generate Recommendations

Get top 5 funds from each category (configurable):

```bash
python src/main.py --recommend
```

This will:
- Rank funds based on multiple factors (returns, consistency, risk)
- Select top 5 from each category (configurable in config.yaml)
- Generate recommendations report
- Save to `data/processed/recommendations.csv` and `.xlsx`

### 4. Run Everything

Run the complete pipeline:

```bash
python src/main.py --all
```

### 5. Display Recommendations

View formatted recommendations:

```bash
python show_recommendations.py
```

## Output Files

After running the analyzer, you'll find:

- **Raw Data**: `data/raw/all_funds.csv` - All fetched funds
- **Category Data**: `data/raw/funds_by_category/{category}_funds.csv` - Category-wise fund data
- **Recommendations**: `data/processed/recommendations.csv` - Top fund recommendations
- **Excel Report**: `data/processed/recommendations.xlsx` - Excel format recommendations
- **Summary**: `RECOMMENDATIONS.md` - Markdown summary of top recommendations

## Configuration

Edit `config/config.yaml` to customize:

- **Categories**: Fund categories to analyze (smallcap, midcap, largecap, etc.)
- **Top Funds**: Number of top funds per category (default: 100)
- **Ranking Weights**: Adjust scoring weights for fund selection
- **Performance Periods**: Years to analyze (1, 3, 5, 10)
- **Output Formats**: CSV, JSON, Excel

## Troubleshooting

### Import Errors

If you get import errors:
```bash
source vmfanalyzer/bin/activate
pip install -r requirements.txt
```

### Virtual Environment Not Activated

Always activate the virtual environment:
```bash
source vmfanalyzer/bin/activate
```

### Network Issues

If you encounter API timeout errors:
- Check internet connection
- The script includes rate limiting to respect API constraints
- Wait a few minutes and retry

### No Data Retrieved

If no funds are fetched:
- Check if `api.mfapi.in` is accessible
- Verify your internet connection
- Check the console output for error messages

## Example Output

```
============================================================
STEP 1: Fetching Mutual Fund Data from MF API
============================================================
Fetching all mutual funds from API...
✓ Fetched 37325 funds from API
Categorizing funds...
  ✓ smallcap: 136 funds
  ✓ midcap: 211 funds
  ✓ largecap: 109 funds
  ✓ index_funds: 691 funds
  ✓ elss: 92 funds
  ✓ hybrid: 716 funds
  ✓ debt: 2102 funds (excluded from processing by default)
  ✓ sectoral: 257 funds

✓ Fetched funds for 8 categories

============================================================
STEP 4: Generating Recommendations
============================================================
✓ Selected top 5 funds for smallcap
✓ Selected top 5 funds for midcap
...

✓ Generated recommendations for 24 funds
✓ Saved to data/processed/recommendations.csv
```

## Next Steps

1. Review the recommendations in `data/processed/recommendations.csv`
2. Check `RECOMMENDATIONS.md` for a formatted summary
3. Adjust ranking weights in `config/config.yaml` based on your preferences
4. Run regularly to get updated fund data and performance metrics

## Data Source

This project uses **MF API (api.mfapi.in)** exclusively:
- **All Funds**: `https://api.mfapi.in/mf`
- **Historical NAV**: `https://api.mfapi.in/mf/{schemeCode}`

No web scraping is performed. All data comes from the official MF API.
