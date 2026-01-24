import sqlite3
import os
import sys

# Ensure path is correct
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')
print("Checking database at: " + db_path)

if not os.path.exists(db_path):
    print("X Database file not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Check Table Definition SQL
print("\n--- Table Definition ---")
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='diaries'")
result = cursor.fetchone()
if result:
    print(result[0])
else:
    print("X Table 'diaries' not found!")
    exit(1)

# 2. Check Indexes
print("\n--- Indexes ---")
cursor.execute("PRAGMA index_list(diaries)")
indexes = cursor.fetchall()
if len(indexes) == 0:
    print("OK: No indexes found (except implicit PK if any)")
else:
    for idx in indexes:
        print("Index: " + str(idx[1]) + ", Unique: " + str(idx[2]))

# 3. Test Insertion
print("\n--- Test Insertion ---")
try:
    # Need a user first
    cursor.execute("SELECT id FROM users LIMIT 1")
    user = cursor.fetchone()
    if not user:
        print("Creating temp user for test...")
        cursor.execute("INSERT INTO users (username, email, password_hash) VALUES ('test_diag', 'diag@test.com', 'pass')")
        user_id = cursor.lastrowid
    else:
        user_id = user[0]
        print("Using existing user ID: " + str(user_id))

    # Insert Diary 1
    cursor.execute("INSERT INTO diaries (user_id, date, mood, content) VALUES (?, '2025-12-31', 'happy', 'Test 1')", (user_id,))
    print("Diary 1 inserted.")

    # Insert Diary 2 (Same day)
    cursor.execute("INSERT INTO diaries (user_id, date, mood, content) VALUES (?, '2025-12-31', 'sad', 'Test 2')", (user_id,))
    print("Diary 2 inserted.")
    
    print("SUCCESS: Multiple diaries allowed!")
    conn.rollback() # Don't actually save test data

except Exception as e:
    print("FAIL: Insertion failed!")
    print(str(e))

conn.close()
