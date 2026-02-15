"""
測試自動警報生成功能
通過 API 提交評估，驗證警報自動生成
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models import User, AssessmentHistory, ScoreAlert
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import json
import requests

app = create_app()

def create_test_user():
    """創建測試用戶"""
    with app.app_context():
        # 檢查是否已存在
        test_user = User.query.filter_by(email='autoalert.test@example.com').first()
        
        if test_user:
            # 清理舊數據
            AssessmentHistory.query.filter_by(user_id=test_user.id).delete()
            ScoreAlert.query.filter_by(user_id=test_user.id).delete()
            db.session.commit()
            print(f"[CLEANUP] 清理測試用戶的舊數據")
            return test_user.id
        
        # 創建新用戶
        user = User(
            email='autoalert.test@example.com',
            name='自動警報測試',
            nickname='Auto Alert Test',
            password_hash=generate_password_hash('test123'),
            group='clinical',
            created_at=datetime.now() - timedelta(days=35)
        )
        db.session.add(user)
        db.session.commit()
        
        print(f"[CREATE] 創建測試用戶 ID: {user.id}")
        return user.id

def get_auth_token(email, password):
    """獲取認證 token"""
    response = requests.post(
        'http://localhost:5000/api/auth/login',
        json={'email': email, 'password': password}
    )
    
    if response.status_code == 200:
        data = response.json()
        return data.get('access_token')
    else:
        print(f"[ERROR] 登入失敗: {response.text}")
        return None

def submit_assessment_via_api(token, total_score, answers=None):
    """通過 API 提交評估"""
    if not answers:
        # 生成樣本答案
        answers = []
        remaining = total_score
        for i in range(14):
            if i == 13:
                score = min(4, max(0, remaining))
            else:
                score = min(4, remaining)
                remaining -= score
            
            answers.append({
                "questionId": i + 1,
                "emoji": f"emoji_{i+1}",
                "score": score
            })
    
    response = requests.post(
        'http://localhost:5000/api/history',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'total_score': total_score,
            'max_score': 56,
            'answers': answers
        }
    )
    
    return response

def create_baseline_data(user_id):
    """創建基線數據（直接插入資料庫，模擬 30 天歷史）"""
    with app.app_context():
        print("\n[BASELINE] 創建 30 天基線數據...")
        
        start_date = datetime.now() - timedelta(days=30)
        
        for day in range(30):
            assessment_date = start_date + timedelta(days=day)
            
            # 分數模式：前 20 天穩定在 28-32，後 10 天下降到 24-26
            if day < 20:
                base_score = 30
                variation = (-2 if day % 3 == 0 else 2)
            else:
                base_score = 25
                variation = (-1 if day % 2 == 0 else 1)
            
            score = base_score + variation
            
            # 每天 3 次評估
            for hour in [8, 14, 20]:
                assessment_time = assessment_date.replace(hour=hour, minute=0, second=0)
                
                assessment = AssessmentHistory(
                    user_id=user_id,
                    total_score=score,
                    max_score=56,
                    level='需要關注' if score >= 30 else '良好',
                    answers=json.dumps([]),
                    completed_at=assessment_time
                )
                db.session.add(assessment)
        
        db.session.commit()
        print(f"[OK] 創建了 90 條基線評估記錄（30 天 × 3 次）")

def main():
    print("="*80)
    print("自動警報生成功能測試")
    print("="*80)
    
    # 1. 創建測試用戶
    user_id = create_test_user()
    
    # 2. 創建基線數據
    create_baseline_data(user_id)
    
    # 3. 獲取認證 token
    print("\n[AUTH] 獲取認證 token...")
    token = get_auth_token('autoalert.test@example.com', 'test123')
    
    if not token:
        print("❌ 無法獲取 token，測試終止")
        return
    
    print(f"[OK] Token 獲取成功")
    
    # 4. 通過 API 提交今天的評估（高分，應該觸發警報）
    print("\n[TEST] 通過 API 提交今天的第一次評估（分數: 35）...")
    
    response = submit_assessment_via_api(token, 35)
    
    if response.status_code in [200, 201]:
        print(f"[OK] 評估提交成功: {response.json()}")
    else:
        print(f"[ERROR] 評估提交失敗: {response.status_code} - {response.text}")
        return
    
    # 5. 檢查警報是否自動生成
    print("\n[VERIFY] 檢查警報是否自動生成...")
    
    with app.app_context():
        today = datetime.now().date()
        alerts = ScoreAlert.query.filter_by(
            user_id=user_id,
            alert_date=today
        ).all()
        
        if alerts:
            print(f"\n✅ 成功！自動生成了 {len(alerts)} 個警報：")
            for alert in alerts:
                print(f"  - {alert.alert_type.upper()} 警報")
                print(f"    日平均: {alert.daily_average}")
                print(f"    超越/接近線: {alert.exceeded_lines}")
                print(f"    狀態: {'未讀' if not alert.is_read else '已讀'}")
        else:
            print(f"\n❌ 失敗！沒有生成警報")
            
            # 調試信息
            print("\n[DEBUG] 檢查評估記錄...")
            assessments_today = AssessmentHistory.query.filter(
                AssessmentHistory.user_id == user_id,
                db.func.date(AssessmentHistory.completed_at) == today
            ).all()
            
            print(f"今天的評估次數: {len(assessments_today)}")
            if assessments_today:
                scores = [a.total_score for a in assessments_today]
                avg = sum(scores) / len(scores)
                print(f"分數: {scores}")
                print(f"平均: {avg:.2f}")
    
    # 6. 提交第二次和第三次評估
    print("\n[TEST] 提交今天的第二次和第三次評估...")
    
    for i, score in enumerate([33, 34], 2):
        response = submit_assessment_via_api(token, score)
        if response.status_code in [200, 201]:
            print(f"[OK] 第 {i} 次評估提交成功（分數: {score}）")
        else:
            print(f"[ERROR] 第 {i} 次評估提交失敗")
    
    # 7. 最終驗證
    print("\n[FINAL] 最終驗證...")
    
    with app.app_context():
        total_assessments = AssessmentHistory.query.filter_by(user_id=user_id).count()
        total_alerts = ScoreAlert.query.filter_by(user_id=user_id).count()
        unread_alerts = ScoreAlert.query.filter_by(user_id=user_id, is_read=False).count()
        
        print(f"\n{'='*60}")
        print(f"測試結果總結")
        print(f"{'='*60}")
        print(f"總評估次數: {total_assessments}")
        print(f"總警報數: {total_alerts}")
        print(f"未讀警報: {unread_alerts}")
        
        # 顯示今天的所有警報
        today_alerts = ScoreAlert.query.filter_by(
            user_id=user_id,
            alert_date=datetime.now().date()
        ).all()
        
        if today_alerts:
            print(f"\n今天的警報 ({len(today_alerts)} 個):")
            for alert in today_alerts:
                print(f"  [{alert.alert_type.upper()}] 日平均: {alert.daily_average} | {alert.exceeded_lines}")
        
        print(f"\n{'='*60}")
        
        if total_alerts > 0:
            print("✅ 自動警報功能正常運作！")
        else:
            print("❌ 自動警報功能可能有問題")
        
        print(f"{'='*60}")
        
        print("\n測試帳號:")
        print("  Email: autoalert.test@example.com")
        print("  Password: test123")
        print("\n可以登入管理後台查看此測試帳號的數據和警報")

if __name__ == '__main__':
    main()
