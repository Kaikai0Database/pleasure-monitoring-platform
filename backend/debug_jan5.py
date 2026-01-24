"""
檢查並修復 1/5 警告問題
查看為何低分警告沒有被正確創建
"""
from app.models import db, User, ScoreAlert
from app.utils.alert_utils import check_and_create_alert
from app import create_app
from datetime import date

def debug_jan5_alerts():
    """調試 1/5 警告"""
    
    print("=" * 80)
    print("調試 2026-01-05 警告創建問題")
    print("=" * 80)
    
    test_date = date(2026, 1, 5)
    
    # 檢查特定用戶
    user = User.query.filter_by(email='trend_test@example.com').first()
    
    if not user:
        print("❌ 找不到用戶")
        return
    
    print(f"\n用戶: {user.name} (ID: {user.id})\n")
    
    # 先刪除舊的 1/5 警告
    old_alerts = ScoreAlert.query.filter_by(
        user_id=user.id,
        alert_date=test_date
    ).all()
    
    print(f"刪除舊的 1/5 警告: {len(old_alerts)} 個")
    for alert in old_alerts:
        db.session.delete(alert)
    db.session.commit()
    
    # 重新觸發警告檢查
    print(f"\n重新觸發 {test_date} 的警告檢查...")
    
    try:
        alerts = check_and_create_alert(user.id, test_date)
        
        if alerts:
            print(f"✅ 創建了 {len(alerts)} 個警告:")
            for alert in alerts:
                alert_type = '🔔 高分' if alert.alert_type == 'high' else '📉 低分'
                print(f"  {alert_type} | 平均: {alert.daily_average}")
                print(f"  exceeded_lines: {alert.exceeded_lines}")
        else:
            print("⚠️  沒有創建任何警告")
            
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 再次檢查所有警告
    print(f"\n{'=' * 80}")
    print(f"用戶 {user.name} 的所有警告:")
    print(f"{'=' * 80}")
    
    all_alerts = ScoreAlert.query.filter_by(user_id=user.id).order_by(ScoreAlert.alert_date).all()
    for alert in all_alerts:
        alert_type = '🔔 高分' if alert.alert_type == 'high' else '📉 低分'
        read_status = '已讀' if alert.is_read else '未讀'
        print(f"{alert_type} | {alert.alert_date} | 平均:{alert.daily_average} | {read_status}")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        debug_jan5_alerts()
