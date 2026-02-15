import sqlite3
import os
import sys

print("Python version:", sys.version)
print("Current CWD:", os.getcwd())

DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')
print("Target DB Path:", DB_PATH)

if os.path.exists(DB_PATH):
    print("DB file exists.")
    try:
        conn = sqlite3.connect(DB_PATH)
        print("Connected successfully.")
        conn.close()
    except Exception as e:
        print("Connection failed:", e)
else:
    print("DB file does NOT exist.")
