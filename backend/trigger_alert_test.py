"""
測試腳本：手動觸發警報檢查（測試模式）
使用放寬的驗證條件
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.utils.alert_utils_test import check_and_create_alert_test
from datetime import date

app = create_app()

with app.app_context():
    # 使用 test.patient@example.com 的 user_id
    # 請根據實際情況修改 user_id
    
    print("=" * 60)
    print("測試模式警報觸發器")
    print("=" * 60)
    
    user_id = int(input("請輸入用戶 ID (例如: 1): "))
    
    # 使用今天的日期
    today = date.today()
    
    print(f"\n正在為用戶 {user_id} 檢查 {today} 的警報...")
    print("(測試模式: 只需 1 次評估 + 1 天數據)\n")
    
    created_alerts = check_and_create_alert_test(user_id, today)
    
    print("=" * 60)
    print(f"完成! 創建了 {len(created_alerts)} 個警報")
    print("=" * 60)
    
    if created_alerts:
        for alert in created_alerts:
            print(f"\n警報類型: {alert.alert_type}")
            print(f"當日平均: {alert.daily_average}")
            print(f"超過的線: {alert.exceeded_lines}")
    else:
        print("\n未創建任何新警報（可能已存在或不符合條件）")
