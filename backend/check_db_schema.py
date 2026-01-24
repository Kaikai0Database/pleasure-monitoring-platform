import sqlite3
import os

# 確保路徑正確
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')
print(f"Checking database at: {db_path}")

if not os.path.exists(db_path):
    print("❌ Database file not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. 檢查表定義 SQL
print("\n--- Table Definition ---")
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='diaries'")
result = cursor.fetchone()
if result:
    print(result[0])
else:
    print("❌ Table 'diaries' not found!")

# 2. 檢查索引
print("\n--- Indexes ---")
cursor.execute("PRAGMA index_list(diaries)")
indexes = cursor.fetchall()
for idx in indexes:
    print(f"Index: {idx[1]}, Unique: {idx[2]}, Origin: {idx[3]}")
    # 檢查索引欄位
    cursor.execute(f"PRAGMA index_info('{idx[1]}')")
    cols = cursor.fetchall()
    for col in cols:
        print(f"  - Column: {col[2]}")

conn.close()
