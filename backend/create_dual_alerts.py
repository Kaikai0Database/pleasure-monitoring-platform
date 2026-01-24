from app import create_app, db
from app.models import User, AssessmentHistory, ScoreAlert
from app.utils.alert_utils import calculate_moving_average, check_and_create_alert
from datetime import datetime, date
import random

app = create_app()

def create_dual_alert_tests():
    """
    創建同時觸發HIGH和LOW警告的測試資料
    
    策略：將當日平均設定在不同MA線之間
    - 高於某些線（如7日線）→ HIGH alert
    - 接近另一些線（如30日線），差距≤3 → LOW alert
    """
    with app.app_context():
        target_users = [
            'test_manual@gmail.com',
            'angel921030chen@gmail.com',
            '111025015@live.asia.edu.tw',
            'test_update@example.com',
            '111025048@live.asia.edu.tw'
        ]
        
        times = [
            datetime(2026, 1, 5, 6, 0, 0),   # 6 AM
            datetime(2026, 1, 5, 14, 0, 0),  # 2 PM
            datetime(2026, 1, 5, 21, 0, 0)   # 9 PM
        ]
        
        jan5 = date(2026, 1, 5)
        
        for email in target_users:
            user = User.query.filter_by(email=email).first()
            if not user:
                print(f"找不到用戶: {email}")
                continue
            
            print(f"\n{'='*70}")
            print(f"處理中: {user.name} ({email})")
            
            # 刪除現有的1/5資料
            existing_assessments = AssessmentHistory.query.filter(
                AssessmentHistory.user_id == user.id,
                db.func.date(AssessmentHistory.completed_at) == jan5
            ).all()
            
            if existing_assessments:
                print(f"刪除 {len(existing_assessments)} 筆現有的1/5測驗...")
                for a in existing_assessments:
                    db.session.delete(a)
            
            # 刪除現有的1/5警告
            existing_alerts = ScoreAlert.query.filter(
                ScoreAlert.user_id == user.id,
                ScoreAlert.alert_date == jan5
            ).all()
            
            if existing_alerts:
                print(f"刪除 {len(existing_alerts)} 筆現有的1/5警告...")
                for a in existing_alerts:
                    db.session.delete(a)
            
            db.session.commit()
            
            # 計算移動平均
            ma_7 = calculate_moving_average(user.id, 7, jan5)
            ma_14 = calculate_moving_average(user.id, 14, jan5)
            ma_30 = calculate_moving_average(user.id, 30, jan5)
            
            print(f"\n移動平均線數值：")
            print(f"  7日線:  {ma_7:.2f}" if ma_7 else "  7日線:  無")
            print(f"  14日線: {ma_14:.2f}" if ma_14 else "  14日線: 無")
            print(f"  30日線: {ma_30:.2f}" if ma_30 else "  30日線: 無")
            
            ma_values = [ma for ma in [ma_7, ma_14, ma_30] if ma is not None]
            
            if len(ma_values) < 2:
                print("移動平均線數量不足，跳過此用戶")
                continue
            
            # 排序找出最小和最大值
            ma_sorted = sorted(ma_values)
            min_ma = ma_sorted[0]
            max_ma = ma_sorted[-1]
            
            # 目標：在中間某個位置，使得：
            # 1. 高於最小的MA（觸發HIGH）
            # 2. 接近最大的MA，差距在3分以內（觸發LOW）
            # 
            # 理想位置：max_ma - 2（距離最大MA 2分，觸發LOW）
            # 同時要確保這個值大於最小的MA
            
            target_avg = max_ma - 2.0
            
            # 確保target_avg確實大於最小的MA
            if target_avg <= min_ma:
                # 如果差距太小，調整到 min_ma + 1 和 max_ma - 2 之間
                target_avg = (min_ma + max_ma) / 2
            
            print(f"\n目標策略：")
            print(f"  最小MA: {min_ma:.2f}")
            print(f"  最大MA: {max_ma:.2f}")
            print(f"  目標平均: {target_avg:.2f}")
            
            # 獲取max_score
            max_score = 56 if user.group == 'student' else 40
            
            # 確保target在有效範圍內
            if target_avg < 1:
                target_avg = (min_ma + max_ma) / 2
            if target_avg > max_score:
                target_avg = max_score - 5
            
            # 創建3個分數
            variance = 0.5
            scores = []
            for i in range(3):
                if i < 2:
                    score = target_avg + random.uniform(-variance, variance)
                else:
                    score = (target_avg * 3) - sum(scores)
                
                score = max(0, min(max_score, score))
                scores.append(round(score, 1))
            
            actual_avg = sum(scores) / len(scores)
            print(f"\n創建分數: {[int(s) for s in scores]}")
            print(f"實際當日平均: {actual_avg:.2f}")
            
            # 預測警告
            print(f"\n預測警告狀況：")
            will_have_high = False
            will_have_low = False
            
            for ma, name in [(ma_7, '7日'), (ma_14, '14日'), (ma_30, '30日')]:
                if ma:
                    if actual_avg > ma:
                        print(f"  {name}線: ✓ 高分警告 (當日 {actual_avg:.2f} > {ma:.2f})")
                        will_have_high = True
                    
                    diff = ma - actual_avg
                    if 0 < diff <= 3:
                        print(f"  {name}線: ✓ 低分警告 (差距 {diff:.2f} ≤ 3)")
                        will_have_low = True
            
            if will_have_high and will_have_low:
                print("\n✅ 預期會同時觸發高分和低分警告！")
            elif will_have_high:
                print("\n⚠️ 僅會觸發高分警告")
            elif will_have_low:
                print("\n⚠️ 僅會觸發低分警告")
            else:
                print("\n❌ 不會觸發任何警告")
            
            # 決定level
            if user.group == 'student':
                if actual_avg >= 42:
                    level = '健康'
                elif actual_avg >= 28:
                    level = '潛在憂鬱風險'
                else:
                    level = '憂鬱'
            else:
                if actual_avg >= 30:
                    level = '健康'
                elif actual_avg >= 20:
                    level = '潛在憂鬱風險'
                else:
                    level = '憂鬱'
            
            # 創建測驗記錄
            for i, (score, timestamp) in enumerate(zip(scores, times)):
                assessment = AssessmentHistory(
                    user_id=user.id,
                    total_score=int(score),
                    max_score=max_score,
                    level=level,
                    completed_at=timestamp,
                    is_deleted=False
                )
                db.session.add(assessment)
            
            db.session.commit()
            print("✓ 測驗記錄已創建")
            
            # 觸發警告檢查
            print("\n執行警告檢查...")
            created_alerts = check_and_create_alert(user.id, jan5)
            
            if created_alerts:
                print(f"✓ 創建了 {len(created_alerts)} 個警告：")
                for alert in created_alerts:
                    import json
                    try:
                        lines = json.loads(alert.exceeded_lines)
                    except:
                        lines = {}
                    alert_name = "🔔 高分" if alert.alert_type == 'high' else "📉 低分"
                    print(f"  {alert_name}: {list(lines.keys())}")
            else:
                print("❌ 未創建警告（不符合預期）")
        
        print(f"\n{'='*70}")
        print("所有用戶處理完成！")
        print("\n請重新整理管理員頁面，應該能看到：")
        print("1. 病患列表：同時顯示 🔔 和 📉 圖標")
        print("2. 病患詳情頁圖表：同時顯示「穿越...」和「接近...」")

if __name__ == "__main__":
    create_dual_alert_tests()
