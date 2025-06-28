"""
price_agent.py

This agent retrieves real-time stock price data using yfinance,
checks alert thresholds, returns JSON-compatible output,
and can display results in Streamlit.
"""

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import time

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
    data = yf.download(ticker, period=period, interval=interval, progress=False)
    return data

def check_alert(data: pd.DataFrame, threshold_percent: float) -> bool:
    """
    Check if the stock price has changed beyond a threshold.

    Args:
        data (pd.DataFrame): Stock price data.
        threshold_percent (float): Threshold in percentage.

    Returns:
        bool: True if alert condition met, False otherwise.
    """
    if data.empty:
        return False

    # Ensure scalar values
    first = float(data['Close'].iloc[0])
    last = float(data['Close'].iloc[-1])
    change = ((last - first) / first) * 100

    print(f"[INFO] Price change: {change:.2f}%")
    return abs(change) >= threshold_percent


def price_to_json(data: pd.DataFrame) -> dict:
    """
    Convert price data to JSON-compatible dict.

    Args:
        data (pd.DataFrame): Stock price data.

    Returns:
        dict: JSON-compatible representation.
    """
    return data.reset_index().to_dict(orient="records")

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

def run_streamlit():
    """
    Run Streamlit app for interactive usage.
    """
    st.title("Agentic Finance - Price Agent")
    ticker = st.text_input("Stock ticker (e.g., AAPL):", value="AAPL")
    threshold = st.number_input("Alert threshold (% change):", min_value=0.0, value=5.0)

    if st.button("Fetch and Check"):
        try:
            data = fetch_price(TICKER)
            time.sleep(3)  # Wait 3 seconds before any next API call
            if not data.empty:
                triggered = check_alert(data, THRESHOLD)
                print(f"Alert triggered: {triggered}")
                print("JSON sample:", price_to_json(data)[:2])
                plot_price(data, TICKER)
            else:
                print("[ERROR] No data fetched.")
        except Exception as e:
            print(f"[ERROR] Exception occurred: {e}")
            print("Consider waiting a few seconds or changing the ticker.")

        st.line_chart(data['Close'])

        alert_triggered = check_alert(data, threshold)
        if alert_triggered:
            st.warning(f"⚠️ Alert: price change exceeded {threshold}%")
        else:
            st.success(f"Price change is within {threshold}%")

        st.json(price_to_json(data))

if __name__ == "__main__":
    # For CLI testing
    TICKER = "MSFT"
    THRESHOLD = 5.0

    data = fetch_price(TICKER)
    if not data.empty:
        triggered = check_alert(data, THRESHOLD)
        print(f"Alert triggered: {triggered}")
        print("JSON sample:", price_to_json(data)[:2])
        plot_price(data, TICKER)
    else:
        print("[ERROR] No data fetched.")

    # Uncomment to run Streamlit directly when executing the file
    # run_streamlit()
