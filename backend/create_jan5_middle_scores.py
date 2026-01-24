from app import create_app, db
from app.models import User, AssessmentHistory
from app.utils.alert_utils import calculate_moving_average, check_and_create_alert
from datetime import datetime, date
import random

app = create_app()

def create_middle_score_tests():
    """
    Create 3 assessments on Jan 5, 2026 for 5 users
    Each user's daily average will be between their lowest and highest MA lines
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
            
            print(f"\n{'='*60}")
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
            
            # Calculate MA values for Jan 5 (based on data up to Jan 4)
            # We need to calculate as if we're on Jan 5
            ma_7 = calculate_moving_average(user.id, 7, jan5)
            ma_14 = calculate_moving_average(user.id, 14, jan5)
            ma_30 = calculate_moving_average(user.id, 30, jan5)
            
            print(f"Moving Averages for Jan 5:")
            print(f"  7-day:  {ma_7}")
            print(f"  14-day: {ma_14}")
            print(f"  30-day: {ma_30}")
            
            # Get available MA values
            ma_values = [ma for ma in [ma_7, ma_14, ma_30] if ma is not None]
            
            if not ma_values:
                print("No MA values available - creating random scores")
                target_avg = 35.0
            else:
                min_ma = min(ma_values)
                max_ma = max(ma_values)
                
                # Target: between min and max MA
                # Add some buffer to ensure it's clearly in the middle
                buffer = (max_ma - min_ma) * 0.2  # 20% buffer from edges
                target_avg = min_ma + buffer + random.uniform(0, max_ma - min_ma - 2*buffer)
                
                print(f"\nTarget daily average: {target_avg:.1f}")
                print(f"  (Between {min_ma:.1f} and {max_ma:.1f})")
            
            # Determine user's group to get max_score
            if user.group == 'student':
                max_score = 56
            else:
                max_score = 40
            
            # Create 3 scores that average to target_avg
            # Add some variance but keep the average
            variance = 3.0
            scores = []
            for i in range(3):
                if i < 2:
                    # Random variation for first 2 scores
                    score = target_avg + random.uniform(-variance, variance)
                else:
                    # Last score calculated to hit exact average
                    score = (target_avg * 3) - sum(scores)
                
                # Ensure score is within valid range
                score = max(0, min(max_score, score))
                scores.append(round(score, 1))
            
            actual_avg = sum(scores) / len(scores)
            print(f"\nCreating 3 assessments with scores: {scores}")
            print(f"Actual daily average: {actual_avg:.1f}")
            
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
                print(f"  [{i+1}] {timestamp.strftime('%H:%M')}: Score {score:.1f}")
            
            db.session.commit()
            print("✓ Assessments created")
            
            # Trigger alert check
            print("\nRunning alert check...")
            created_alerts = check_and_create_alert(user.id, jan5)
            
            if created_alerts:
                print(f"⚠ Created {len(created_alerts)} alert(s) - this shouldn't happen!")
                for alert in created_alerts:
                    print(f"  - Type: {alert.alert_type}, Lines: {alert.exceeded_lines}")
            else:
                print("✓ No alerts created (as expected - score in middle range)")
        
        print(f"\n{'='*60}")
        print("All users processed successfully!")
        print("\nNext steps:")
        print("1. Refresh the admin dashboard")
        print("2. All alert bells should disappear for these 5 users")
        print("3. Check charts to verify scores are between MA lines")

if __name__ == "__main__":
    create_middle_score_tests()
