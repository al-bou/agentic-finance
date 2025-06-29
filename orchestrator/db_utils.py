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
