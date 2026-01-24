"""
手動觸發警告檢查
為所有用戶在 2026-01-04 檢查並創建警告
"""
from datetime import date
from app.models import db, User
from app.utils.alert_utils import check_and_create_alert
from app import create_app

def trigger_alert_check():
    """手動觸發警告檢查"""
    
    test_date = date(2026, 1, 4)
    
    print("=" * 70)
    print("手動觸發警告檢查")
    print(f"檢查日期: {test_date}")
    print("=" * 70)
    
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
    
    print("\n" + "=" * 70)
    print(f"✅ 警告檢查完成！")
    print(f"🔔 高分警告: {total_high} 個")
    print(f"📉 低分警告: {total_low} 個")
    print("=" * 70)
    
    print("\n📋 預期結果：")
    print("- 56分是滿分，應該遠高於歷史移動平均線")
    print("- 應該創建多個「高分警告」（🔔紅色）")
    print("- 理論上不應該有「低分警告」（📉藍色）")
    
    print("\n✅ 現在可以測試了：")
    print("1. 登入病人帳號 → 主選單應該看到紅色鈴鐺🔔")
    print("2. 點擊鈴鐺 → 查看「高分警示」彈窗")
    print("3. 登入管理員 → Dashboard/Watchlist 看到紅色鈴鐺圖標")
    

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        trigger_alert_check()
