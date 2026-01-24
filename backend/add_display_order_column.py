import sqlite3
import os

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')
print(f"Migrating database at: {db_path}")

if not os.path.exists(db_path):
    print("❌ Database file not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if display_order column exists
    cursor.execute("PRAGMA table_info(patient_watchlist)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    print(f"Current columns in patient_watchlist: {column_names}")
    
    if 'display_order' not in column_names:
        print("Adding display_order column...")
        cursor.execute("ALTER TABLE patient_watchlist ADD COLUMN display_order INTEGER DEFAULT 0")
        conn.commit()
        print("✅ Successfully added display_order column!")
    else:
        print("✅ display_order column already exists!")
    
    # Verify the column was added
    cursor.execute("PRAGMA table_info(patient_watchlist)")
    columns = cursor.fetchall()
    print("\nUpdated table schema:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    conn.close()
