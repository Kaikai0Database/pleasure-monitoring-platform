"""
檢查測試數據是否創建成功
"""
from datetime import datetime, date
from app.models import db, User, AssessmentHistory, ScoreAlert
from app import create_app

def check_test_data():
    """檢查 2026-01-04 的測試數據"""
    
    test_date = date(2026, 1, 4)
    
    print("=" * 70)
    print("檢查測試數據 (2026-01-04)")
    print("=" * 70)
    
    # 獲取所有用戶
    users = User.query.all()
    print(f"\n總用戶數: {len(users)}")
    
    # 檢查每個用戶的評估記錄
    print("\n" + "-" * 70)
    print(f"{'用戶名':<15} {'Email':<25} {'評估數':<10} {'警告數'}")
    print("-" * 70)
    
    for user in users:
        # 查詢該用戶在測試日期的評估數
        assessments = AssessmentHistory.query.filter(
            AssessmentHistory.user_id == user.id,
            AssessmentHistory.deleted_at.is_(None),
            db.func.date(AssessmentHistory.completed_at) == test_date
        ).all()
        
        # 查詢該用戶在測試日期的警告數
        alerts = ScoreAlert.query.filter(
            ScoreAlert.user_id == user.id,
            ScoreAlert.alert_date == test_date
        ).all()
        
        # 分類警告
        high_alerts = [a for a in alerts if a.alert_type == 'high']
        low_alerts = [a for a in alerts if a.alert_type == 'low']
        
        alert_info = ""
        if high_alerts:
            alert_info += f"🔔{len(high_alerts)} "
        if low_alerts:
            alert_info += f"📉{len(low_alerts)}"
        if not alert_info:
            alert_info = "-"
        
        print(f"{user.name[:15]:<15} {user.email[:25]:<25} {len(assessments):<10} {alert_info}")
        
        # 顯示評估詳情
        if assessments:
            for i, a in enumerate(assessments, 1):
                time_str = a.completed_at.strftime('%H:%M')
                print(f"  {i}. {time_str} - {a.total_score}/{a.max_score} 分")
        
        # 顯示警告詳情
        if alerts:
            for alert in alerts:
                alert_type_icon = "🔔" if alert.alert_type == 'high' else "📉"
                alert_type_name = "高分" if alert.alert_type == 'high' else "低分"
                lines = ', '.join(alert.exceeded_lines) if isinstance(alert.exceeded_lines, list) else alert.exceeded_lines
                print(f"  {alert_type_icon} {alert_type_name}警告: 平均 {alert.daily_average} 分")
    
    print("-" * 70)
    
    # 統計總數
    total_assessments = AssessmentHistory.query.filter(
        AssessmentHistory.deleted_at.is_(None),
        db.func.date(AssessmentHistory.completed_at) == test_date
    ).count()
    
    total_alerts = ScoreAlert.query.filter(
        ScoreAlert.alert_date == test_date
    ).count()
    
    high_count = ScoreAlert.query.filter(
        ScoreAlert.alert_date == test_date,
        ScoreAlert.alert_type == 'high'
    ).count()
    
    low_count = ScoreAlert.query.filter(
        ScoreAlert.alert_date == test_date,
        ScoreAlert.alert_type == 'low'
    ).count()
    
    print(f"\n總評估記錄數: {total_assessments}")
    print(f"總警告數: {total_alerts}")
    print(f"  🔔 高分警告: {high_count}")
    print(f"  📉 低分警告: {low_count}")
    print("=" * 70)

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        check_test_data()
