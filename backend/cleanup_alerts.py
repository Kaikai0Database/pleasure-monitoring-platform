
from app import create_app, db
from app.models import User, ScoreAlert, AssessmentHistory
from app.utils.alert_utils import check_and_create_alert, calculate_moving_average, calculate_daily_average
import json
from sqlalchemy import desc

app = create_app()

def cleanup_alerts():
    with app.app_context():
        print("Starting alert cleanup...")
        users = User.query.all()
        
        for user in users:
            # Get latest assessment
            latest_assessment = AssessmentHistory.query.filter_by(
                user_id=user.id,
                is_deleted=False
            ).order_by(desc(AssessmentHistory.completed_at)).first()
            
            if not latest_assessment:
                continue
                
            print(f"Checking user {user.email} (Last assessment: {latest_assessment.completed_at.date()})")
            
            # Get all unread alerts for this user
            unread_alerts = ScoreAlert.query.filter_by(
                user_id=user.id,
                is_read=False
            ).all()
            
            if not unread_alerts:
                continue

            # Re-evaluate status based on LATEST assessment date
            # We can basically call check_and_create_alert for the latest date.
            # But wait, check_and_create_alert is designed to run when a NEW assessment is added.
            # It will:
            # 1. Mark past unread alerts as read (if date < latest_date)
            # 2. Update/Create/Delete alert for the latest_date
            
            # So, calling it for the latest assessment date should synchronize everything.
            created = check_and_create_alert(user.id, latest_assessment.completed_at.date())
            
            # Verify what happened
            current_alerts = ScoreAlert.query.filter_by(
                user_id=user.id,
                is_read=False
            ).all()
            
            count = len(current_alerts)
            print(f"  -> User now has {count} unread alerts.")

        print("Cleanup complete.")

if __name__ == "__main__":
    cleanup_alerts()
