import sqlite3
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')

def list_users():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, email, name, created_at FROM users")
        users = cursor.fetchall()
        
        print(f"Total Users: {len(users)}")
        print("-" * 60)
        print(f"{'ID':<5} {'Name':<20} {'Email':<30}")
        print("-" * 60)
        for user in users:
            print(f"{user[0]:<5} {user[2]:<20} {user[1]:<30}")
        print("-" * 60)

    except Exception as e:
        print(f"Error querying database: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    list_users()
