# Mutual Fund Analyzer

A comprehensive tool to analyze mutual funds, evaluate their performance, and identify the best investment opportunities across different fund categories.

## 🎯 Project Goals

1. **Fetch Top 100 Mutual Funds** from internet sources across categories:
   - Small Cap Funds
   - Mid Cap Funds
   - Large Cap Funds
   - Index Funds
   - ELSS (Equity Linked Savings Scheme)
   - And more categories

2. **Analyze Mutual Fund Performance** - Historical returns, risk metrics, Sharpe ratio, etc.

3. **Analyze Current Stock Holdings** - Understand what stocks each fund holds

4. **Analyze Top 10 Holdings** - Deep dive into the most significant positions in each fund

5. **Select Top 3 Funds** from each category for potential investment

6. **Maximize Profits/Growth** - Data-driven recommendations for optimal investment strategy

## 📁 Project Structure

```
mutual-fund-analyzer/
├── src/
│   ├── data_fetcher/      # Modules to fetch fund data from various sources
│   ├── analyzer/          # Performance and holdings analysis modules
│   ├── ranking/           # Fund ranking and selection logic
│   └── utils/             # Utility functions and helpers
├── data/
│   ├── raw/               # Raw fetched data
│   └── processed/         # Processed and cleaned data
├── config/                # Configuration files
├── tests/                 # Unit and integration tests
└── requirements.txt       # Python dependencies
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mutual-fund-analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the project:
```bash
# Edit config/config.yaml with your settings
```

### Usage

```bash
# Fetch mutual fund data
python src/main.py --fetch

# Analyze funds
python src/main.py --analyze

# Get top recommendations
python src/main.py --recommend
```

## 📊 Features

### Data Fetching
- Scrape mutual fund data from multiple sources
- Support for various fund categories
- Historical data collection

### Performance Analysis
- Return calculations (1Y, 3Y, 5Y, 10Y)
- Risk metrics (Standard Deviation, Beta, Sharpe Ratio)
- Category comparison
- Benchmark comparison

### Holdings Analysis
- Current portfolio composition
- Top 10 holdings analysis
- Sector allocation
- Stock-level performance tracking

### Ranking & Selection
- Multi-factor scoring system
- Category-wise top 3 selection
- Risk-adjusted returns consideration
- Diversification analysis

## 🔧 Configuration

Edit `config/config.yaml` to customize:
- Data sources
- Analysis parameters
- Ranking weights
- Output formats

## 📈 Output

The tool generates:
- CSV reports with fund rankings
- JSON data files
- Visual charts and graphs
- Investment recommendations report

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is for educational and research purposes.

---

**Created with Cursor AI**

