# Implementation Details

## Data Fetching Implementation

### MF API (api.mfapi.in)

The project uses the **MF API** exclusively for all data fetching. This is a public API that provides:
- Complete list of all mutual funds in India
- Historical NAV (Net Asset Value) data
- Scheme codes for each fund

#### API Endpoints

1. **All Funds Endpoint**
   - **URL**: `https://api.mfapi.in/mf`
   - **Method**: GET
   - **Returns**: JSON array of all mutual funds with:
     - `schemeCode`: Unique identifier for the fund
     - `schemeName`: Full name of the fund

2. **Historical NAV Endpoint**
   - **URL**: `https://api.mfapi.in/mf/{schemeCode}`
   - **Method**: GET
   - **Returns**: JSON object with:
     - `meta`: Fund metadata
     - `data`: Array of NAV records with date and NAV value

#### Data Processing Flow

1. **Fetch All Funds**: Get complete list from `/mf` endpoint
2. **Categorization**: Automatically categorize funds based on scheme name keywords:
   - Small Cap: "small cap", "smallcap", "small-cap"
   - Mid Cap: "mid cap", "midcap", "mid-cap"
   - Large Cap: "large cap", "largecap", "large-cap"
   - Index Funds: "index", "nifty", "sensex", "etf"
   - ELSS: "elss", "tax saving", "tax-saving"
   - Hybrid: "hybrid", "balanced", "aggressive"
   - Debt: "debt", "income", "gilt", "liquid"
   - Sectoral: "sectoral", "sector", "infrastructure", "technology", etc.

3. **Performance Calculation**: For top funds in each category:
   - Fetch historical NAV data
   - Calculate returns for 1Y, 3Y, 5Y, 10Y periods
   - Calculate risk metrics (standard deviation, Sharpe ratio, etc.)

4. **Data Enrichment**: Add calculated metrics to fund data

### Features Implemented

1. **Automatic Categorization**: Intelligent fund categorization based on scheme names
2. **Rate Limiting**: Respects API constraints (0.5 seconds between requests)
3. **Error Handling**: Graceful error handling with retries for failed requests
4. **Data Validation**: Validates and cleans numeric values
5. **Performance Metrics**: Calculates historical returns and risk-adjusted metrics
6. **Batch Processing**: Efficiently processes large numbers of funds

### Architecture

```
src/data_fetcher/
├── mf_api_fetcher.py    # Core API fetcher and performance calculator
└── fund_fetcher.py      # Orchestrates fetching and categorization
```

### Usage Example

```python
from data_fetcher import FundFetcher, MFAPIFetcher

# Fetch all funds by category
fetcher = FundFetcher()
all_funds = fetcher.fetch_all_categories()

# Or use MFAPIFetcher directly
api_fetcher = MFAPIFetcher(rate_limit=0.5)

# Fetch all funds
all_funds_df = api_fetcher.fetch_all_funds()

# Categorize funds
categorized = api_fetcher.categorize_funds(all_funds_df)

# Get funds for a specific category
smallcap_funds = api_fetcher.fetch_funds_by_category('smallcap', all_funds_df)

# Enrich with performance data
enriched = api_fetcher.enrich_funds_with_performance(smallcap_funds.head(10))
```

### Performance Calculation

The `MFAPIFetcher` calculates:

- **Returns**: 1Y, 3Y, 5Y, 10Y percentage returns
- **Risk Metrics**:
  - Standard Deviation
  - Sharpe Ratio (risk-adjusted returns)
  - Beta (market correlation)
  - Maximum Drawdown

### Data Storage

- **Raw Data**: `data/raw/all_funds.csv` - All fetched funds
- **Category Data**: `data/raw/funds_by_category/{category}_funds.csv`
- **Processed Data**: `data/processed/recommendations.csv` - Top recommendations

### Notes

- **Holdings Data**: Holdings information is not available via MF API. This feature is currently skipped but can be added using other data sources if needed.
- **Rate Limiting**: The API fetcher includes built-in rate limiting to avoid overwhelming the API service.
- **Data Freshness**: NAV data is updated daily. Historical data goes back several years.
- **No Authentication**: The MF API is public and does not require authentication.

### Advantages of MF API Approach

1. **Reliability**: Official API, no dependency on website structure changes
2. **Completeness**: Access to all mutual funds in India
3. **Historical Data**: Rich historical NAV data for performance analysis
4. **No Scraping**: No need to parse HTML or handle anti-scraping measures
5. **Rate Limiting**: Built-in respect for API constraints
6. **Maintainability**: API-based approach is easier to maintain

### Future Enhancements

Potential improvements:
- Add holdings data from other sources
- Implement caching for frequently accessed data
- Add more sophisticated risk metrics
- Implement portfolio optimization algorithms
- Add visualization and reporting features
