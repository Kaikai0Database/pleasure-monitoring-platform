#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Add Low Alert test data to existing user
Creates assessment data that triggers Low Alert (approaching MA lines)
"""

from app import create_app, db
from app.models import User, AssessmentHistory, ScoreAlert
from app.utils.alert_utils import check_and_create_alert
from datetime import datetime, date, timedelta
import json

app = create_app()

def create_low_alert_scenario():
    """Create data to trigger Low Alert for alert.test@example.com"""
    with app.app_context():
        # Find user
        user = User.query.filter_by(email='alert.test@example.com').first()
        if not user:
            print("ERROR: User not found!")
            return
        
        user_id = user.id
        print(f"Found user ID: {user_id}")
        
        # Clear today's data
        today = date.today()
        AssessmentHistory.query.filter(
            AssessmentHistory.user_id == user_id,
            db.func.date(AssessmentHistory.completed_at) == today
        ).delete()
        
        ScoreAlert.query.filter_by(
            user_id=user_id,
            alert_date=today
        ).delete()
        
        db.session.commit()
        print("Cleared today's data")
        
        # Get current MA values
        from app.utils.alert_utils import calculate_moving_average
        ma7 = calculate_moving_average(user_id, 7, today)
        ma14 = calculate_moving_average(user_id, 14, today)
        ma30 = calculate_moving_average(user_id, 30, today)
        
        print(f"\nCurrent MA values:")
        print(f"  MA7: {ma7}")
        print(f"  MA14: {ma14}")
        print(f"  MA30: {ma30}")
        
        # Calculate target scores for Low Alert
        # Low Alert: 0 < (MA - daily_avg) <= 3
        # We want daily_avg to be 1-2 points below MA
        
        if ma7:
            target_avg = ma7 - 2  # 2 points below MA7
        elif ma14:
            target_avg = ma14 - 2
        else:
            target_avg = 30  # Fallback
        
        # Create 3 assessments with scores around target
        scores = [
            int(target_avg - 1),  # Slightly below
            int(target_avg),      # At target
            int(target_avg + 1)   # Slightly above
        ]
        
        print(f"\nTarget average: {target_avg:.1f}")
        print(f"Creating scores: {scores}")
        print(f"Expected average: {sum(scores)/len(scores):.1f}")
        
        # Create today's assessments
        for i, score in enumerate(scores):
            assessment = AssessmentHistory(
                user_id=user_id,
                total_score=score,
                max_score=100,
                level='Good' if score < 29 else 'Attention',
                answers=json.dumps({
                    'q1': 2, 'q2': 2, 'q3': 2, 'q4': 2, 'q5': 2,
                    'q6': 2, 'q7': 2, 'q8': 2, 'q9': 2, 'q10': 2
                }),
                completed_at=datetime(
                    today.year, today.month, today.day,
                    8 if i == 0 else (12 if i == 1 else 17),
                    0 if i != 1 else 30, 0
                )
            )
            db.session.add(assessment)
            
            time_str = "08:00" if i == 0 else ("12:30" if i == 1 else "17:00")
            print(f"  {time_str}: {score}")
        
        db.session.commit()
        
        actual_avg = sum(scores) / len(scores)
        print(f"\nActual average: {actual_avg:.1f}")
        
        # Generate alerts
        print("\nGenerating alerts...")
        alerts = check_and_create_alert(user_id, today)
        
        if alerts:
            print(f"SUCCESS! Generated {len(alerts)} alert(s):")
            for alert in alerts:
                print(f"  Type: {alert.alert_type.upper()}")
                print(f"  Score: {alert.daily_average}")
                print(f"  Lines: {alert.exceeded_lines}")
                
                # Verify it's Low Alert
                if alert.alert_type == 'low':
                    print("\n  ✓ LOW ALERT successfully created!")
                    lines = alert.exceeded_lines
                    for period, ma_val in lines.items():
                        diff = ma_val - alert.daily_average
                        print(f"    {period}: MA={ma_val}, diff={diff:.1f}")
        else:
            print("WARNING: No alerts generated")
            print("\nDiagnostic info:")
            from app.utils.alert_utils import calculate_daily_average
            daily_avg, count = calculate_daily_average(user_id, today)
            print(f"  Daily avg: {daily_avg}")
            print(f"  Count: {count}")
            
            if ma7:
                diff7 = ma7 - daily_avg
                print(f"  MA7 diff: {diff7:.1f} (need 0 < diff <= 3)")
            if ma14:
                diff14 = ma14 - daily_avg
                print(f"  MA14 diff: {diff14:.1f} (need 0 < diff <= 3)")
            if ma30:
                diff30 = ma30 - daily_avg
                print(f"  MA30 diff: {diff30:.1f} (need 0 < diff <= 3)")

def main():
    print("="*50)
    print("Low Alert Test Data Generator")
    print("="*50)
    
    create_low_alert_scenario()
    
    print("\n" + "="*50)
    print("COMPLETE!")
    print("="*50)
    print("\nLogin and check:")
    print("  Account: alert.test@example.com")
    print("  Password: Alert123!")
    print("  Click the 📉 trend button to see Low Alert")

if __name__ == '__main__':
    main()
