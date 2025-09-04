# db.py
import sqlite3

DB_NAME = "my_db"  # or absolute path if you want


def get_connection():
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row  # lets you access columns by name
    except Exception as e:
        print("Connection failed:", e)
    return conn
