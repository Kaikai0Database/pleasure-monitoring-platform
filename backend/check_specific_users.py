"""
檢查特定用戶的警告狀態
"""
from app.models import db, User, ScoreAlert, AssessmentHistory
from app import create_app
from datetime import date

def check_specific_users():
    """檢查特定用戶"""
    
    print("=" * 80)
    print("檢查特定用戶的警告狀態")
    print("=" * 80)
    
    # 查找用戶
    user1 = User.query.filter_by(email='angel921030chen@gmail.com').first()
    user2 = User.query.filter_by(email='trend_test@example.com').first()
    
    users_to_check = []
    if user1:
        users_to_check.append(user1)
    else:
        print("\n❌ 找不到 angel921030chen@gmail.com")
    
    if user2:
        users_to_check.append(user2)
    else:
        print("\n❌ 找不到 trend_test@example.com")
    
    for user in users_to_check:
        print(f"\n{'=' * 80}")
        print(f"用戶: {user.name} ({user.email})")
        print(f"ID: {user.id}, 組別: {user.group}")
        print(f"{'=' * 80}")
        
        # 檢查 1/4 和 1/5 的評估記錄
        for test_date in [date(2026, 1, 4), date(2026, 1, 5)]:
            assessments = AssessmentHistory.query.filter(
                AssessmentHistory.user_id == user.id,
                db.func.date(AssessmentHistory.completed_at) == test_date,
                AssessmentHistory.deleted_at.is_(None)
            ).all()
            
            print(f"\n{test_date} 的評估記錄: {len(assessments)} 筆")
            for a in assessments:
                print(f"  - {a.completed_at.strftime('%H:%M')} | {a.total_score}/{a.max_score} | {a.level}")
        
        # 檢查警告記錄
        alerts = ScoreAlert.query.filter_by(user_id=user.id).all()
        print(f"\n警告記錄總數: {len(alerts)}")
        
        if alerts:
            for alert in alerts:
                alert_type_display = '🔔 高分' if alert.alert_type == 'high' else '📉 低分'
                read_status = '已讀' if alert.is_read else '未讀'
                print(f"  {alert_type_display} | {alert.alert_date} | 平均:{alert.daily_average} | {read_status}")
        else:
            print("  ⚠️  沒有任何警告記錄")
        
        # 檢查未讀警告
        unread_alerts = ScoreAlert.query.filter_by(
            user_id=user.id,
            is_read=False
        ).all()
        
        print(f"\n未讀警告數: {len(unread_alerts)}")
        if unread_alerts:
            for alert in unread_alerts:
                alert_type_display = '🔔' if alert.alert_type == 'high' else '📉'
                print(f"  {alert_type_display} {alert.alert_date} - 平均:{alert.daily_average}")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        check_specific_users()
