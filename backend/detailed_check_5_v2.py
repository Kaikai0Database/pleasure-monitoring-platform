from app import create_app
from app.models import ScoreAlert, User, AssessmentHistory
from app.utils.alert_utils import calculate_moving_average, calculate_daily_average
from datetime import date
import json

app = create_app()

target_emails = [
    'test_manual@gmail.com',
    'angel921030chen@gmail.com',
    '111025015@live.asia.edu.tw',
    'test_update@example.com',
    '111025048@live.asia.edu.tw'
]

jan5 = date(2026, 1, 5)

with app.app_context():
    print("DETAILED STATUS FOR 5 TARGET USERS\n")
    
    for email in target_emails:
        user = User.query.filter_by(email=email).first()
        if not user:
            continue
        
        print(f"{user.name} ({email})")
        print("-" * 70)
        
        # MA values
        ma_7 = calculate_moving_average(user.id, 7, jan5)
        ma_14 = calculate_moving_average(user.id, 14, jan5)
        ma_30 = calculate_moving_average(user.id, 30, jan5)
        
        # Daily average
        daily_avg, count = calculate_daily_average(user.id, jan5)
        
        ma_7_str = f"{ma_7:.2f}" if ma_7 else "N/A"
        ma_14_str = f"{ma_14:.2f}" if ma_14 else "N/A"
        ma_30_str = f"{ma_30:.2f}" if ma_30 else "N/A"
        daily_str = f"{daily_avg:.2f}" if daily_avg else "N/A"
        
        print(f"MA: 7d={ma_7_str}, 14d={ma_14_str}, 30d={ma_30_str}")
        print(f"Daily Avg: {daily_str}")
        
        # Check each MA
        if daily_avg:
            for ma, name in [(ma_7, '7d'), (ma_14, '14d'), (ma_30, '30d')]:
                if ma:
                    diff = ma - daily_avg
                    if daily_avg > ma:
                        print(f"  {name}: ❌ HIGH (daily {daily_avg:.2f} > {ma:.2f})")
                    elif 0 < diff <= 3:
                        print(f"  {name}: ⚠️ LOW ALERT (diff={diff:.2f})")
                    else:
                        print(f"  {name}: ✓ Safe (diff={diff:.2f})")
        
        # Alerts
        alerts = ScoreAlert.query.filter_by(user_id=user.id, is_read=False).all()
        print(f"Unread Alerts: {len(alerts)}")
        for alert in alerts:
            try:
                lines = json.loads(alert.exceeded_lines)
            except:
                lines = {}
            print(f"  [{alert.alert_type.upper()}] {alert.alert_date}: {list(lines.keys())}")
        
        print()
