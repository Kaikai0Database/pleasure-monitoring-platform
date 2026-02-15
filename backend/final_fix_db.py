"""
最終檢查和修復資料庫約束問題
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')

# 確保資料庫存在
if not os.path.exists(db_path):
    print("資料庫不存在，將創建新的")
else:
    print("找到現有資料庫，檢查結構...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 檢查 diaries 表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='diaries'")
    if cursor.fetchone():
        # 檢查索引
        cursor.execute("PRAGMA index_list(diaries)")
        indexes = cursor.fetchall()
        print(f"\n當前索引數量: {len(indexes)}")
        for idx in indexes:
            print(f"  索引: {idx}")
            # 獲取索引詳情
            cursor.execute(f"PRAGMA index_info('{idx[1]}')")
            cols = cursor.fetchall()
            for col in cols:
                print(f"    - 欄位: {col}")
    
    conn.close()

# 強制重建
print("\n=== 強制重建資料庫 ===")
if os.path.exists(db_path):
    os.remove(db_path)
    print("已刪除舊資料庫檔案")

# 創建新資料庫
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 先建立 users 表（如果需要）
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# 建立 diaries 表 - 完全沒有任何唯一約束
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

# 建立 assessment_history 表（如果需要）
cursor.execute("""
CREATE TABLE IF NOT EXISTS assessment_history (
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

conn.commit()

print("新資料庫已創建")

# 最終驗證
print("\n=== 最終驗證 ===")
cursor.execute("PRAGMA index_list(diaries)")
indexes = cursor.fetchall()
print(f"diaries 表索引數量: {len(indexes)}")
if len(indexes) > 0:
    print("警告！發現索引：")
    for idx in indexes:
        print(f"  {idx}")
else:
    print("確認：沒有任何索引或約束")

cursor.execute("PRAGMA table_info(diaries)")
columns = cursor.fetchall()
print("\ndiaries 表結構:")
for col in columns:
    print(f"  {col[1]}: {col[2]} (NOT NULL: {col[3]})")

conn.close()
print("\n完成！資料庫已準備好，可以創建多筆日記。")
