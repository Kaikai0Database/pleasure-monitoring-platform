"""
重新生成Tester帳號的1月5日資料，確保觸發雙警報
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import User, ScoreAlert, AssessmentHistory,db
from app.utils.alert_utils import calculate_moving_average, check_and_create_alert
from datetime import datetime, date, time
import json

app = create_app()

jan5 = date(2026, 1, 5)

with app.app_context():
    user = User.query.filter_by(email='test_update@example.com').first()
    
    if not user:
        print("ERROR: Tester account not found!")
    else:
        print(f"重新生成Tester ({user.name}) 的1月5日資料...")
        
        # 1. 刪除現有的1月5日資料
        jan5_assessments = AssessmentHistory.query.filter(
            AssessmentHistory.user_id == user.id,
            AssessmentHistory.completed_at >= datetime.combine(jan5, time.min),
            AssessmentHistory.completed_at < datetime.combine(date(2026, 1, 6), time.min)
        ).all()
        
        print(f"刪除 {len(jan5_assessments)} 筆現有評估記錄...")
        for assessment in jan5_assessments:
            db.session.delete(assessment)
        
        jan5_alerts = ScoreAlert.query.filter_by(
            user_id=user.id,
            alert_date=jan5
        ).all()
        
        print(f"刪除 {len(jan5_alerts)} 個現有警報...")
        for alert in jan5_alerts:
            db.session.delete(alert)
        
        db.session.commit()
        
        # 2. 計算移動平均
        ma_7 = calculate_moving_average(user.id, 7, jan5)
        ma_14 = calculate_moving_average(user.id, 14, jan5)
        ma_30 = calculate_moving_average(user.id, 30, jan5)
        
        print(f"\n移動平均:")
        print(f"  7日:  {f'{ma_7:.2f}' if ma_7 else 'None'}")
        print(f"  14日: {f'{ma_14:.2f}' if ma_14 else 'None'}")
        print(f"  30日: {f'{ma_30:.2f}' if ma_30 else 'None'}")
        
        # 3. 計算目標平均值
        # 需要: 高於某些線（觸發high），接近某些線（觸發low，差距在3以內）
        # 策略: 設定在14日線和30日線之間，且接近7日線
        # 例如: ma_7=41.52, ma_14=38.52, ma_30=38.19
        # 目標: 39.5 (高於14和30日線，與7日線差2點 - 會觸發low alert)
        
        target_avg = 39.5
        
        print(f"\n目標平均: {target_avg}")
        print(f"預期觸發:")
        if ma_14 and target_avg > ma_14:
            print(f"  ✓ HIGH: 穿越14日線 (diff: {target_avg - ma_14:.2f})")
        if ma_30 and target_avg > ma_30:
            print(f"  ✓ HIGH: 穿越30日線 (diff: {target_avg - ma_30:.2f})")
        if ma_7:
            diff = ma_7 - target_avg
            if 0 < diff <= 3:
                print(f"  ✓ LOW: 接近7日線 (diff: {diff:.2f})")
        
        # 4. 創建3個評估記錄來達到目標平均
        scores = []
        base_score = target_avg
        scores.append(base_score)
        scores.append(base_score + 0.5)
        scores.append(base_score - 0.5)
        
        # 確保總和 = target_avg * 3
        adjustment = (target_avg * 3) - sum(scores)
        scores[2] += adjustment
        
        print(f"\n創建3個評估記錄: {[f'{s:.2f}' for s in scores]}")
        print(f"平均值檢驗: {sum(scores)/3:.2f}")
        
        times = [
            datetime.combine(jan5, time(6, 0, 0)),
            datetime.combine(jan5, time(14, 0, 0)),
            datetime.combine(jan5, time(21, 0, 0))
        ]
        
        max_score = 40  # Tester使用的最大分數
        
        for i, (score, timestamp) in enumerate(zip(scores, times)):
            assessment = AssessmentHistory(
                user_id=user.id,
                total_score=int(round(score)),
                max_score=max_score,
                level='測試',
                answers='[]',
                completed_at=timestamp
            )
            db.session.add(assessment)
            print(f"  {i+1}. {timestamp}: {int(round(score))}/{max_score}")
        
        db.session.commit()
        
        # 5. 觸發警報檢查
        print(f"\n執行警報檢查...")
        created_alerts = check_and_create_alert(user.id, jan5)
        
        if created_alerts:
            print(f"成功創建 {len(created_alerts)} 個警報:")
            for alert in created_alerts:
                try:
                    lines = json.loads(alert.exceeded_lines)
                    line_names = list(lines.keys())
                    action = "穿越" if alert.alert_type == 'high' else "接近"
                    print(f"  - [{alert.alert_type}] {action}: {', '.join(line_names)}")
                except:
                    print(f"  - [{alert.alert_type}] {alert.exceeded_lines}")
        else:
            print("警告：沒有創建任何警報！")
