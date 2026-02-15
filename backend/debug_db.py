import sqlite3
import os

DB_PATH = os.path.join('instance', 'database.db')

def debug():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print("=== USERS ===")
        cursor.execute("SELECT id, email, name FROM users")
        for row in cursor.fetchall():
            print(row)

        print("\n=== HEALTHCARE STAFF ===")
        # Check tables first to be sure
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"Tables: {tables}")
        
        if 'healthcare_staff' in tables:
            cursor.execute("SELECT id, email, name, role FROM healthcare_staff")
            for row in cursor.fetchall():
                print(row)
        else:
            print("healthcare_staff table not found")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    debug()
