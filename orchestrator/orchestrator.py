from fastapi import FastAPI
from agents.price_agent import fetch_price_with_fallback, compute_deltas, check_alert_enriched
from datetime import datetime
import pandas as pd
from orchestrator.db_utils import init_db, log_price_result, get_recent_logs, compute_history_stats
import os
import sqlite3
from fastapi import Query
from typing import Optional
from orchestrator.ai_utils import generate_price_comment, generate_investment_decision
from orchestrator.history_utils import fetch_52week_history, compute_52week_stats, compute_trend_indicators



DB_PATH = os.path.join("db", "agentic.db")

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Orchestrator is running"}

@app.get("/price")
def price_agent(ticker: str = "AAPL"):
    init_db()
    data = fetch_price_with_fallback(ticker)
    print(f"[DEBUG] Raw data fetched (rows): {len(data)}")
    print(f"[DEBUG] Data head:\n{data.head()}")
    print(f"[DEBUG] Data tail:\n{data.tail()}")
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
        delta_oc_val = latest_row.get("Delta_OC", float("nan"))
        delta_hl_val = latest_row.get("Delta_HL", float("nan"))

        output["metrics"] = {
            "delta_oc": float(delta_oc_val),
            "delta_hl": float(delta_hl_val)
        }

    log_price_result(output)
    comment = generate_price_comment(output)
    output["ia_comment"] = comment
    history_data = fetch_52week_history(ticker)
    stats_52w = compute_52week_stats(history_data)
    news_context = "No major news affecting the stock reported today."  # ou récupéré de ton futur News Agent
    trend = compute_trend_indicators(history_data)
    print(f"[DEBUG] Number of data points: {len(data)}")
    print(f"[DEBUG] First date: {data.index.min()}, Last date: {data.index.max()}")

    print("\n📝 === DECISION INPUT DATA ===")
    print(f"Ticker: {output['ticker']}")
    print(f"Current metrics:")
    print(f"  Delta_OC: {output['metrics'].get('delta_oc', 'N/A')}%")
    print(f"  Delta_HL: {output['metrics'].get('delta_hl', 'N/A')}%")
    print(f"Alert status: {'TRIGGERED' if output['alert'] else 'not triggered'}")

    print("\n52-week stats:")
    for key, value in stats_52w.items():
        print(f"  {key}: {value}%")

    print("\nTrend indicators (recent dynamics):")
    for key, value in trend.items():
        print(f"  {key}: {value}%")

    print(f"\nNews context: {news_context}")
    print("📝 === END OF INPUT DATA ===\n")
    decision = generate_investment_decision(output, stats_52w, trend, news_context)
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