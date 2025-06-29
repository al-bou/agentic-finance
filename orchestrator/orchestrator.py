from fastapi import FastAPI
from agents.price_agent import fetch_price_with_fallback, compute_deltas, check_alert_enriched
from datetime import datetime
import pandas as pd
from orchestrator.db_utils import init_db, log_price_result


import sqlite3

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Orchestrator is running"}

@app.get("/price")
def price_agent(ticker: str = "AAPL"):
    init_db()
    data = fetch_price_with_fallback(ticker)
    output = {
        "ticker": ticker,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "alert": False,
        "metrics": {},
        "details": {
            "static_oc_threshold": 5.0,
            "static_hl_threshold": 7.0,
            "dynamic_window": 3,
            "std_multiplier": 2.0
        }
    }

    if data is not None:
        data = compute_deltas(data)
        alert = check_alert_enriched(data)
        output["alert"] = alert

        latest_row = data.iloc[-1]
        output["metrics"] = {
            "delta_oc": float(latest_row.get("Delta_OC", float("nan"))),
            "delta_hl": float(latest_row.get("Delta_HL", float("nan")))
        }
    log_price_result(output)
    return output
