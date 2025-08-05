import yfinance as yf
from datetime import datetime, timedelta

def fetch_market_summary():
    tickers = {
        "S&P 500": "^GSPC",
        "NASDAQ": "^IXIC",
        "Dow Jones": "^DJI"
    }
    data = {}
    end = datetime.now()
    start = end - timedelta(days=2)
    
    for name, symbol in tickers.items():
        df = yf.download(symbol, start=start, end=end)
        if not df.empty:
            latest = df.iloc[-1]
            change = latest['Close'] - df.iloc[-2]['Close']
            pct = (change / df.iloc[-2]['Close']) * 100
            data[name] = {
                "close": latest['Close'],
                "change": round(change, 2),
                "pct": round(pct, 2)
            }
    return data
