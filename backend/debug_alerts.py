"""
檢查病人的警告資訊
"""
from datetime import date
from app.models import db, ScoreAlert, User
from app import create_app
import json

def check_patient_alerts():
    """檢查病人警告"""
    
    print("=" * 70)
    print("檢查病人警告狀態")
    print("=" * 70)
    
    # 獲取所有用戶和他們的未讀警告
    users = User.query.all()
    
    for user in users:
        alerts = ScoreAlert.query.filter_by(
            user_id=user.id,
            is_read=False,
            alert_type='high'
        ).all()
        
        if alerts:
            print(f"\n用戶: {user.name} (ID: {user.id})")
            print(f"未讀高分警告數: {len(alerts)}")
            
            for alert in alerts:
                print(f"\n  警告 ID: {alert.id}")
                print(f"  日期: {alert.alert_date}")
                print(f"  平均分數: {alert.daily_average}")
                print(f"  exceeded_lines 原始: {alert.exceeded_lines}")
                print(f"  exceeded_lines 類型: {type(alert.exceeded_lines)}")
                
                try:
                    lines = json.loads(alert.exceeded_lines)
                    print(f"  解析後: {lines}")
                    print(f"  線的名稱: {list(lines.keys())}")
                except Exception as e:
                    print(f"  解析錯誤: {e}")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        check_patient_alerts()
