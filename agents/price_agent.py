"""
price_agent.py

Fetches stock price data using yfinance with a fallback to Finnhub.
Includes delay between API calls to reduce rate-limiting risks.
"""

import yfinance as yf
import pandas as pd
import requests
import time
from dotenv import load_dotenv
import os

# Load API key from .env
load_dotenv()
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

API_CALL_DELAY = 3  # seconds between API calls

def fetch_price_yfinance(ticker: str, period="1d", interval="5m") -> pd.DataFrame:
    """
    Try to fetch price data using yfinance.
    """
    try:
        print(f"[INFO] Attempting yfinance for {ticker}")
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        time.sleep(API_CALL_DELAY)  # delay after call
        if data.empty:
            print("[WARN] yfinance returned no data.")
            return None
        print("[INFO] yfinance data retrieved.")
        return data
    except Exception as e:
        print(f"[ERROR] yfinance exception: {e}")
        time.sleep(API_CALL_DELAY)
        return None

def fetch_price_finnhub(ticker: str) -> pd.DataFrame:
    """
    Fetch price data from Finnhub API.
    """
    url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_API_KEY}"
    try:
        print(f"[INFO] Attempting Finnhub for {ticker}")
        response = requests.get(url)
        time.sleep(API_CALL_DELAY)  # delay after call
        if response.status_code != 200:
            print(f"[ERROR] Finnhub API error: {response.status_code}")
            return None
        json_data = response.json()
        if 'c' not in json_data:
            print("[WARN] Finnhub returned incomplete data.")
            return None
        df = pd.DataFrame([{
            'Close': json_data['c'],
            'Open': json_data['o'],
            'High': json_data['h'],
            'Low': json_data['l']
        }])
        print("[INFO] Finnhub data retrieved.")
        return df
    except Exception as e:
        print(f"[ERROR] Finnhub exception: {e}")
        time.sleep(API_CALL_DELAY)
        return None

def fetch_price_with_fallback(ticker: str) -> pd.DataFrame:
    """
    Fetch price data using yfinance with Finnhub as fallback.
    """
    data = fetch_price_yfinance(ticker)
    if data is not None:
        return data
    print("[INFO] Falling back to Finnhub...")
    return fetch_price_finnhub(ticker)

if __name__ == "__main__":
    TICKER = "AAPL"
    data = fetch_price_with_fallback(TICKER)
    if data is not None:
        print(data)
    else:
        print("[ERROR] No data fetched from any source.")
