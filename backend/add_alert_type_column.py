"""
Add alert_type column to score_alerts table
"""
from app.models import db
from sqlalchemy import text

def add_alert_type_column():
    """Add alert_type column to score_alerts table"""
    with db.engine.connect() as conn:
        # Add alert_type column with default value 'high'
        conn.execute(text('''
            ALTER TABLE score_alerts 
            ADD COLUMN alert_type VARCHAR(10) DEFAULT 'high' NOT NULL
        '''))
        conn.commit()
    print("✓ alert_type column added successfully")

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        add_alert_type_column()
