import sqlite3
import os

db_path = 'instance/database.db'

def migrate_user():
    print(f"Checking database at {db_path}...")
    
    if not os.path.exists(db_path):
        print("Database not found!")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(users)")
    columns = [info[1] for info in cursor.fetchall()]
    print(f"Existing columns: {columns}")
    
    try:
        if 'last_login_date' not in columns:
            print("Adding 'last_login_date' column...")
            cursor.execute("ALTER TABLE users ADD COLUMN last_login_date DATE")
            
        if 'daily_login_count' not in columns:
            print("Adding 'daily_login_count' column...")
            cursor.execute("ALTER TABLE users ADD COLUMN daily_login_count INTEGER DEFAULT 0")
            
        conn.commit()
        print("Migration successful!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_user()
