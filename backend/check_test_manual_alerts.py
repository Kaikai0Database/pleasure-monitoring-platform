from app import create_app
from app.models import ScoreAlert, User
from datetime import date
import json

app = create_app()

with app.app_context():
    # 查找Test Manual
    user = User.query.filter_by(email='test_manual@gmail.com').first()
    
    if not user:
        print("找不到Test Manual帳號")
    else:
        print(f"Test Manual 警告狀態檢查")
        print("="*70)
        print(f"用戶ID: {user.id}")
        print(f"用戶名稱: {user.name}")
        
        # 獲取所有警告（包括已讀和未讀）
        all_alerts = ScoreAlert.query.filter_by(user_id=user.id).order_by(ScoreAlert.alert_date.desc()).all()
        
        print(f"\n所有警告總數: {len(all_alerts)}")
        
        if all_alerts:
            print("\n警告詳情：")
            for alert in all_alerts:
                try:
                    lines = json.loads(alert.exceeded_lines) if alert.exceeded_lines else {}
                except:
                    lines = {}
                
                read_status = "✓已讀" if alert.is_read else "❌未讀"
                alert_type_cn = "高分🔔" if alert.alert_type == 'high' else "低分📉"
                action = "穿越" if alert.alert_type == 'high' else "接近"
                
                print(f"  日期:{alert.alert_date} [{alert_type_cn}] {read_status}")
                print(f"    {action}: {', '.join([f'{k}線' for k in lines.keys()])}")
                print(f"    當日平均: {alert.daily_average}")
        
        # 檢查未讀警告
        unread_alerts = ScoreAlert.query.filter_by(
            user_id=user.id,
            is_read=False
        ).all()
        
        print(f"\n未讀警告數量: {len(unread_alerts)}")
        
        if len(unread_alerts) == 0:
            print("⚠️ 沒有未讀警告，這就是為什麼icon消失的原因！")
            print("\n可能原因：")
            print("1. 病患登入並查看了警告（手動標記為已讀）")
            print("2. 病患做了新測驗，觸發了自動清除邏輯")
            print("3. 警告被系統或腳本誤刪除")
        else:
            print("✓ 有未讀警告，應該要顯示icon")
            print("\n未讀警告：")
            for alert in unread_alerts:
                try:
                    lines = json.loads(alert.exceeded_lines) if alert.exceeded_lines else {}
                except:
                    lines = {}
                print(f"  {alert.alert_date}: [{alert.alert_type}] {list(lines.keys())}")
