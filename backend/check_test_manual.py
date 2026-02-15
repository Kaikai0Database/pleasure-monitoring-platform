from app.models import db, User, ScoreAlert
from app.utils.alert_utils import calculate_moving_average, calculate_daily_average
from app import create_app
from datetime import date
import json

def check():
    user = User.query.filter_by(email='test_manual@gmail.com').first()
    test_date = date(2026, 1, 5)
    
    daily_avg, _ = calculate_daily_average(user.id, test_date)
    ma_7 = calculate_moving_average(user.id, 7, test_date)
    
    print(f"Daily: {daily_avg}")
    print(f"MA_7: {ma_7}")
    
    if ma_7:
        diff = ma_7 - daily_avg
        print(f"Diff: {diff}")
        print(f"Trigger (0 < diff <= 3): {0 < diff <= 3}")

    alert = ScoreAlert.query.filter_by(user_id=user.id, alert_date=test_date, alert_type='low').first()
    if alert:
        print(f"Alert Exceeded Lines: {alert.exceeded_lines}")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        check()
