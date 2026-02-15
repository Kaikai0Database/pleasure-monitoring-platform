"""
測試腳本：為所有用戶在 2026-01-04 創建三次測驗記錄
每次測驗分數為 56 分，時間分別為 6:00, 14:00, 21:00
用於測試雙重警告系統是否正常運作
"""
from datetime import datetime
from app.models import db, User, AssessmentHistory
from app import create_app

def create_test_assessments():
    """為所有用戶創建測試評估記錄"""
    
    # 測試日期：2026-01-04
    test_date = datetime(2026, 1, 4)
    
    # 三個測試時間點
    test_times = [
        test_date.replace(hour=6, minute=0, second=0),   # 早上 6:00
        test_date.replace(hour=14, minute=0, second=0),  # 下午 2:00
        test_date.replace(hour=21, minute=0, second=0),  # 晚上 9:00
    ]
    
    # 測試分數
    test_score = 56
    max_score = 70  # 假設總分為 70
    
    print("=" * 60)
    print("開始創建測試數據...")
    print(f"測試日期: {test_date.strftime('%Y-%m-%d')}")
    print(f"測試時間: 06:00, 14:00, 21:00")
    print(f"測試分數: {test_score}/{max_score}")
    print("=" * 60)
    
    # 獲取所有用戶
    users = User.query.all()
    print(f"\n找到 {len(users)} 個用戶帳號\n")
    
    created_count = 0
    
    for user in users:
        print(f"處理用戶: {user.name} (ID: {user.id}, Email: {user.email})")
        
        # 檢查是否已存在該日期的記錄
        existing = AssessmentHistory.query.filter(
            AssessmentHistory.user_id == user.id,
            AssessmentHistory.deleted_at.is_(None),
            db.func.date(AssessmentHistory.completed_at) == test_date.date()
        ).count()
        
        if existing > 0:
            print(f"  ⚠️  已存在 {existing} 筆記錄，跳過此用戶")
            continue
        
        # 為該用戶創建三次評估記錄
        for i, completed_time in enumerate(test_times, 1):
            assessment = AssessmentHistory(
                user_id=user.id,
                total_score=test_score,
                max_score=max_score,
                level='normal',  # 可根據實際計算調整
                completed_at=completed_time,
                deleted_at=None
            )
            db.session.add(assessment)
            print(f"  ✓ 創建第 {i} 次評估 - {completed_time.strftime('%H:%M')}")
            created_count += 1
        
        # 提交該用戶的記錄
        try:
            db.session.commit()
            print(f"  ✅ 成功創建 3 筆記錄")
        except Exception as e:
            db.session.rollback()
            print(f"  ❌ 創建失敗: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"測試數據創建完成！")
    print(f"總共創建了 {created_count} 筆評估記錄")
    print("=" * 60)
    print("\n⚠️  警告檢查說明：")
    print("- 系統會在第3次測驗後自動檢查警告")
    print("- 如果 56 分高於或低於移動平均線±3分，將創建相應警告")
    print("- 請登入前端查看警告圖標是否顯示")
    print("\n建議測試步驟：")
    print("1. 登入病人帳號查看主選單是否顯示警告圖標")
    print("2. 點擊圖標查看警告詳情")
    print("3. 登入管理員查看 Dashboard/Watchlist 警告圖標")
    print("4. 確認標記已讀功能正常運作")
    

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        create_test_assessments()
