import sqlite3
import os

db_path = 'instance/database.db'

def check_schema():
    print(f"Checking database at {db_path}...")
    
    if not os.path.exists(db_path):
        print("Database not found!")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get existing columns
        cursor.execute("PRAGMA table_info(assessment_history)")
        columns = cursor.fetchall()
        print("Columns in assessment_history:")
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
            
    except Exception as e:
        print(f"Check failed: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    check_schema()
