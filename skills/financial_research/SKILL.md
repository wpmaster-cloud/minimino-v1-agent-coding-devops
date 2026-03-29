---
name: financial_research
description: "Look up stock prices, company financials, historical market data, and financial summaries. Use when the mission involves stocks, tickers, investments, or financial analysis."
---

# Financial Research skill

Use this skill when the mission involves looking up stock prices, company fundamentals, historical data, or producing financial summaries.

## Setup

Install yfinance once per agent session (cached after first install):

```bash
pip install yfinance
```

## Getting data

Write a python script to `files/` and run it. All data comes from the `yfinance` library.

### Current price

```python
import yfinance as yf
t = yf.Ticker("AAPL")
info = t.info
print(f"Price: {info.get('currentPrice')} {info.get('currency')}")
print(f"Open: {info.get('open')}  High: {info.get('dayHigh')}  Low: {info.get('dayLow')}")
print(f"Volume: {info.get('volume')}")
print(f"Change: {info.get('currentPrice', 0) - info.get('previousClose', 0):.2f}")
```

### Company fundamentals

```python
import yfinance as yf
t = yf.Ticker("AAPL")
info = t.info
print(f"Name: {info.get('longName')}")
print(f"Sector: {info.get('sector')} / {info.get('industry')}")
print(f"Market Cap: {info.get('marketCap')}")
print(f"PE (trailing): {info.get('trailingPE')}  PE (forward): {info.get('forwardPE')}")
print(f"Dividend Yield: {info.get('dividendYield')}")
print(f"52w Range: {info.get('fiftyTwoWeekLow')} - {info.get('fiftyTwoWeekHigh')}")
```

### Historical data

```python
import yfinance as yf
df = yf.Ticker("AAPL").history(period="1mo", interval="1d")
print(df[["Open", "High", "Low", "Close", "Volume"]].to_string())
```

**period** options: `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max`
**interval** options: `1m`, `5m`, `15m`, `30m`, `1h`, `1d`, `1wk`, `1mo`

### Multiple tickers

```python
import yfinance as yf
tickers = yf.Tickers("AAPL MSFT GOOGL")
for symbol, t in tickers.tickers.items():
    info = t.info
    print(f"{symbol}: {info.get('currentPrice')} ({info.get('currency')})")
```

## Workflow

1. **Install** — `pip install yfinance` (once)
2. **Identify tickers** — Map company names to Yahoo Finance symbols (e.g. Tesla → TSLA, Apple → AAPL)
3. **Write script** — Write a python script to `files/finance.py` with the data fetching and analysis
4. **Run** — `python3 files/finance.py`
5. **Analyze** — Add calculations as needed: moving averages, % changes, comparisons
6. **Deliver** — Format as a report, send via Telegram, or save to file

## Guardrails

- Yahoo Finance symbols only. Use `.L` suffix for London, `.T` for Tokyo, etc.
- If a ticker returns empty/error, it may be delisted or misspelled. Try an alternative before reporting stuck.
- Do not provide financial advice. Present data and analysis, not recommendations.
- For large analyses, write the full script to a file rather than using one-liners.
