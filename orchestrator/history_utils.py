import yfinance as yf
import pandas as pd
import numpy as np

import yfinance as yf
import pandas as pd
import requests
import os

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

def fetch_52week_history(ticker: str) -> pd.DataFrame:
    """
    Try to fetch 52-week data with yfinance, fallback to Finnhub.
    """
    # First try yfinance
    data = yf.download(ticker, period="1y", interval="1d", auto_adjust=False)
    if not data.empty:
        return _compute_deltas(data)

    print(f"[WARN] yfinance failed for {ticker}, trying Finnhub...")

    # Fallback to Finnhub
    if not FINNHUB_API_KEY:
        print("[ERROR] No Finnhub API key configured.")
        return pd.DataFrame()

    url = f"https://finnhub.io/api/v1/stock/candle"
    params = {
        "symbol": ticker,
        "resolution": "D",
        "from": int((pd.Timestamp.now() - pd.Timedelta(days=365)).timestamp()),
        "to": int(pd.Timestamp.now().timestamp()),
        "token": FINNHUB_API_KEY
    }

    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        print(f"[ERROR] Finnhub API error: {resp.status_code}")
        return pd.DataFrame()

    json_data = resp.json()
    if json_data.get("s") != "ok":
        print(f"[ERROR] Finnhub returned error status: {json_data.get('s')}")
        return pd.DataFrame()

    df = pd.DataFrame({
        "Open": json_data["o"],
        "Close": json_data["c"],
        "High": json_data["h"],
        "Low": json_data["l"]
    }, index=pd.to_datetime(json_data["t"], unit="s"))

    return _compute_deltas(df)

def _compute_deltas(data: pd.DataFrame) -> pd.DataFrame:
    data["Delta_OC"] = (abs(data["Open"] - data["Close"]) / data["Open"]) * 100
    data["Delta_HL"] = (abs(data["High"] - data["Low"]) / data["Open"]) * 100
    return data


def compute_52week_stats(data: pd.DataFrame) -> dict:
    """
    Compute descriptive stats for 52-week history.
    """
    if data.empty:
        return {
            "mean_delta_oc": None,
            "std_delta_oc": None,
            "90th_delta_oc": None,
            "mean_delta_hl": None,
            "std_delta_hl": None,
            "90th_delta_hl": None
        }

    return {
        "mean_delta_oc": float(np.mean(data["Delta_OC"])),
        "std_delta_oc": float(np.std(data["Delta_OC"])),
        "90th_delta_oc": float(np.percentile(data["Delta_OC"], 90)),
        "mean_delta_hl": float(np.mean(data["Delta_HL"])),
        "std_delta_hl": float(np.std(data["Delta_HL"])),
        "90th_delta_hl": float(np.percentile(data["Delta_HL"], 90))
    }

def compute_trend_indicators(data: pd.DataFrame) -> dict:
    """
    Compute trend indicators over multiple periods.
    """
    import numpy as np

    indicators = {}

    for period, label in [(5, "5d"), (30, "30d"), (90, "90d"), (180, "180d"), (250, "365d")]:# Note: 365d = environ 250 jours boursiers
        if len(data) >= period:
            recent = data.tail(period)

            indicators[f"mean_delta_oc_{label}"] = float(recent["Delta_OC"].mean())
            indicators[f"mean_delta_hl_{label}"] = float(recent["Delta_HL"].mean())
            indicators[f"mean_close_{label}"] = float(recent["Close"].mean())

            slope_close = float(np.polyfit(range(len(recent)), recent["Close"], 1)[0])
            indicators[f"close_slope_{label}"] = slope_close
        else:
            indicators[f"mean_delta_oc_{label}"] = None
            indicators[f"mean_delta_hl_{label}"] = None
            indicators[f"mean_close_{label}"] = None
            indicators[f"close_slope_{label}"] = None

    return indicators

