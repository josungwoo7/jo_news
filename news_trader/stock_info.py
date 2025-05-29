import yfinance as yf

def get_stock_info(ticker):
    stock = yf.Ticker(ticker)
    try:
        info = stock.info
    except Exception as e:
        # 404 등 에러 발생 시 None 반환
        return {
            "price": None,
            "pe_ratio": None,
            "market_cap": None,
            "info": None
        }
    price = info.get("regularMarketPrice")
    pe_ratio = info.get("trailingPE")
    market_cap = info.get("marketCap")
    return {
        "price": price,
        "pe_ratio": pe_ratio,
        "market_cap": market_cap,
        "info": info
    }

if __name__ == "__main__":
    print(get_stock_info("AAPL")) 