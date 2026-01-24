"""
觸發 1/5 的警告檢查
檢查是否創建低分警告
"""
from datetime import date
from app.models import db, User, ScoreAlert
from app.utils.alert_utils import check_and_create_alert
from app import create_app

def trigger_jan5_alerts():
    """觸發 1/5 的警告檢查"""
    
    test_date = date(2026, 1, 5)
    
    print("=" * 80)
    print("觸發 2026-01-05 的警告檢查")
    print("=" * 80)
    
    # 獲取所有用戶
    users = User.query.all()
    print(f"\n找到 {len(users)} 個用戶\n")
    
    total_high = 0
    total_low = 0
    
    for user in users:
        print(f"檢查用戶: {user.name} (ID: {user.id})")
        
        try:
            # 調用警告檢查函數
            alerts = check_and_create_alert(user.id, test_date)
            
            if alerts:
                for alert in alerts:
                    if alert.alert_type == 'high':
                        print(f"  🔔 創建高分警告 - 平均: {alert.daily_average}")
                        total_high += 1
                    else:
                        print(f"  📉 創建低分警告 - 平均: {alert.daily_average}")
                        total_low += 1
            else:
                print(f"  ℹ️  無需創建警告")
                
        except Exception as e:
            print(f"  ❌ 警告檢查失敗: {str(e)}")
    
    print("\n" + "=" * 80)
    print(f"✅ 警告檢查完成！")
    print(f"🔔 高分警告: {total_high} 個")
    print(f"📉 低分警告: {total_low} 個")
    print("=" * 80)
    
    print("\n📋 預期結果：")
    print("- 1/5 的測試數據分數低於30日線 2 分")
    print("- 應該創建多個「低分警告」（📉藍色）")
    print("- 不應該有「高分警告」（🔔紅色）")
    
    print("\n✅ 現在可以測試了：")
    print("1. 登入病人帳號 → 主選單應該看到藍色 📉")
    print("2. 點擊 📉 → 查看「低分預警」彈窗（藍色主題）")
    print("3. 登入管理員 → Dashboard/Watchlist 看到藍色 📉 圖標")
    print("4. 圖表標題旁應該**不顯示**「穿越XX線」（因為是低分）")
    
    # 顯示詳細的警告資訊
    print("\n" + "=" * 80)
    print("詳細警告列表：")
    print("=" * 80)
    
    all_alerts = ScoreAlert.query.filter_by(alert_date=test_date).all()
    for alert in all_alerts:
        user = User.query.get(alert.user_id)
        alert_type_display = '🔔 高分' if alert.alert_type == 'high' else '📉 低分'
        print(f"{alert_type_display} | {user.name} | 平均:{alert.daily_average} | 已讀:{alert.is_read}")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        trigger_jan5_alerts()
