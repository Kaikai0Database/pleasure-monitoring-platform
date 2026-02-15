"""
Generate Mock Patient Data - Python Version
"""
import json
import random
import uuid
from datetime import datetime, timedelta

# 隨機中文姓氏
last_names = [
    '王', '李', '張', '劉', '陳', '楊', '黃', '趙', '吳', '周',
    '徐', '孫', '馬', '朱', '胡', '郭', '何', '高', '林', '羅',
    '鄭', '梁', '謝', '宋', '唐', '許', '韓', '馮', '鄧', '曹'
]

# 隨機中文名字
first_names = [
    '明', '華', '強', '偉', '芳', '娟', '敏', '靜', '麗', '軍',
    '杰', '勇', '磊', '濤', '超', '婷', '雪', '梅', '玲', '紅',
    '宇', '浩', '欣', '怡', '雅', '詩', '曉', '雨', '晨', '陽'
]

def generate_chinese_name():
    """生成隨機中文姓名"""
    last_name = random.choice(last_names)
    first_name1 = random.choice(first_names)
    first_name2 = random.choice(first_names) if random.random() > 0.5 else ''
    return last_name + first_name1 + first_name2

def generate_admission_date():
    """生成隨機日期（過去一年內）"""
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)
    random_days = random.randint(0, 365)
    admission_date = one_year_ago + timedelta(days=random_days)
    return admission_date.strftime('%Y-%m-%d')

def determine_status(score):
    """根據分數決定狀態"""
    if score >= 80:
        return '正常'
    elif score >= 60:
        return '需追蹤'
    elif score >= 40:
        return '穩定'
    elif score >= 20:
        return '待評估'
    else:
        return '高風險'

def generate_mock_patient(index):
    """生成單筆病人數據"""
    score = random.randint(0, 100)
    age = random.randint(18, 80)
    gender = random.choice(['男', '女'])
    
    return {
        'id': str(uuid.uuid4()),
        'name': generate_chinese_name(),
        'age': age,
        'gender': gender,
        'last_assessment_score': score,
        'status': determine_status(score),
        'admission_date': generate_admission_date(),
        'patient_number': f'P{str(index + 1).zfill(4)}',
        'email': f'patient{index + 1}@test.com',
        'phone': f'09{random.randint(10000000, 99999999)}'
    }

def generate_mock_patients(count=30):
    """生成多筆病人數據"""
    patients = []
    for i in range(count):
        patients.push(generate_mock_patient(i))
    return patients

if __name__ == '__main__':
    # 生成 30 筆測試數據
    patient_count = 30
    mock_patients = [generate_mock_patient(i) for i in range(patient_count)]
    
    print('=' * 60)
    print(f'生成了 {patient_count} 筆測試病人數據')
    print('=' * 60)
    print(json.dumps(mock_patients, ensure_ascii=False, indent=2))
    print('=' * 60)
    print(f'\n總共 {len(mock_patients)} 筆數據')
    print(f'狀態分布：')
    status_count = {}
    for p in mock_patients:
        status = p['status']
        status_count[status] = status_count.get(status, 0) + 1
    for status, count in sorted(status_count.items()):
        print(f'  {status}: {count} 人')
