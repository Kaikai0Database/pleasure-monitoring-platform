"""
資料庫遷移腳本：允許 mood 欄位為 NULL
"""
import sqlite3
import os

# 連接資料庫
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("開始資料庫遷移...")
    
    # 1. 移除舊的唯一性約束（如果存在）
    print("步驟 1: 移除唯一性約束...")
    cursor.execute("DROP INDEX IF EXISTS unique_user_diary_per_day")
    
    # 2. 創建新的表結構（mood 可以為 NULL）
    print("步驟 2: 創建臨時表...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diaries_new (
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
    
    # 3. 複製資料
    print("步驟 3: 複製資料...")
    cursor.execute("""
        INSERT INTO diaries_new (id, user_id, date, mood, content, images, period_marker, created_at, updated_at)
        SELECT id, user_id, date, mood, content, images, period_marker, created_at, updated_at
        FROM diaries
    """)
    
    # 4. 刪除舊表
    print("步驟 4: 刪除舊表...")
    cursor.execute("DROP TABLE diaries")
    
    # 5. 重命名新表
    print("步驟 5: 重命名新表...")
    cursor.execute("ALTER TABLE diaries_new RENAME TO diaries")
    
    # 提交變更
    conn.commit()
    print("✅ 資料庫遷移完成！mood 欄位現在允許 NULL。")
    
except Exception as e:
    conn.rollback()
    print(f"❌ 遷移失敗: {e}")
finally:
    conn.close()
