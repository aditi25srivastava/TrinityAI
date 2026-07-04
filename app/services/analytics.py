import sqlite3
import os
import json
from datetime import datetime
from typing import List

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'metrics.db')

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            latency_ms REAL,
            tts_time_ms REAL,
            stt_accuracy REAL,
            satisfaction_score REAL,
            success_rate REAL,
            personality TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_metric(latency_ms: float, tts_time_ms: float, stt_accuracy: float, satisfaction_score: float, success_rate: float, personality: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO metrics (timestamp, latency_ms, tts_time_ms, stt_accuracy, satisfaction_score, success_rate, personality)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), latency_ms, tts_time_ms, stt_accuracy, satisfaction_score, success_rate, personality))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Failed to log metric: {e}")

def get_recent_metrics(limit: int = 100) -> List[dict]:
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM metrics ORDER BY timestamp DESC LIMIT ?', (limit,))
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Failed to get metrics: {e}")
        return []

# Initialize DB on import
init_db()
