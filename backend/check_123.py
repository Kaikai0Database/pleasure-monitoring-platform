"""
檢查 123 帳號的詳細警告資訊
"""
from app.models import db, User, ScoreAlert, AssessmentHistory
from app.utils.alert_utils import calculate_moving_average, calculate_daily_average
from app import create_app
from datetime import date
import json

def check_123_account():
    """檢查 123 帳號"""
    
    user = User.query.filter_by(email='angel921030chen@gmail.com').first()
    
    if not user:
        print("❌ 找不到用戶")
        return
    
    print("=" * 80)
    print(f"用戶: {user.name} ({user.email})")
    print(f"ID: {user.id}")
    print("=" * 80)
    
    test_date = date(2026, 1, 5)
    
    # 計算當天平均
    daily_avg, count = calculate_daily_average(user.id, test_date)
    print(f"\n{test_date} 當日平均: {daily_avg} 分 (共 {count} 次測驗)")
    
    # 計算移動平均
    ma_7 = calculate_moving_average(user.id, 7, test_date)
    ma_14 = calculate_moving_average(user.id, 14, test_date)
    ma_30 = calculate_moving_average(user.id, 30, test_date)
    
    print(f"\n移動平均線:")
    print(f"  7日線:  {ma_7}")
    print(f"  14日線: {ma_14}")
    print(f"  30日線: {ma_30}")
    
    # 計算差距
    print(f"\n與移動平均線的差距:")
    if ma_7:
        diff_7 = ma_7 - daily_avg
        print(f"  7日線:  {diff_7:.1f} 分 ({daily_avg} vs {ma_7})")
    if ma_14:
        diff_14 = ma_14 - daily_avg
        print(f"  14日線: {diff_14:.1f} 分 ({daily_avg} vs {ma_14})")
    if ma_30:
        diff_30 = ma_30 - daily_avg
        print(f"  30日線: {diff_30:.1f} 分 ({daily_avg} vs {ma_30})")
    
    # 檢查觸發條件
    print(f"\n低分警告觸發條件 (0 < 差距 <= 3):")
    if ma_7:
        triggered_7 = 0 < diff_7 <= 3
        print(f"  7日線:  {triggered_7} (差距 {diff_7:.1f})")
    if ma_14:
        triggered_14 = 0 < diff_14 <= 3
        print(f"  14日線: {triggered_14} (差距 {diff_14:.1f})")
    if ma_30:
        triggered_30 = 0 < diff_30 <= 3
        print(f"  30日線: {triggered_30} (差距 {diff_30:.1f})")
    
    # 檢查實際創建的警告
    alert = ScoreAlert.query.filter_by(
        user_id=user.id,
        alert_date=test_date,
        alert_type='low'
    ).first()
    
    if alert:
        print(f"\n實際創建的低分警告:")
        print(f"  平均分數: {alert.daily_average}")
        print(f"  exceeded_lines: {alert.exceeded_lines}")
        
        try:
            lines = json.loads(alert.exceeded_lines)
            print(f"  觸發的線: {list(lines.keys())}")
            for line_name, line_value in lines.items():
                print(f"    {line_name}: {line_value}")
        except:
            pass
    else:
        print(f"\n⚠️  沒有找到 {test_date} 的低分警告")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        check_123_account()
