"""
修正測試腳本：
1. 刪除 2026-01-04 的錯誤數據（56/70）
2. 創建正確的測試數據（56/56 滿分）

目的：讓56分（滿分）超過7日、14日、30日移動平均線，觸發高分警告
"""
from datetime import datetime, date
from app.models import db, User, AssessmentHistory, ScoreAlert
from app import create_app

def fix_test_data():
    """修正測試數據"""
    
    test_date = date(2026, 1, 4)
    
    print("=" * 70)
    print("修正測試數據")
    print("=" * 70)
    
    # 步驟1: 刪除今天的錯誤數據
    print("\n步驟 1: 刪除 2026-01-04 的錯誤數據...")
    
    # 刪除評估記錄
    deleted_assessments = AssessmentHistory.query.filter(
        db.func.date(AssessmentHistory.completed_at) == test_date,
        AssessmentHistory.deleted_at.is_(None)
    ).delete(synchronize_session=False)
    
    # 刪除警告記錄
    deleted_alerts = ScoreAlert.query.filter(
        ScoreAlert.alert_date == test_date
    ).delete(synchronize_session=False)
    
    db.session.commit()
    
    print(f"  已刪除 {deleted_assessments} 筆評估記錄")
    print(f"  已刪除 {deleted_alerts} 筆警告記錄")
    
    # 步驟2: 創建正確的測試數據
    print("\n步驟 2: 創建正確的測試數據（56/56 滿分）...")
    
    # 三個測試時間點
    test_times = [
        datetime(2026, 1, 4, 6, 0, 0),   # 早上 6:00
        datetime(2026, 1, 4, 14, 0, 0),  # 下午 2:00
        datetime(2026, 1, 4, 21, 0, 0),  # 晚上 9:00
    ]
    
    # 正確的測試分數：滿分56分
    test_score = 56
    max_score = 56  # 滿分
    
    # 獲取所有用戶
    users = User.query.all()
    print(f"\n找到 {len(users)} 個用戶")
    
    created_count = 0
    
    for user in users:
        print(f"\n處理用戶: {user.name} (ID: {user.id})")
        
        # Calculate level based on user group (same logic as in history.py)
        if user.group == 'student':
            # Student group: threshold is 24
            level = '需要關注' if test_score >= 24 else '良好'
        else:
            # Clinical group: threshold is 29
            level = '需要關注' if test_score >= 29 else '良好'
        
        print(f"  等級: {level}")
        
        # 為該用戶創建三次滿分評估
        for i, completed_time in enumerate(test_times, 1):
            assessment = AssessmentHistory(
                user_id=user.id,
                total_score=test_score,
                max_score=max_score,
                level=level,
                completed_at=completed_time,
                deleted_at=None
            )
            db.session.add(assessment)
            print(f"  ✓ 第 {i} 次評估 - {completed_time.strftime('%H:%M')} - {test_score}/{max_score} (滿分, 等級: {level})")
            created_count += 1
        
        # 提交該用戶的記錄
        try:
            db.session.commit()
            print(f"  ✅ 成功創建 3 筆滿分記錄")
        except Exception as e:
            db.session.rollback()
            print(f"  ❌ 創建失敗: {str(e)}")
    
    print("\n" + "=" * 70)
    print(f"✅ 測試數據修正完成！")
    print(f"總共創建了 {created_count} 筆評估記錄（每筆都是 56/56 滿分）")
    print("=" * 70)
    
    print("\n⚠️  警告觸發說明：")
    print("- 56分是滿分，應該會遠高於過去的移動平均線")
    print("- 系統會在第3次測驗後自動檢查並創建高分警告（🔔）")
    print("- 理論上不會觸發低分警告（📉）")
    
    print("\n📋 測試步驟：")
    print("1. 重新運行腳本觸發警告檢查")
    print("2. 登入病人帳號查看主選單是否顯示紅色警告鈴鐺（🔔）")
    print("3. 點擊查看「高分警示」彈窗")
    print("4. 登入管理員查看 Dashboard/Watchlist 的紅色鈴鐺圖標")
    

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        fix_test_data()
