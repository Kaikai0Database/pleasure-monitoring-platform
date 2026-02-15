"""
刪除 1/5 的所有警告並重新創建
"""
from app.models import db, User, ScoreAlert
from app.utils.alert_utils import check_and_create_alert
from app import create_app
from datetime import date

def recreate_jan5_alerts():
    """重新創建 1/5 警告"""
    
    test_date = date(2026, 1, 5)
    
    print("=" * 80)
    print(f"刪除並重新創建 {test_date} 的所有警告")
    print("=" * 80)
    
    # 刪除所有 1/5 的警告
    old_alerts = ScoreAlert.query.filter_by(alert_date=test_date).all()
    print(f"\n刪除舊警告: {len(old_alerts)} 個")
    
    for alert in old_alerts:
        user = User.query.get(alert.user_id)
        alert_type = '🔔' if alert.alert_type == 'high' else '📉'
        print(f"  {alert_type} {user.name} - 平均:{alert.daily_average}")
        db.session.delete(alert)
    
    db.session.commit()
    
    # 重新創建所有用戶的警告
    print(f"\n重新創建警告...")
    users = User.query.all()
    
    total_high = 0
    total_low = 0
    
    for user in users:
        alerts = check_and_create_alert(user.id, test_date)
        
        if alerts:
            for alert in alerts:
                if alert.alert_type == 'high':
                    print(f"  🔔 {user.name} - 平均:{alert.daily_average}")
                    total_high += 1
                else:
                    print(f"  📉 {user.name} - 平均:{alert.daily_average}")
                    total_low += 1
    
    print(f"\n✅ 完成！")
    print(f"  🔔 高分警告: {total_high} 個")
    print(f"  📉 低分警告: {total_low} 個")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        recreate_jan5_alerts()
