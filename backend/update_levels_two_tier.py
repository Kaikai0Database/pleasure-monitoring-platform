"""
Migration script to update all assessment history records to new two-tier level system
Updates all records to use only two levels:
- Score >= 24: 需要關注 (Needs Attention)
- Score < 24: 良好 (Good)
"""
import sqlite3
import os

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')
print(f"Updating assessment levels in: {db_path}")

if not os.path.exists(db_path):
    print("❌ Database file not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Get all assessment records
    cursor.execute("SELECT id, total_score, level FROM assessment_history")
    records = cursor.fetchall()
    
    print(f"\nFound {len(records)} assessment records")
    
    # Update each record based on score
    updated_count = 0
    for record_id, total_score, current_level in records:
        # Determine new level based on score
        if total_score >= 24:
            new_level = '需要關注'
        else:
            new_level = '良好'
        
        # Only update if level has changed
        if current_level != new_level:
            cursor.execute(
                "UPDATE assessment_history SET level = ? WHERE id = ?",
                (new_level, record_id)
            )
            updated_count += 1
            print(f"  Updated record {record_id}: score={total_score}, '{current_level}' → '{new_level}'")
    
    conn.commit()
    
    print(f"\n✅ Successfully updated {updated_count} records!")
    print(f"   {len(records) - updated_count} records were already correct")
    
    # Show summary
    cursor.execute("SELECT level, COUNT(*) FROM assessment_history GROUP BY level")
    summary = cursor.fetchall()
    print("\nCurrent level distribution:")
    for level, count in summary:
        print(f"  {level}: {count} records")
    
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    conn.close()
