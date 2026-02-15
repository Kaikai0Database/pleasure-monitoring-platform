"""
手動修改資料庫結構：移除 mood 欄位的 NOT NULL 約束
"""
import sqlite3
import os

# 連接資料庫
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("開始修改資料庫結構...")
    
    # 先刪除可能存在的臨時表
    print("清理舊的臨時表...")
    cursor.execute("DROP TABLE IF EXISTS diaries_new")
    
    # 1. 創建新表（mood 可為 NULL）
    print("步驟 1: 創建新表結構...")
    cursor.execute("""
        CREATE TABLE diaries_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date DATE NOT NULL,
            mood VARCHAR(50),
            content TEXT,
            images TEXT,
            period_marker BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # 2. 複製現有資料
    print("步驟 2: 複製現有資料...")
    cursor.execute("""
        INSERT INTO diaries_new 
        SELECT * FROM diaries
    """)
    
    # 3. 刪除舊表
    print("步驟 3: 刪除舊表...")
    cursor.execute("DROP TABLE diaries")
    
    # 4. 重命名新表
    print("步驟 4: 重命名新表...")
    cursor.execute("ALTER TABLE diaries_new RENAME TO diaries")
    
    # 提交變更
    conn.commit()
    print("✓ 成功！mood 欄位現在允許 NULL 值。")
    
except Exception as e:
    conn.rollback()
    print(f"X 錯誤: {e}")
finally:
    conn.close()
