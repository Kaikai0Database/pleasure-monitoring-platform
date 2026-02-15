#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Create both High and Low alerts for testing
Creates two alerts on different days to show both alert types simultaneously
"""

from app import create_app, db
from app.models import User, AssessmentHistory, ScoreAlert
from datetime import datetime, date, timedelta
import json

app = create_app()

def create_dual_alerts():
    """Create both High and Low alerts for complete testing"""
    with app.app_context():
        # Find user
        user = User.query.filter_by(email='alert.test@example.com').first()
        if not user:
            print("ERROR: User not found!")
            return
        
        user_id = user.id
        print(f"User ID: {user_id}")
        
        # Clear existing alerts
        ScoreAlert.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        print("Cleared all existing alerts")
        
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Get current MA
        from app.utils.alert_utils import calculate_moving_average
        ma7_today = calculate_moving_average(user_id, 7, today)
        ma7_yesterday = calculate_moving_average(user_id, 7, yesterday)
        
        print(f"\nMA7 yesterday: {ma7_yesterday}")
        print(f"MA7 today: {ma7_today}")
        
        # Create yesterday's High Alert manually
        print("\n=== Creating Yesterday's High Alert ===")
        high_alert = ScoreAlert(
            user_id=user_id,
            alert_type='high',
            alert_date=yesterday,
            daily_average=37.0,  # High score
            exceeded_lines=json.dumps({
                "7日": round(ma7_yesterday, 1) if ma7_yesterday else 32.0,
                "14日": 32.0
            }),
            is_read=False
        )
        db.session.add(high_alert)
        db.session.commit()
        print(f"HIGH alert created: {high_alert.daily_average} > MA")
        print(f"  Lines: {high_alert.exceeded_lines}")
        
        # Verify today's Low Alert exists
        print("\n=== Checking Today's Low Alert ===")
        today_low = ScoreAlert.query.filter_by(
            user_id=user_id,
            alert_date=today,
            alert_type='low'
        ).first()
        
        if today_low:
            print(f"LOW alert exists: {today_low.daily_average}")
            print(f"  Lines: {today_low.exceeded_lines}")
        else:
            print("No Low alert found for today, creating one...")
            # Clear today's assessments
            AssessmentHistory.query.filter(
                AssessmentHistory.user_id == user_id,
                db.func.date(AssessmentHistory.completed_at) == today
            ).delete()
            
            # Create Low Alert scenario
            target_avg = ma7_today - 2 if ma7_today else 30
            scores = [int(target_avg - 1), int(target_avg), int(target_avg + 1)]
            
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
            
            db.session.commit()
            
            # Generate Low Alert
            from app.utils.alert_utils import check_and_create_alert
            alerts = check_and_create_alert(user_id, today)
            
            if alerts:
                print(f"LOW alert created: {alerts[0].daily_average}")
                print(f"  Lines: {alerts[0].exceeded_lines}")
        
        # Verify final state
        print("\n=== Final Alert Summary ===")
        all_alerts = ScoreAlert.query.filter_by(
            user_id=user_id,
            is_read=False
        ).order_by(ScoreAlert.alert_date.desc()).all()
        
        print(f"Total unread alerts: {len(all_alerts)}")
        for alert in all_alerts:
            print(f"  {alert.alert_date} - {alert.alert_type.upper()}: {alert.daily_average}")
        
        print("\n=== SUCCESS ===")
        print("Both High and Low alerts are now active!")
        print("\nExpected UI:")
        print("  🔔 Bell with red badge '1' (High Alert - yesterday)")
        print("  📉 Trend with blue badge '1' (Low Alert - today)")

def main():
    print("="*50)
    print("Dual Alert Test Data Generator")
    print("="*50)
    
    create_dual_alerts()
    
    print("\n" + "="*50)
    print("COMPLETE!")
    print("="*50)
    print("\nLogin and check both buttons:")
    print("  Account: alert.test@example.com")
    print("  Password: Alert123!")
    print("  Reload page with Ctrl+Shift+R")

if __name__ == '__main__':
    main()
