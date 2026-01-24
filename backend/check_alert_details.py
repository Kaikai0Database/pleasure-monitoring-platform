"""
查看警告詳細內容
"""
from datetime import date
from app.models import db, ScoreAlert, User
from app import create_app
import json

def check_alert_details():
    """查看警告詳細內容"""
    
    test_date = date(2026, 1, 4)
    
    print("=" * 80)
    print("查看 2026-01-04 的警告詳細內容")
    print("=" * 80)
    
    # 獲取所有警告
    alerts = ScoreAlert.query.filter(
        ScoreAlert.alert_date == test_date
    ).all()
    
    print(f"\n總警告數: {len(alerts)}\n")
    
    for alert in alerts:
        user = User.query.get(alert.user_id)
        print("-" * 80)
        print(f"用戶: {user.name} (ID: {alert.user_id})")
        print(f"警告類型: {'🔔 越線警告' if alert.alert_type == 'high' else '📉 低分警告'}")
        print(f"當天平均: {alert.daily_average} 分")
        print(f"已讀狀態: {'已讀' if alert.is_read else '未讀'}")
        
        # 解析 exceeded_lines
        try:
            lines = json.loads(alert.exceeded_lines)
            print(f"超過的移動平均線: ({len(lines)} 條)")
            for period, avg in lines.items():
                print(f"  • {period}平均: {avg} 分")
        except:
            print(f"exceeded_lines: {alert.exceeded_lines}")
    
    print("-" * 80)
    print(f"\n總結:")
    print(f"- 每個用戶有 1 個警告記錄")
    print(f"- 但每個警告記錄包含了多條被超過的線")
    print(f"- 這是目前的設計邏輯")
    print("\n如果您希望:")
    print("  越過 3 條線 = 顯示「3個越線警告」")
    print("  需要修改計數邏輯（計算 exceeded_lines 的數量）")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        check_alert_details()
