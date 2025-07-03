import sqlite3
import os

DB_PATH = os.path.join("db", "agentic.db")

def init_db():
    """
    Initialize the SQLite database and create table if not exists.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            alert INTEGER NOT NULL,
            delta_oc REAL,
            delta_hl REAL,
            static_oc_threshold REAL,
            static_hl_threshold REAL,
            dynamic_window INTEGER,
            std_multiplier REAL
        )
    """)
    conn.commit()
    conn.close()

def log_price_result(result: dict):
    """
    Insert a price agent result into the database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO price_logs (
            ticker, timestamp, alert, delta_oc, delta_hl,
            static_oc_threshold, static_hl_threshold, dynamic_window, std_multiplier
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        result["ticker"],
        result["timestamp"],
        int(result["alert"]),
        result["metrics"].get("delta_oc"),
        result["metrics"].get("delta_hl"),
        result["details"]["static_oc_threshold"],
        result["details"]["static_hl_threshold"],
        result["details"]["dynamic_window"],
        result["details"]["std_multiplier"]
    ))
    conn.commit()
    conn.close()

def get_recent_logs(ticker: str, limit: int = 5) -> list:
    """
    Retrieve recent price logs for a given ticker from the database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT timestamp, alert, delta_oc, delta_hl
        FROM price_logs
        WHERE ticker = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (ticker.upper(), limit)
    )
    rows = cursor.fetchall()
    conn.close()

    # Format as list of dicts
    return [
        {"timestamp": r[0], "alert": r[1], "delta_oc": r[2], "delta_hl": r[3]}
        for r in rows
    ]

def compute_history_stats(history: list) -> dict:
    """
    Compute basic stats from recent history (mean, std, alert count).
    """
    import numpy as np

    if not history:
        return {
            "mean_delta_oc": None,
            "std_delta_oc": None,
            "mean_delta_hl": None,
            "std_delta_hl": None,
            "alert_count": 0
        }

    delta_oc = [h['delta_oc'] for h in history if h['delta_oc'] is not None]
    delta_hl = [h['delta_hl'] for h in history if h['delta_hl'] is not None]

    return {
        "mean_delta_oc": float(np.mean(delta_oc)) if delta_oc else None,
        "std_delta_oc": float(np.std(delta_oc)) if delta_oc else None,
        "mean_delta_hl": float(np.mean(delta_hl)) if delta_hl else None,
        "std_delta_hl": float(np.std(delta_hl)) if delta_hl else None,
        "alert_count": sum(h['alert'] for h in history)
    }
