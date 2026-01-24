"""
真正的資料庫修復腳本
針對正確的檔案：database.db
"""
import sqlite3
import os

# 正確的資料庫名稱
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')
print("Target Database: " + db_path)

if os.path.exists(db_path):
    os.remove(db_path)
    print("Old database removed.")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Creating tables...")

# Users
cursor.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    name VARCHAR(255)
)
""")

# Assessment History
cursor.execute("""
CREATE TABLE assessment_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    total_score INTEGER NOT NULL,
    max_score INTEGER NOT NULL,
    level VARCHAR(20),
    answers TEXT,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

# Diaries - NO UNIQUE CONSTRAINT
cursor.execute("""
CREATE TABLE diaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL,
    mood VARCHAR(50),
    content TEXT,
    images TEXT,
    period_marker INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

conn.commit()
print("Tables created successfully.")

# Verify
cursor.execute("PRAGMA index_list(diaries)")
indexes = cursor.fetchall()
if len(indexes) == 0:
    print("VERIFIED: No unique constraints on diaries table.")
else:
    print("WARNING: Indexes found: " + str(indexes))

conn.close()
