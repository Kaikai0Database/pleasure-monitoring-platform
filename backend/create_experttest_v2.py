"""
創建測試帳號並生成評估數據
experttest1_2@example.com 和 experttest2_2@example.com
時間範圍：2025/12/1 - 2026/2/1
每天3次測驗（08:00, 14:00, 20:00）
確保2026/2/1滿足MA條件
"""

from app import create_app
from app.models import db, User, AssessmentHistory
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def create_test_accounts():
    """創建兩個測試帳號，返回(id, email)元組列表"""
    app = create_app()
    account_info = []
    
    with app.app_context():
        emails = [
            ('experttest1_2@example.com', 'Expert Test 1-2'),
            ('experttest2_2@example.com', 'Expert Test 2-2')
        ]
        
        for email, name in emails:
            # 檢查是否已存在
            existing = User.query.filter_by(email=email).first()
            
            if existing:
                print(f"\n⚠️  帳號 {email} 已存在 (ID: {existing.id})")
                print(f"   將清除舊的測驗數據...")
                # 刪除舊測驗數據
                AssessmentHistory.query.filter_by(user_id=existing.id).delete()
                db.session.commit()
                account_info.append((existing.id, existing.email))
                print(f"   ✅ 舊數據已清除")
            else:
                # 創建新帳號
                new_user = User(
                    email=email,
                    name=name,
                    password_hash=generate_password_hash('test123')
                )
                db.session.add(new_user)
                db.session.commit()
                account_info.append((new_user.id, new_user.email))
                print(f"\n✅ 帳號創建成功: {email} (ID: {new_user.id})")

        return account_info


def generate_score(phase, day_in_phase, time_of_day, base_variation=0):
    """
    根據階段生成分數
    phase: 'baseline', 'rising', 'sprint', 'final'
    day_in_phase: 該階段的第幾天
    time_of_day: 'morning', 'afternoon', 'evening'
    base_variation: 基礎變化（用於兩個帳號間的差異）
    """
    
    # 時段調整
    time_adjust = {
        'morning': 0,
        'afternoon': -1,
        'evening': 1
    }
    
    if phase == 'baseline':
        # 階段1: 20-30分
        base = 25
        variation = random.randint(-3, 3)
        
    elif phase == 'rising':
        # 階段2: 30-48分，漸進上升
        # 25天分為3個小階段
        if day_in_phase <= 10:  # 前10天
            base = 30 + day_in_phase * 0.5
        elif day_in_phase <= 20:  # 中10天
            base = 35 + (day_in_phase - 10) * 0.7
        else:  # 後5天
            base = 42 + (day_in_phase - 20) * 1.2
        variation = random.randint(-2, 2)
        
    elif phase == 'sprint':
        # 階段3: 48-54分，快速上升
        base = 48 + day_in_phase * 1.0
        variation = random.randint(-1, 1)
        
    elif phase == 'final':
        # 階段4: 最後一天，固定50-52分
        if time_of_day == 'morning':
            return 50 + base_variation
        elif time_of_day == 'afternoon':
            return 51 + base_variation
        else:  # evening
            return 52 + base_variation
    
    score = int(base + time_adjust[time_of_day] + variation + base_variation)
    return max(0, min(60, score))  # 限制在0-60範圍


def generate_assessment_data(user, base_variation=0):
    """為用戶生成63天的測驗數據"""
    app = create_app()
    
    with app.app_context():
        # 重新查詢用戶以確保在當前session中
        user = User.query.get(user.id)
        
        start_date = datetime(2025, 12, 1)
        end_date = datetime(2026, 2, 1)
        current_date = start_date
        
        assessment_count = 0
        
        while current_date <= end_date:
            # 判斷當前階段
            if current_date.month == 12:  # 2025年12月
                phase = 'baseline'
                day_in_phase = current_date.day
            elif current_date.month == 1 and current_date.day <= 25:  # 1/1-1/25
                phase = 'rising'
                day_in_phase = current_date.day
            elif current_date.month == 1 and current_date.day > 25:  # 1/26-1/31
                phase = 'sprint'
                day_in_phase = current_date.day - 25
            else:  # 2/1
                phase = 'final'
                day_in_phase = 1
            
            # 每天3次測驗
            times = [
                ('morning', 8, 0, 0),    # 08:00
                ('afternoon', 14, 0, 0),  # 14:00
                ('evening', 20, 0, 0)     # 20:00
            ]
            
            for time_of_day, hour, minute, second in times:
                score = generate_score(phase, day_in_phase, time_of_day, base_variation)
                
                # 創建測驗時間（UTC時間，台灣是UTC+8）
                assessment_time = datetime(
                    current_date.year,
                    current_date.month,
                    current_date.day,
                    hour - 8,  # 轉換為UTC時間
                    minute,
                    second
                )
                
                # 創建測驗記錄
                assessment = AssessmentHistory(
                    user_id=user.id,
                    total_score=score,
                    max_score=60,  # 最高分60分
                    level='normal',  # 固定為normal
                    answers='[]',  # 空答案陣列
                    completed_at=assessment_time
                )
                
                db.session.add(assessment)
                assessment_count += 1
            
            # 每10天提交一次
            if assessment_count % 30 == 0:
                db.session.commit()
                print(f"  已生成 {assessment_count} 次測驗...")
            
            current_date += timedelta(days=1)
        
        # 最後提交
        db.session.commit()
        print(f"✅ {user.email} 數據生成完成：共 {assessment_count} 次測驗")
        
        return assessment_count


def calculate_ma(user, target_date, days):
    """計算指定日期的移動平均線"""
    app = create_app()
    
    with app.app_context():
        user = User.query.get(user.id)
        
        # 計算目標日期前N天的日平均
        end_date = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59)
        start_date = end_date - timedelta(days=days-1)
        start_date = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
        
        # 轉換為UTC
        end_date_utc = end_date - timedelta(hours=8)
        start_date_utc = start_date - timedelta(hours=8)
        
        # 查詢該期間的測驗
        assessments = AssessmentHistory.query.filter(
            AssessmentHistory.user_id == user.id,
            AssessmentHistory.completed_at >= start_date_utc,
            AssessmentHistory.completed_at <= end_date_utc
        ).all()
        
        if not assessments:
            return None
        
        # 按日期分組計算日平均
        daily_scores = {}
        for a in assessments:
            # 轉換回台灣時間
            local_time = a.completed_at + timedelta(hours=8)
            date_key = local_time.date()
            
            if date_key not in daily_scores:
                daily_scores[date_key] = []
            daily_scores[date_key].append(a.total_score)
        
        # 計算每日平均
        daily_averages = [sum(scores) / len(scores) for scores in daily_scores.values()]
        
        # 計算移動平均
        if len(daily_averages) > 0:
            ma = sum(daily_averages) / len(daily_averages)
            return round(ma, 2)
        
        return None


def verify_conditions(user):
    """驗證2026/2/1的條件"""
    app = create_app()
    
    with app.app_context():
        user = User.query.get(user.id)
        target_date = datetime(2026, 2, 1)
        
        # 計算當日平均
        start = datetime(2026, 2, 1, 0, 0, 0) - timedelta(hours=8)
        end = datetime(2026, 2, 1, 23, 59, 59) - timedelta(hours=8)
        
        daily_assessments = AssessmentHistory.query.filter(
            AssessmentHistory.user_id == user.id,
            AssessmentHistory.completed_at >= start,
            AssessmentHistory.completed_at <= end
        ).all()
        
        daily_avg = sum(a.total_score for a in daily_assessments) / len(daily_assessments) if daily_assessments else 0
        
        # 計算MA
        ma7 = calculate_ma(user, target_date, 7)
        ma14 = calculate_ma(user, target_date, 14)
        ma30 = calculate_ma(user, target_date, 30)
        
        print(f"\n📊 {user.email} - 2026/2/1 驗證結果")
        print(f"  當日平均：{daily_avg:.2f}分")
        print(f"  7日MA：{ma7:.2f}分（差距：{abs(daily_avg - ma7):.2f}分）")
        print(f"  14日MA：{ma14:.2f}分（差距：{abs(daily_avg - ma14):.2f}分）")
        print(f"  30日MA：{ma30:.2f}分（差距：{abs(daily_avg - ma30):.2f}分）")
        
        # 檢查條件
        exceed_condition = False
        close_condition = False
        
        # 超越條件（差距>3分）
        if daily_avg > ma30 + 3:
            print(f"  ✅ 超越30日MA（{daily_avg:.2f} > {ma30:.2f} + 3）")
            exceed_condition = True
        
        # 接近條件（差距<3分）
        if abs(daily_avg - ma7) < 3:
            print(f"  ✅ 接近7日MA（差距{abs(daily_avg - ma7):.2f} < 3）")
            close_condition = True
        
        if exceed_condition and close_condition:
            print(f"  🎉 所有條件滿足！")
            return True
        else:
            print(f"  ⚠️  條件未完全滿足")
            return False


if __name__ == '__main__':
    print("=" * 60)
    print("測試帳號與評估數據生成")
    print("=" * 60)
    
    # 步驟1：創建帳號
    print("\n【步驟1】創建測試帳號...")
    account_info = create_test_accounts()  # 直接返回[(id, email), ...]
    
    # 步驟2：生成數據
    print("\n【步驟2】生成評估數據...")
    print("  時間範圍：2025/12/1 - 2026/2/1（63天）")
    print("  每天3次：08:00, 14:00, 20:00")
    print("  總計：63天 × 3次 × 2帳號 = 378次測驗\n")
    
    # 創建臨時user對象僅用於傳遞ID
    class UserInfo:
        def __init__(self, uid):
            self.id = uid
    
    total_assessments = 0
    for i, (user_id, email) in enumerate(account_info):
        print(f"\n正在生成 {email} 的數據...")
        user_obj = UserInfo(user_id)
        count = generate_assessment_data(user_obj, base_variation=i)
        total_assessments += count
    
    # 步驟3：驗證條件
    print("\n" + "=" * 60)
    print("【步驟3】驗證移動平均線條件")
    print("=" * 60)
    
    all_satisfied = True
    for user_id, email in account_info:
        user_obj = UserInfo(user_id)
        satisfied = verify_conditions(user_obj)
        if not satisfied:
            all_satisfied = False
    
    print("\n" + "=" * 60)
    if all_satisfied:
        print("✅ 所有測試完成！條件全部滿足！")
    else:
        print("⚠️  測試完成，但部分條件未滿足，可能需要調整")
    print(f"總計生成：{total_assessments} 次測驗記錄")
    print("=" * 60)
