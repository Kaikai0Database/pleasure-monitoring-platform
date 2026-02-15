#!/usr/bin/env python3
"""
Database migration script to add has_consented field to users table.
Run this script to update existing database schema.
"""

from app import create_app
from app.models import db
from sqlalchemy import text

def migrate():
    """Add has_consented column to users table"""
    app = create_app('development')
    
    with app.app_context():
        try:
            # Check if column already exists
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            if 'has_consented' in columns:
                print("✓ Column 'has_consented' already exists. No migration needed.")
                return
            
            # Add the column
            print("Adding 'has_consented' column to users table...")
            db.session.execute(text(
                "ALTER TABLE users ADD COLUMN has_consented BOOLEAN DEFAULT 0 NOT NULL"
            ))
            db.session.commit()
            print("✓ Successfully added 'has_consented' column")
            
            # Verify
            columns = [col['name'] for col in inspector.get_columns('users')]
            if 'has_consented' in columns:
                print("✓ Migration verified successfully")
            else:
                print("✗ Migration verification failed")
                
        except Exception as e:
            db.session.rollback()
            print(f"✗ Migration failed: {str(e)}")
            raise

if __name__ == '__main__':
    print("=" * 60)
    print("Database Migration: Add has_consented field")
    print("=" * 60)
    migrate()
    print("=" * 60)
    print("Migration complete!")
