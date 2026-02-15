"""
檢查並修復資料庫結構
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== 檢查當前資料庫結構 ===")
cursor.execute("PRAGMA table_info(diaries)")
columns = cursor.fetchall()
for col in columns:
    print(f"欄位: {col[1]}, 類型: {col[2]}, NOT NULL: {col[3]}, 預設值: {col[4]}")

print("\n=== 開始修復 ===")
try:
    # 1. 創建新表（mood 明確設定為可 NULL）
    print("1. 創建新表...")
    cursor.execute("DROP TABLE IF EXISTS diaries_temp")
    cursor.execute("""
        CREATE TABLE diaries_temp (
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
    
    # 2. 複製資料（如果有的話）
    print("2. 複製資料...")
    try:
        cursor.execute("""
            INSERT INTO diaries_temp 
            SELECT * FROM diaries
        """)
        print(f"   已複製 {cursor.rowcount} 筆資料")
    except:
        print("   沒有現有資料需要複製")
    
    # 3. 刪除舊表
    print("3. 刪除舊表...")
    cursor.execute("DROP TABLE IF EXISTS diaries")
    
    # 4. 重命名新表
    print("4. 重命名新表...")
    cursor.execute("ALTER TABLE diaries_temp RENAME TO diaries")
    
    conn.commit()
    print("\n=== 修復完成！===")
    
    # 驗證
    print("\n=== 驗證新結構 ===")
    cursor.execute("PRAGMA table_info(diaries)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"欄位: {col[1]}, 類型: {col[2]}, NOT NULL: {col[3]}")
    
except Exception as e:
    conn.rollback()
    print(f"\n錯誤: {e}")
finally:
    conn.close()
