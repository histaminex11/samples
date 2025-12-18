# Quick Start Guide

## Installation

### Option 1: Automated Setup (Recommended)

```bash
./setup.sh
```

This will:
- Check Python version
- Optionally create a virtual environment
- Install all dependencies
- Create necessary directories

### Option 2: Manual Setup

```bash
# Install dependencies
pip3 install -r requirements.txt

# Or with user flag if you don't have admin access
pip3 install --user -r requirements.txt
```

## Usage

### 1. Fetch Mutual Fund Data

Fetch top 100 funds from each category:

```bash
python3 src/main.py --fetch
```

This will:
- Scrape data from Moneycontrol, Value Research, and AMFI
- Save raw data to `data/raw/` directory
- Create CSV files for each category

### 2. Analyze Funds

Analyze performance and holdings:

```bash
python3 src/main.py --analyze
```

This requires fetched data first. It will:
- Analyze fund performance metrics
- Fetch and analyze holdings for top funds
- Save analysis to `data/processed/`

### 3. Generate Recommendations

Get top 3 funds from each category:

```bash
python3 src/main.py --recommend
```

This will:
- Rank funds based on multiple factors
- Select top 3 from each category
- Generate recommendations report
- Save to `data/processed/recommendations.csv`

### 4. Run Everything

Run the complete pipeline:

```bash
python3 src/main.py --all
```

## Output Files

After running the analyzer, you'll find:

- **Raw Data**: `data/raw/{category}_funds.csv` - Fetched fund data
- **Holdings**: `data/processed/holdings_analysis.csv` - Stock holdings analysis
- **Recommendations**: `data/processed/recommendations.csv` - Top fund recommendations
- **Excel Report**: `data/processed/recommendations.xlsx` - Excel format recommendations

## Configuration

Edit `config/config.yaml` to customize:

- **Categories**: Add/remove fund categories
- **Data Sources**: Enable/disable specific sources
- **Ranking Weights**: Adjust scoring weights
- **Analysis Parameters**: Change performance periods, risk metrics

## Troubleshooting

### Import Errors

If you get import errors:
```bash
pip3 install -r requirements.txt
```

### Network Issues

The scraper respects rate limits. If you encounter:
- Timeout errors: Check internet connection
- Rate limiting: The script automatically waits between requests
- Blocked requests: Some sites may block automated access

### No Data Retrieved

If no funds are fetched:
- Check if websites are accessible
- Verify category names in config.yaml match source URLs
- Website structures may have changed - update scraper selectors

## Example Output

```
============================================================
STEP 1: Fetching Mutual Fund Data
============================================================

Fetching smallcap funds from multiple sources...
  ✓ Fetched 45 funds from Moneycontrol
  ✓ Fetched 52 funds from Value Research
  ✓ Total unique funds: 87 (from moneycontrol, valueresearch)

✓ Fetched funds for 8 categories

============================================================
STEP 4: Generating Recommendations
============================================================
✓ Selected top 3 funds for smallcap
✓ Selected top 3 funds for midcap
...

✓ Generated recommendations for 24 funds
✓ Saved to data/processed/recommendations.csv
```

## Next Steps

1. Review the recommendations in `data/processed/recommendations.csv`
2. Analyze holdings to understand fund composition
3. Adjust ranking weights in `config/config.yaml` based on your preferences
4. Run regularly to get updated fund data

