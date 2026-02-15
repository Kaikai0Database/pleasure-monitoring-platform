"""
清理非測試帳號的1月5日資料
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import User, ScoreAlert, AssessmentHistory, db
from datetime import datetime, date

app = create_app()

target_emails = [
    'test_manual@gmail.com',
    'angel921030chen@gmail.com',
    '111025015@live.asia.edu.tw',
    'test_update@example.com',
    '111025048@live.asia.edu.tw'
]

jan5 = date(2026, 1, 5)
jan6 = date(2026, 1, 6)

with app.app_context():
    print("清理非測試帳號的1月5日資料...")
    
    all_users = User.query.all()
    cleaned_count = 0
    
    for user in all_users:
        if user.email in target_emails:
            continue
        
        # 刪除1月5日的評估記錄
        jan5_assessments = AssessmentHistory.query.filter(
            AssessmentHistory.user_id == user.id,
            AssessmentHistory.completed_at >= datetime.combine(jan5, datetime.min.time()),
            AssessmentHistory.completed_at < datetime.combine(jan6, datetime.min.time())
        ).all()
        
        if jan5_assessments:
            print(f"清理 {user.name} ({user.email}): {len(jan5_assessments)} 筆記錄")
            for assessment in jan5_assessments:
                db.session.delete(assessment)
            cleaned_count += 1
        
        # 刪除1月5日的警報
        jan5_alerts = ScoreAlert.query.filter_by(
            user_id=user.id,
            alert_date=jan5
        ).all()
        
        if jan5_alerts:
            print(f"  同時刪除 {len(jan5_alerts)} 個警報")
            for alert in jan5_alerts:
                db.session.delete(alert)
    
    db.session.commit()
    print(f"\n完成！清理了 {cleaned_count} 個非測試帳號的1月5日資料")
