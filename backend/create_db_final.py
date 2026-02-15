"""
階段 1：創建無 UNIQUE 約束的資料庫
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== 開始創建資料庫 ===")

# 刪除舊表
cursor.execute("DROP TABLE IF EXISTS diaries")
print("✓ 已刪除舊表")

# 創建新表（無 UNIQUE 約束）
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
print("✓ 已創建新表（無 UNIQUE 約束）")

conn.commit()

# 驗證結構
print("\n=== 驗證結構 ===")
cursor.execute("PRAGMA index_list(diaries)")
indexes = cursor.fetchall()
print(f"索引數量: {len(indexes)}")
if len(indexes) == 0:
    print("✓ 確認：沒有唯一性索引")
else:
    for idx in indexes:
        print(f"  警告：發現索引 {idx}")

conn.close()
print("\n✓ 資料庫創建完成！可以創建多篇日記了。")
