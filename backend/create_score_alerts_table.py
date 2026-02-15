"""
Create score_alerts table
"""
from app.models import db
from sqlalchemy import text

def create_score_alerts_table():
    """Create score_alerts table"""
    with db.engine.connect() as conn:
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS score_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                alert_date DATE NOT NULL,
                daily_average REAL NOT NULL,
                exceeded_lines TEXT NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        '''))
        conn.commit()
    print("✓ score_alerts table created successfully")

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        create_score_alerts_table()

