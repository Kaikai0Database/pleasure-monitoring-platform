"""
創建低分測試數據
目的：測試低分警告功能

為每個用戶在 2026-01-05 創建三次測試評估
分數：30日線最後一個點 - 2 分
時間：早上6點、下午2點、晚上9點
"""
from datetime import datetime, date, timedelta
from app.models import db, User, AssessmentHistory
from app import create_app
from collections import defaultdict

def calculate_30day_ma_last_point(user_id, target_date):
    """計算指定日期的30日移動平均線（用於確定測試分數）"""
    
    # 獲取目標日期前30天的數據
    start_date = target_date - timedelta(days=30)
    
    assessments = AssessmentHistory.query.filter(
        AssessmentHistory.user_id == user_id,
        db.func.date(AssessmentHistory.completed_at) >= start_date,
        db.func.date(AssessmentHistory.completed_at) < target_date,
        AssessmentHistory.deleted_at.is_(None)
    ).order_by(AssessmentHistory.completed_at).all()
    
    if not assessments:
        return None
    
    # 按日期分組計算每日平均
    daily_scores = defaultdict(list)
    for assessment in assessments:
        date_key = assessment.completed_at.date()
        daily_scores[date_key].append(assessment.total_score)
    
    # 計算每日平均
    daily_averages = []
    for date_key in sorted(daily_scores.keys()):
        avg = sum(daily_scores[date_key]) / len(daily_scores[date_key])
        daily_averages.append(avg)
    
    # 計算30日移動平均（只有當有30天數據時）
    if len(daily_averages) >= 30:
        # 取最後30天的平均
        last_30_days = daily_averages[-30:]
        ma_30 = sum(last_30_days) / 30
        return round(ma_30, 1)
    
    return None

def create_low_score_test_data():
    """創建低分測試數據"""
    
    test_date = date(2026, 1, 5)
    
    print("=" * 80)
    print("創建低分測試數據")
    print(f"測試日期: {test_date}")
    print("目的: 測試低分警告功能（分數低於30日線 2 分）")
    print("=" * 80)
    
    # 三個測試時間點
    test_times = [
        datetime(2026, 1, 5, 6, 0, 0),   # 早上 6:00
        datetime(2026, 1, 5, 14, 0, 0),  # 下午 2:00
        datetime(2026, 1, 5, 21, 0, 0),  # 晚上 9:00
    ]
    
    # 獲取所有用戶
    users = User.query.all()
    print(f"\n找到 {len(users)} 個用戶\n")
    
    created_count = 0
    skipped_count = 0
    
    for user in users:
        print(f"處理用戶: {user.name} (ID: {user.id}, 組別: {user.group or 'unknown'})")
        
        # 計算該用戶的30日移動平均線最後一個點
        ma_30 = calculate_30day_ma_last_point(user.id, test_date)
        
        if ma_30 is None:
            print(f"  ⚠️  跳過：該用戶沒有足夠的30日線數據")
            skipped_count += 1
            continue
        
        # 測試分數 = 30日線 - 2
        test_score = int(ma_30 - 2)
        
        # 確保分數不小於0，不大於56
        test_score = max(0, min(test_score, 56))
        
        print(f"  30日線最後一點: {ma_30}")
        print(f"  測試分數: {test_score} (30日線 - 2)")
        
        # 計算等級（根據用戶組別）
        if user.group == 'student':
            level = '需要關注' if test_score >= 24 else '良好'
        else:
            level = '需要關注' if test_score >= 29 else '良好'
        
        print(f"  等級: {level}")
        
        # 為該用戶創建三次評估
        for i, completed_time in enumerate(test_times, 1):
            assessment = AssessmentHistory(
                user_id=user.id,
                total_score=test_score,
                max_score=56,
                level=level,
                completed_at=completed_time,
                deleted_at=None
            )
            db.session.add(assessment)
            print(f"  ✓ 第 {i} 次評估 - {completed_time.strftime('%H:%M')} - {test_score}/56 (等級: {level})")
            created_count += 1
        
        # 提交該用戶的記錄
        try:
            db.session.commit()
            print(f"  ✅ 成功創建 3 筆測試記錄\n")
        except Exception as e:
            db.session.rollback()
            print(f"  ❌ 創建失敗: {str(e)}\n")
    
    print("=" * 80)
    print(f"✅ 測試數據創建完成！")
    print(f"成功創建: {created_count} 筆評估記錄")
    print(f"跳過用戶: {skipped_count} 個（缺少30日線數據）")
    print("=" * 80)
    
    print("\n📋 下一步：")
    print("1. 運行 trigger_alerts.py 來觸發警告檢查")
    print("2. 檢查是否創建了低分警告（📉）")
    print("3. 登入病人端查看藍色警告圖標")
    print("4. 登入管理員端查看藍色警告圖標和提示")
    
    print("\n⚠️  預期結果：")
    print("- 應該創建「低分警告」（alert_type='low'）")
    print("- 病人端主選單顯示藍色 📉 圖標")
    print("- 管理員 Dashboard/Watchlist 顯示藍色 📉 圖標")
    print("- 圖表標題旁不應該顯示「穿越XX線」（因為是低分）")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        create_low_score_test_data()
