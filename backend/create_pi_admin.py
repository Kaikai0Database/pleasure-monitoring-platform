"""
建立計畫主持人（PI）管理員帳號

帳號資訊：
- 登入帳號（郵箱）: jadeching@gmail.com
- 登入密碼: anhedoniaMA
- 顯示姓名: 計畫主持人帳號1
- 職稱: 計畫主持人 (PI)
- 權限角色: super_admin（全域最高權限）
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.admin_models import HealthcareStaff, db
from werkzeug.security import generate_password_hash

def create_pi_admin():
    """建立計畫主持人（PI）管理員帳號"""
    app = create_app()
    
    with app.app_context():
        # 帳號資訊
        email = 'jadeching@gmail.com'
        password = 'anhedoniaMA'
        name = '計畫主持人帳號1'
        role = 'super_admin'
        
        print("=" * 70)
        print("計畫主持人（PI）管理員帳號建立程序")
        print("=" * 70)
        
        # 檢查是否已存在
        existing = HealthcareStaff.query.filter_by(email=email).first()
        
        if existing:
            print(f"\n[!] 帳號已存在: {email}")
            print(f"    舊姓名: {existing.name}")
            print(f"    舊角色: {existing.role}")
            
            # 更新所有欄位
            existing.name = name
            existing.role = role
            existing.password_hash = generate_password_hash(password)
            
            db.session.commit()
            
            print(f"\n[✓] 帳號更新成功！")
            print(f"    新姓名: {name}")
            print(f"    新角色: {role}")
            print(f"    密碼已更新並加密儲存")
        else:
            # 建立新帳號
            print(f"\n[+] 建立新帳號: {email}")
            
            pi_admin = HealthcareStaff(
                email=email,
                name=name,
                password_hash=generate_password_hash(password),
                role=role
            )
            
            db.session.add(pi_admin)
            db.session.commit()
            
            print(f"[✓] 帳號建立成功！")
        
        # 顯示帳號資訊
        print("\n" + "=" * 70)
        print("計畫主持人（PI）管理員帳號資訊")
        print("=" * 70)
        print(f"  登入帳號（郵箱）: {email}")
        print(f"  登入密碼:         {password}")
        print(f"  顯示姓名:         {name}")
        print(f"  職稱:             計畫主持人 (PI)")
        print(f"  權限角色:         {role}")
        print("=" * 70)
        print("\n權限說明：")
        print("  ✓ 全域資料存取權 - 可查看所有患者資料")
        print("  ✓ 繞過個案分配限制 - 不受 assigned_nurse_id 過濾")
        print("  ✓ 個案分配管理 - 可檢視並重新分配所有個案")
        print("  ✓ 全域趨勢監控 - 查看所有病人的 MA 穿越與接近警報")
        print("  ✓ 個案細節與日記 - 讀取所有患者的歷史分數與心情紀錄")
        print("  ✓ 護理師列表查看 - 可查看所有醫護人員")
        print("=" * 70)
        print("\n注意事項：")
        print("  • 密碼已使用 Werkzeug 的 generate_password_hash() 加密")
        print("  • 此帳號僅限醫護端後台使用")
        print("  • 不具備像素風測驗、等級提升或 XP 增加等遊戲化功能")
        print("  • 查看的數據仍遵循「當日 ≥3 次評估」的 MA 警報計算邏輯")
        print("=" * 70)
        print("\n✓ 完成！")

if __name__ == "__main__":
    create_pi_admin()
