import sqlite3
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')

def migrate():
    # Helper to check if column exists
    def column_exists(cursor, table, column):
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [info[1] for info in cursor.fetchall()]
        return column in columns

    # Helper to add column if not exists
    def add_column(cursor, table, column_def):
        column_name = column_def.split()[0]
        if not column_exists(cursor, table, column_name):
            print(f"Adding column {column_name} to {table}...")
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column_def}")
        else:
            print(f"Column {column_name} already exists in {table}.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Define new columns
        # Note: SQLite ALTER TABLE ADD COLUMN limited support, doing one by one
        columns = [
            "nickname TEXT",
            "dob DATE",
            "gender TEXT",
            "height REAL",
            "weight REAL",
            "education TEXT",
            "marital_status TEXT",
            "marriage_other TEXT",
            "has_children BOOLEAN",
            "children_count INTEGER",
            "economic_status TEXT",
            "family_structure TEXT",
            "family_other TEXT",
            "has_job BOOLEAN",
            "salary_range TEXT",
            "location_city TEXT",
            "location_district TEXT",
            "living_situation TEXT",
            "cohabitant_count INTEGER",
            "religion BOOLEAN",
            "religion_other TEXT",
            "is_profile_completed BOOLEAN DEFAULT 0"
        ]

        for col in columns:
            add_column(cursor, 'users', col)

        conn.commit()
        print("Migration completed successfully!")

    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
    else:
        migrate()
