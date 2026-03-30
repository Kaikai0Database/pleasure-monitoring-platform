from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login_date = db.Column(db.Date, nullable=True)
    daily_login_count = db.Column(db.Integer, default=0)
    
    # Profile Fields
    nickname = db.Column(db.String(255), nullable=True)
    dob = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(50), nullable=True)
    height = db.Column(db.Float, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    education = db.Column(db.String(50), nullable=True)
    marital_status = db.Column(db.String(50), nullable=True)
    marriage_other = db.Column(db.String(255), nullable=True)
    has_children = db.Column(db.Boolean, nullable=True)
    children_count = db.Column(db.Integer, nullable=True)
    economic_status = db.Column(db.String(50), nullable=True)
    economic_status = db.Column(db.String(50), nullable=True)
    family_structure = db.Column(db.String(50), nullable=True)
    family_other = db.Column(db.String(255), nullable=True)
    has_job = db.Column(db.Boolean, nullable=True)
    salary_range = db.Column(db.String(50), nullable=True)
    location_city = db.Column(db.String(50), nullable=True)
    location_district = db.Column(db.String(50), nullable=True)
    living_situation = db.Column(db.String(50), nullable=True)
    cohabitant_count = db.Column(db.Integer, nullable=True) # "deducting self"
    religion = db.Column(db.Boolean, nullable=True)
    religion_other = db.Column(db.String(255), nullable=True)
    is_profile_completed = db.Column(db.Boolean, default=False)
    has_consented = db.Column(db.Boolean, default=False)
    group = db.Column(db.String(20), default='clinical')  # 'student' or 'clinical'
    
    # Relationship
    histories = db.relationship('AssessmentHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    diaries = db.relationship('Diary', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': str(self.created_at) if self.created_at else None,
            'daily_login_count': self.daily_login_count,
            'is_profile_completed': bool(self.is_profile_completed) if self.is_profile_completed is not None else False,
            'nickname': self.nickname,
            'dob':  str(self.dob) if self.dob else None,
            'gender': self.gender,
            'height': self.height,
            'weight': self.weight,
            'education': self.education,
            'marital_status': self.marital_status,
            'marriage_other': self.marriage_other,
            'has_children': bool(self.has_children) if self.has_children is not None else False,
            'children_count': self.children_count,
            'economic_status': self.economic_status,
            'family_structure': self.family_structure,
            'family_other': self.family_other,
            'has_job': bool(self.has_job) if self.has_job is not None else False,
            'salary_range': self.salary_range,
            'location_city': self.location_city,
            'location_district': self.location_district,
            'living_situation': self.living_situation,
            'cohabitant_count': self.cohabitant_count,
            'religion': bool(self.religion) if self.religion is not None else False,
            'religion_other': self.religion_other,
            'group': self.group,
            'has_consented': bool(self.has_consented) if self.has_consented is not None else False,
            'consecutive_days': self.calculate_streak()
        }

    def calculate_streak(self):
        """Calculate consecutive days of assessments"""
        if not self.histories:
            return 0
            
        from datetime import datetime, date
        temp_dates = []
        for h in self.histories:
            val = h.completed_at
            if not val: continue
            
            # 如果是字串，轉成 date 物件
            if isinstance(val, str):
                try:
                    temp_dates.append(datetime.strptime(val[:10], '%Y-%m-%d').date())
                except: continue
            # 如果已經是日期物件，直接取 date()
            elif hasattr(val, 'date'):
                temp_dates.append(val.date())
                
        dates = sorted(list(set(temp_dates)), reverse=True)
        if not dates:
            return 0
            
        today = datetime.now().date()
        
        # 檢查最近一次測試是否在今天或昨天
        if (today - dates[0]).days > 1:
            return 0
            
        streak = 1
        for i in range(len(dates) - 1):
            if (dates[i] - dates[i+1]).days == 1:
                streak += 1
            else:
                break
        return streak


class AssessmentHistory(db.Model):
    """Assessment history model"""
    __tablename__ = 'assessment_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_score = db.Column(db.Integer, nullable=False)
    max_score = db.Column(db.Integer, nullable=False)
    level = db.Column(db.String(50), nullable=False)
    answers = db.Column(db.Text, nullable=False)  # JSON string
    completed_at = db.Column(db.DateTime, default=datetime.now)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    delete_reason = db.Column(db.String(255), nullable=True)
    
    def to_dict(self):
        """Convert assessment history to dictionary - 安全防護版"""
        # 1. 這裡維持原樣，這是算進度條用的
        percentage = round((self.total_score / self.max_score) * 100) if self.max_score > 0 else 0
        
        # 2. 【核心修正】：判斷 answers 的類型
        answers_data = self.answers
        if isinstance(answers_data, str):  # 只有當它是「字串」時，才需要 json.loads
            try:
                import json
                answers_data = json.loads(answers_data)
            except:
                answers_data = []
        elif answers_data is None:
            answers_data = []
        # 如果 answers_data 本來就是 list，它會直接跳過上面的判斷，平安抵達 return

        # 3. 變數一個都不能少！全部回傳給前端
        return {
            'id': self.id,
            'total_score': self.total_score,
            'max_score': self.max_score,
            'level': self.level,
            'percentage': percentage,
            'answers': answers_data, # 使用處理完的資料
            'completed_at': str(self.completed_at) if self.completed_at else None,
            'is_deleted': bool(self.is_deleted),
            'deleted_at': str(self.deleted_at) if self.deleted_at else None,
            'delete_reason': self.delete_reason
        }



class Diary(db.Model):
    """Diary model"""
    __tablename__ = 'diaries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)  # 使用者選擇的日期
    mood = db.Column(db.String(50), nullable=True)  # 情緒表情 key（可選，允許只標記生理期）
    content = db.Column(db.Text, nullable=True)  # 文字內容（可選）
    images = db.Column(db.Text, nullable=True)  # 圖片路徑（JSON 陣列字串）
    period_marker = db.Column(db.Boolean, default=False)  # 是否為生理期
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 移除唯一性約束，允許同一天創建多筆日記
    # __table_args__ = (
    #     db.UniqueConstraint('user_id', 'date', name='unique_user_diary_per_day'),
    # )
    
    def to_dict(self):
        """Convert diary to dictionary"""
        images_data = self.images
        if isinstance(images_data, str):
            try:
                images_data = json.loads(images_data)
            except:
                images_data = []
        elif images_data is None:
            images_data = []

        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': str(self.date) if self.date else None,
            'mood': self.mood,
            'content': self.content,
            'images': images_data,
            'period_marker': bool(self.period_marker) if self.period_marker is not None else False,
            'created_at': str(self.created_at) if self.created_at else None,
            'updated_at': str(self.updated_at) if self.updated_at else None
        }


class ScoreAlert(db.Model):
    """Score Alert model - tracks when daily average exceeds moving averages"""
    __tablename__ = 'score_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    alert_date = db.Column(db.Date, nullable=False)
    daily_average = db.Column(db.Float, nullable=False)
    exceeded_lines = db.Column(db.Text, nullable=False)  # JSON: {"7日": 38, "14日": 35}
    alert_type = db.Column(db.String(10), default='high', nullable=False)  # 'high' or 'low'
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationship
    user = db.relationship('User', backref='score_alerts')
    
    def to_dict(self):
        """Convert score alert to dictionary - 同樣加上 JSON 安全防護"""
        import json
        
        # 1. 處理 exceeded_lines 的類型衝突
        lines_data = self.exceeded_lines
        if isinstance(lines_data, str): # 如果從資料庫出來是字串（如 SQLite）
            try:
                lines_data = json.loads(lines_data)
            except:
                lines_data = {}
        elif lines_data is None:
            lines_data = {}
        # 如果已經是 dict，則直接使用

        return {
            'id': self.id,
            'user_id': self.user_id,
            'alert_date': str(self.alert_date) if self.alert_date else None,
            'daily_average': float(self.daily_average) if self.daily_average else 0,
            'score_alerts_alert_type': self.alert_type, # 確保與前端對接的 key 一致
            'alert_type': self.alert_type,
            'exceeded_lines': lines_data, # 這裡現在保證是字典格式了
            'is_read': bool(self.is_read) if hasattr(self, 'is_read') else False,
            'created_at': str(self.created_at) if self.created_at else None
        }
