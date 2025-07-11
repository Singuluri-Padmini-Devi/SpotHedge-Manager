import sqlite3
import os
from datetime import datetime

# DB path setup
DB_FILE = os.path.join(os.path.dirname(__file__), '..', 'hedge_logs.db')

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS hedge_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            asset TEXT,
            delta REAL,
            action TEXT,
            price REAL,
            timestamp TEXT
        )
        """)
        conn.commit()

def log_hedge(user_id, asset, delta, action, price):
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO hedge_logs (user_id, asset, delta, action, price, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, asset, delta, action, price, timestamp))
        conn.commit()

def get_hedge_history(user_id):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timestamp, asset, delta, action, price
                FROM hedge_logs
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT 10
            """, (user_id,))
            return cursor.fetchall()
    except Exception as e:
        print("Error retrieving hedge history:", e)
        return []
