"""
price_agent.py

This agent retrieves real-time stock price data using yfinance.
"""

import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

def fetch_price(ticker: str, period: str = "1d", interval: str = "5m") -> pd.DataFrame:
    """
    Fetch stock price data for a given ticker.

    Args:
        ticker (str): Stock symbol, e.g., 'AAPL'.
        period (str): Data period, e.g., '1d', '5d', '1mo'.
        interval (str): Data interval, e.g., '1m', '5m', '15m'.

    Returns:
        pd.DataFrame: Stock price data.
    """
    print(f"[INFO] Fetching price data for {ticker} (period={period}, interval={interval})")
    data = yf.download(ticker, period=period, interval=interval, progress=False)
    if data.empty:
        print(f"[WARN] No data returned for {ticker}")
    else:
        print(f"[INFO] Retrieved {len(data)} data points for {ticker}")
    return data

def plot_price(data: pd.DataFrame, ticker: str):
    """
    Plot the stock's closing price.

    Args:
        data (pd.DataFrame): Stock price data.
        ticker (str): Stock symbol for the plot title.
    """
    if data.empty:
        print("[ERROR] No data to plot.")
        return

    plt.figure(figsize=(10, 4))
    plt.plot(data.index, data['Close'], marker='o')
    plt.title(f"{ticker} - Closing Price")
    plt.xlabel("Time")
    plt.ylabel("Price (USD)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Example usage
    TICKER = "AAPL"  # Change this to any stock symbol you like
    price_data = fetch_price(TICKER)
    plot_price(price_data, TICKER)
