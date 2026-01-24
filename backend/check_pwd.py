import sqlite3
import os
from werkzeug.security import check_password_hash

DB_PATH = os.path.join('instance', 'database.db')

def check_pwd():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check user angel921030chenen@gmail.com
        cursor.execute("SELECT password_hash FROM users WHERE email='angel921030chenen@gmail.com'")
        row = cursor.fetchone()
        if row:
            ph = row[0]
            pwd = '123456789'
            is_match = check_password_hash(ph, pwd)
            print(f"User angel921030chenen@gmail.com password '123456789' match: {is_match}")
        else:
            print("User angel921030chenen@gmail.com not found")

        # Check admin admin@hospital.com
        cursor.execute("SELECT password_hash FROM healthcare_staff WHERE email='admin@hospital.com'")
        row = cursor.fetchone()
        if row:
            ph = row[0]
            # Try some common defaults if I find them elsewhere
            pwd_options = ['admin123', 'password', '123456', '12345678']
            for p in pwd_options:
                if check_password_hash(ph, p):
                    print(f"Admin admin@hospital.com password '{p}' match: True")
                    break
            else:
                print("Admin admin@hospital.com password not matched with common defaults")
        else:
            print("Admin admin@hospital.com not found")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    check_pwd()
