from fastapi import FastAPI
from agents.price_agent import fetch_price_with_fallback, compute_deltas, check_alert_enriched
from datetime import datetime
import pandas as pd
from orchestrator.db_utils import init_db, log_price_result, get_recent_logs
import os
import sqlite3
from fastapi import Query
from typing import Optional
from orchestrator.ai_utils import generate_price_comment, generate_investment_decision


DB_PATH = os.path.join("db", "agentic.db")

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
    comment = generate_price_comment(output)
    output["ia_comment"] = comment
    history = get_recent_logs(ticker)
    decision = generate_investment_decision(output, history)
    output["ia_decision"] = decision

    return output

@app.get("/price_logs")
def get_price_logs(
    alert: Optional[int] = Query(None, description="Filter by alert status (1 or 0)"),
    ticker: Optional[str] = Query(None, description="Filter by ticker symbol"),
    limit: int = Query(10, description="Limit number of results (default 10)")
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = "SELECT * FROM price_logs"
    conditions = []
    params = []

    if alert is not None:
        conditions.append("alert = ?")
        params.append(alert)
    if ticker is not None:
        conditions.append("ticker = ?")
        params.append(ticker.upper())

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, tuple(params))
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()

    conn.close()

    # Convert to list of dicts
    results = [dict(zip(columns, row)) for row in rows]
    return results