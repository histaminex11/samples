# Implementation Details

## Data Fetching Implementation

### Web Scraping Sources

The project implements web scraping for three major Indian mutual fund data sources:

#### 1. Moneycontrol
- **URL Pattern**: `https://www.moneycontrol.com/mutual-funds/{category}-funds`
- **Categories Supported**: All configured categories
- **Data Extracted**:
  - Fund names
  - NAV (Net Asset Value)
  - Returns (1Y, 3Y, 5Y)
  - AUM (Assets Under Management)

#### 2. Value Research
- **URL Pattern**: `https://www.valueresearchonline.com/funds/selector/category/{category}`
- **Categories Supported**: All configured categories
- **Data Extracted**:
  - Fund names
  - NAV
  - Historical returns
  - Performance metrics

#### 3. AMFI (Association of Mutual Funds in India)
- **Data Source**: Official AMFI NAV data
- **URL**: `https://www.amfiindia.com/spages/NAVAll.txt`
- **Format**: Text file with NAV data
- **Data Extracted**:
  - Fund names
  - Current NAV
  - Scheme codes

### Holdings Fetching

The `HoldingsFetcher` class fetches:
- Current stock holdings for each fund
- Top 10 holdings with weights
- Sector allocation
- Stock quantities

### Features Implemented

1. **Multi-Source Aggregation**: Combines data from multiple sources
2. **Deduplication**: Removes duplicate funds based on name matching
3. **Rate Limiting**: Respects website rate limits (2 seconds between requests)
4. **Error Handling**: Graceful error handling with retries
5. **Data Validation**: Parses and validates numeric values
6. **Category Mapping**: Maps internal categories to source-specific URLs

### Usage Example

```python
from src.data_fetcher import FundFetcher, HoldingsFetcher

# Fetch funds
fetcher = FundFetcher()
all_funds = fetcher.fetch_all_categories()

# Fetch holdings
holdings_fetcher = HoldingsFetcher()
holdings = holdings_fetcher.fetch_top_10_holdings("Fund Name")
```

### Notes

- Web scraping may need adjustments if website structures change
- Some sources may require authentication or have anti-scraping measures
- Consider using official APIs when available
- Always respect robots.txt and terms of service

