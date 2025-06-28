"""
price_agent.py

Fetches stock price data using yfinance with a fallback to Finnhub.
Includes enriched alert logic: static thresholds + dynamic anomaly detection.
"""

import yfinance as yf
import pandas as pd
import requests
import time
from dotenv import load_dotenv
import os

# Load API key
load_dotenv()
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

API_CALL_DELAY = 3  # seconds between API calls

def fetch_price_yfinance(ticker: str, period="5d", interval="1d") -> pd.DataFrame:
    """
    Try to fetch price data using yfinance.
    """
    try:
        print(f"[INFO] Attempting yfinance for {ticker}")
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        time.sleep(API_CALL_DELAY)
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
    Fetch price data from Finnhub API (current quote only).
    """
    url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_API_KEY}"
    try:
        print(f"[INFO] Attempting Finnhub for {ticker}")
        response = requests.get(url)
        time.sleep(API_CALL_DELAY)
        if response.status_code != 200:
            print(f"[ERROR] Finnhub API error: {response.status_code}")
            return None
        json_data = response.json()
        if 'c' not in json_data or json_data['c'] == 0:
            print("[WARN] Finnhub returned incomplete data.")
            return None
        df = pd.DataFrame([{
            'Open': json_data['o'],
            'Close': json_data['c'],
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

def compute_deltas(data: pd.DataFrame) -> pd.DataFrame:
    """
    Add delta columns to the data: Open-Close % and High-Low %.
    """
    data = data.copy()
    data['Delta_OC'] = ((data['Close'] - data['Open']) / data['Open']) * 100
    data['Delta_HL'] = ((data['High'] - data['Low']) / data['Open']) * 100
    return data

def check_alert_enriched(data: pd.DataFrame, static_oc=5.0, static_hl=7.0, dynamic_window=3, std_multiplier=2.0) -> bool:
    """
    Check for alert based on static thresholds and dynamic thresholds.
    """
    if data is None or data.empty:
        print("[ERROR] No data to evaluate alert.")
        return False

    data = compute_deltas(data)

    latest_oc = data['Delta_OC'].iloc[-1]
    latest_hl = data['Delta_HL'].iloc[-1]

    print(f"[INFO] Latest Delta_OC: {latest_oc:.2f}%")
    print(f"[INFO] Latest Delta_HL: {latest_hl:.2f}%")

    # Static checks
    if abs(latest_oc) >= static_oc:
        print(f"[ALERT] Static OC threshold exceeded ({static_oc}%)")
        return True
    if abs(latest_hl) >= static_hl:
        print(f"[ALERT] Static HL threshold exceeded ({static_hl}%)")
        return True

    # Dynamic checks
    if len(data) > dynamic_window:
        oc_hist = data['Delta_OC'].iloc[-dynamic_window-1:-1]
        hl_hist = data['Delta_HL'].iloc[-dynamic_window-1:-1]

        oc_mean = oc_hist.mean()
        oc_std = oc_hist.std()
        hl_mean = hl_hist.mean()
        hl_std = hl_hist.std()

        print(f"[INFO] OC dynamic baseline: mean={oc_mean:.2f}%, std={oc_std:.2f}%")
        print(f"[INFO] HL dynamic baseline: mean={hl_mean:.2f}%, std={hl_std:.2f}%")

        if (latest_oc - oc_mean) > std_multiplier * oc_std:
            print(f"[ALERT] Dynamic OC anomaly detected (> {std_multiplier} std devs above mean)")
            return True
        if (latest_hl - hl_mean) > std_multiplier * hl_std:
            print(f"[ALERT] Dynamic HL anomaly detected (> {std_multiplier} std devs above mean)")
            return True
    else:
        print("[INFO] Not enough data for dynamic threshold evaluation.")

    print("[INFO] No alert triggered.")
    return False


if __name__ == "__main__":
    TICKER = "AAPL"
    data = fetch_price_with_fallback(TICKER)
    if data is not None:
        alert = check_alert_enriched(data)
        print(f"[RESULT] Alert triggered: {alert}")
        print(data.tail())
    else:
        print("[ERROR] No data fetched from any source.")
