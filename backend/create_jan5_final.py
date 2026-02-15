from app import create_app, db
from app.models import User, AssessmentHistory
from app.utils.alert_utils import calculate_moving_average, check_and_create_alert
from datetime import datetime, date
import random

app = create_app()

def create_alert_free_tests():
    """
    Create 3 assessments on Jan 5, 2026 for 5 users
    Target: AVOID BOTH HIGH and LOW alerts
    
    - HIGH alert: daily_avg > MA
    - LOW alert: 0 < (MA - daily_avg) <= 3
    
    Safe zone: daily_avg < (min_MA - 3)
    We'll target: min_MA - 3.5 to be safely in the middle
    """
    with app.app_context():
        # User emails
        target_users = [
            'test_manual@gmail.com',
            'angel921030chen@gmail.com',
            '111025015@live.asia.edu.tw',
            'test_update@example.com',
            '111025048@live.asia.edu.tw'
        ]
        
        # Times for assessments on Jan 5
        times = [
            datetime(2026, 1, 5, 6, 0, 0),   # 6 AM
            datetime(2026, 1, 5, 14, 0, 0),  # 2 PM
            datetime(2026, 1, 5, 21, 0, 0)   # 9 PM
        ]
        
        jan5 = date(2026, 1, 5)
        
        for email in target_users:
            user = User.query.filter_by(email=email).first()
            if not user:
                print(f"User not found: {email}")
                continue
            
            print(f"\n{'='*70}")
            print(f"Processing: {user.name} ({email})")
            
            # Delete existing Jan 5 assessments first
            existing = AssessmentHistory.query.filter(
                AssessmentHistory.user_id == user.id,
                db.func.date(AssessmentHistory.completed_at) == jan5
            ).all()
            
            if existing:
                print(f"Deleting {len(existing)} existing Jan 5 assessments...")
                for a in existing:
                    db.session.delete(a)
                db.session.commit()
            
            # Calculate MA values for Jan 5
            ma_7 = calculate_moving_average(user.id, 7, jan5)
            ma_14 = calculate_moving_average(user.id, 14, jan5)
            ma_30 = calculate_moving_average(user.id, 30, jan5)
            
            print(f"Moving Averages for Jan 5:")
            if ma_7: print(f"  7-day:  {ma_7:.2f}")
            if ma_14: print(f"  14-day: {ma_14:.2f}")
            if ma_30: print(f"  30-day: {ma_30:.2f}")
            
            # Get available MA values
            ma_values = [ma for ma in [ma_7, ma_14, ma_30] if ma is not None]
            
            if not ma_values:
                print("No MA values available - skipping")
                continue
            
            min_ma = min(ma_values)
            max_ma = max(ma_values)
            
            # Safe zone: MORE than 3 points below the minimum MA
            # Target: min_MA - 3.5 points (safely beyond LOW alert threshold)
            target_avg = min_ma - 3.5
            
            print(f"\nMA Range: {min_ma:.2f} to {max_ma:.2f}")
            print(f"Safe Zone Target: {target_avg:.2f} (= min_MA - 3.5)")
            
            # Determine user's group to get max_score
            if user.group == 'student':
                max_score = 56
            else:
                max_score = 40
            
            # Ensure target is not negative or too low
            if target_avg < 5:
                print(f"⚠️ Target too low ({target_avg:.2f}), adjusting to 5.0")
                target_avg = 5.0
            
            # Create 3 scores that average to target_avg
            variance = 1.0  # Small variance to keep close to target
            scores = []
            for i in range(3):
                if i < 2:
                    score = target_avg + random.uniform(-variance, variance)
                else:
                    # Last score calculated to hit exact average
                    score = (target_avg * 3) - sum(scores)
                
                # Ensure score is within valid range
                score = max(0, min(max_score, score))
                scores.append(round(score, 1))
            
            actual_avg = sum(scores) / len(scores)
            print(f"\nScores: {[int(s) for s in scores]}")
            print(f"Actual Daily Average: {actual_avg:.2f}")
            
            # Verify safe zone
            print(f"\nVerification:")
            has_issue = False
            for ma, name in [(ma_7, '7-day'), (ma_14, '14-day'), (ma_30, '30-day')]:
                if ma:
                    diff = ma - actual_avg
                    if actual_avg > ma:
                        print(f"  {name}: ❌ HIGH ALERT (daily > MA)")
                        has_issue = True
                    elif 0 < diff <= 3:
                        print(f"  {name}: ❌ LOW ALERT (diff={diff:.2f} <= 3)")
                        has_issue = True
                    else:
                        print(f"  {name}: ✓ Safe (diff={diff:.2f})")
            
            if has_issue:
                print("⚠️ WARNING: This configuration may still trigger alerts!")
            
            # Determine Chinese level based on average
            if user.group == 'student':
                if actual_avg >= 42:
                    level = '健康'
                elif actual_avg >= 28:
                    level = '潛在憂鬱風險'
                else:
                    level = '憂鬱'
            else:
                if actual_avg >= 30:
                    level = '健康'
                elif actual_avg >= 20:
                    level = '潛在憂鬱風險'
                else:
                    level = '憂鬱'
            
            # Create assessments
            for i, (score, timestamp) in enumerate(zip(scores, times)):
                assessment = AssessmentHistory(
                    user_id=user.id,
                    total_score=int(score),
                    max_score=max_score,
                    level=level,
                    completed_at=timestamp,
                    is_deleted=False
                )
                db.session.add(assessment)
            
            db.session.commit()
            print("✓ Assessments created")
            
            # Trigger alert check
            print("\nRunning alert check...")
            created_alerts = check_and_create_alert(user.id, jan5)
            
            if created_alerts:
                print(f"⚠️ Created {len(created_alerts)} alert(s) - UNEXPECTED!")
                for alert in created_alerts:
                    print(f"  - Type: {alert.alert_type}, Lines: {alert.exceeded_lines}")
            else:
                print("✅ No alerts created - SUCCESS!")
        
        print(f"\n{'='*70}")
        print("All users processed!")
        print("\nExpected result:")
        print("- All 5 users should have NO unread alerts")
        print("- Refresh admin dashboard to verify bells are gone")

if __name__ == "__main__":
    create_alert_free_tests()
