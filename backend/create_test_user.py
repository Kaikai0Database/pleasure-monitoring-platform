#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test user creation script with alert data
Creates a complete test account that triggers High Alert

Account: alert.test@example.com
Password: Alert123!
"""

from app import create_app, db
from app.models import User, AssessmentHistory, ScoreAlert
from app.utils.alert_utils import check_and_create_alert
from werkzeug.security import generate_password_hash
from datetime import datetime, date, timedelta
import json

app = create_app()

def create_test_user():
    """Create test user"""
    with app.app_context():
        existing_user = User.query.filter_by(email='alert.test@example.com').first()
        if existing_user:
            print(f"User exists, using existing user")
            print(f"   ID: {existing_user.id}")
            print(f"   Email: {existing_user.email}")
            return existing_user.id
        
        # Note: User model uses 'name' not 'username', 'password_hash' not 'password'
        new_user = User(
            name='Alert Test User',  # Use 'name'
            email='alert.test@example.com',
            password_hash=generate_password_hash('Alert123!'),  # Use 'password_hash'
            group='clinical'
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        print(f"User created successfully!")
        print(f"   ID: {new_user.id}")
        print(f"   Account: alert.test@example.com") 
        print(f"   Password: Alert123!")
        
        return new_user.id

def clear_old_data(user_id):
    """Clear old data"""
    with app.app_context():
        print("\nClearing old data...")
        
        deleted_assessments = AssessmentHistory.query.filter_by(user_id=user_id).delete()
        print(f"   Deleted {deleted_assessments} assessments")
        
        deleted_alerts = ScoreAlert.query.filter_by(user_id=user_id).delete()
        print(f"   Deleted {deleted_alerts} alerts")
        
        db.session.commit()
        print("   Cleared")

def create_historical_data(user_id):
    """Create 7 days of historical data"""
    with app.app_context():
        print("\nCreating historical assessment data...")
        
        historical_scores = [
            [30, 32, 34],
            [31, 33, 35],
            [29, 31, 33],
            [30, 32, 34],
            [31, 33, 35],
            [30, 32, 34],
            [29, 31, 33],
        ]
        
        for days_ago in range(7, 0, -1):
            assess_date = date.today() - timedelta(days=days_ago)
            day_index = 7 - days_ago
            scores = historical_scores[day_index]
            
            for i, score in enumerate(scores):
                assessment = AssessmentHistory(
                    user_id=user_id,
                    total_score=score,
                    max_score=100,
                    level='Good' if score < 29 else 'Attention',
                    answers=json.dumps({'q1': 2, 'q2': 2, 'q3': 2, 'q4': 2, 'q5': 2,
                                       'q6': 2, 'q7': 2, 'q8': 2, 'q9': 2, 'q10': 2}),
                    completed_at=datetime(
                        assess_date.year, assess_date.month, assess_date.day,
                        8 if i == 0 else (12 if i == 1 else 17),
                        0 if i != 1 else 30, 0
                    )
                )
                db.session.add(assessment)
            
            day_avg = sum(scores) / len(scores)
            print(f"   {assess_date}: {scores} -> avg {day_avg:.1f}")
        
        db.session.commit()
        print("   Historical data created!")

def create_today_data(user_id):
    """Create today's data (triggers High Alert)"""
    with app.app_context():
        print("\nCreating today's high score data...")
        
        today = date.today()
        today_scores = [35, 37, 39]  # avg 37.0
        
        for i, score in enumerate(today_scores):
            assessment = AssessmentHistory(
                user_id=user_id,
                total_score=score,
                max_score=100,
                level='Attention',
                answers=json.dumps({'q1': 3, 'q2': 3, 'q3': 3, 'q4': 3, 'q5': 3,
                                   'q6': 3, 'q7': 3, 'q8': 3, 'q9': 3, 'q10': 3}),
                completed_at=datetime(
                    today.year, today.month, today.day,
                    8 if i == 0 else (12 if i == 1 else 17),
                    0 if i != 1 else 30, 0
                )
            )
            db.session.add(assessment)
            
            time_str = "08:00" if i == 0 else ("12:30" if i == 1 else "17:00")
            print(f"   {time_str}: {score}")
        
        db.session.commit()
        today_avg = sum(today_scores) / len(today_scores)
        print(f"   Today's avg: {today_avg:.1f}")

def generate_alerts(user_id):
    """Generate alerts"""
    with app.app_context():
        print("\nGenerating alerts...")
        
        try:
            alerts = check_and_create_alert(user_id, date.today())
            
            if alerts:
                print(f"   Generated {len(alerts)} alerts!")
                for alert in alerts:
                    print(f"      Type: {alert.alert_type.upper()}")
                    print(f"      Score: {alert.daily_average}")
                    print(f"      Lines: {alert.exceeded_lines}")
            else:
                print("   No alerts generated")
        except Exception as e:
            print(f"   Alert generation failed: {e}")

def verify_user(user_id):
    """Verify user can login"""
    with app.app_context():
        print("\nVerifying user...")
        
        user = User.query.get(user_id)
        if user:
            print(f"   User exists")
            print(f"      ID: {user.id}")
            print(f"      Email: {user.email}")
            print(f"      Name: {user.name}")
            print(f"      Group: {user.group}")
            
            from werkzeug.security import check_password_hash
            is_valid = check_password_hash(user.password_hash, 'Alert123!')
            print(f"      Password: {'OK' if is_valid else 'FAIL'}")
        else:
            print(f"   User not found: {user_id}")

def main():
    print("="*50)
    print("Test User & Alert Data Generator")
    print("="*50)
    
    try:
        user_id = create_test_user()
        clear_old_data(user_id)
        create_historical_data(user_id)
        create_today_data(user_id)
        generate_alerts(user_id)
        verify_user(user_id)
        
        print("\n" + "="*50)
        print("COMPLETE!")
        print("="*50)
        print("\nLogin Info:")
        print(f"   Account: alert.test@example.com")
        print(f"   Password: Alert123!")
        print(f"   URL: http://localhost:5173/login")
        
    except Exception as e:
        print(f"\nFailed: {e}")

if __name__ == '__main__':
    main()
