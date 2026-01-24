import sqlite3
import os

db_path = 'instance/database.db'

def migrate_db():
    print(f"Checking database at {db_path}...")
    
    if not os.path.exists(db_path):
        print("Database not found!")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(assessment_history)")
    columns = [info[1] for info in cursor.fetchall()]
    print(f"Existing columns: {columns}")
    
    try:
        if 'is_deleted' not in columns:
            print("Adding 'is_deleted' column...")
            cursor.execute("ALTER TABLE assessment_history ADD COLUMN is_deleted BOOLEAN DEFAULT 0")
            
        if 'deleted_at' not in columns:
            print("Adding 'deleted_at' column...")
            cursor.execute("ALTER TABLE assessment_history ADD COLUMN deleted_at TIMESTAMP")
            
        if 'delete_reason' not in columns:
            print("Adding 'delete_reason' column...")
            cursor.execute("ALTER TABLE assessment_history ADD COLUMN delete_reason VARCHAR(255)")
            
        conn.commit()
        print("Migration successful!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_db()
