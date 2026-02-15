"""
創建 patient_assignments 資料表的遷移腳本
手動執行此腳本來創建資料表
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.models import db

def create_patient_assignments_table():
    """創建病人分配表"""
    app = create_app()
    
    with app.app_context():
        # 創建資料表的 SQL
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS patient_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id INTEGER NOT NULL,
            patient_id INTEGER NOT NULL,
            assigned_by INTEGER,
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (staff_id) REFERENCES healthcare_staff (id),
            FOREIGN KEY (patient_id) REFERENCES users (id),
            FOREIGN KEY (assigned_by) REFERENCES healthcare_staff (id),
            UNIQUE (staff_id, patient_id)
        );
        """
        
        try:
            print("開始創建 patient_assignments 資料表...")
            db.session.execute(db.text(create_table_sql))
            db.session.commit()
            print("✓ patient_assignments 資料表創建成功！")
            
            # 驗證資料表是否存在
            result = db.session.execute(db.text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='patient_assignments';"
            ))
            if result.fetchone():
                print("✓ 驗證成功：資料表已存在於資料庫中")
            else:
                print("✗ 驗證失敗：資料表不存在")
                
        except Exception as e:
            print(f"✗ 創建資料表失敗: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    create_patient_assignments_table()
