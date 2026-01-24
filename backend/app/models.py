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
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'daily_login_count': self.daily_login_count,
            'is_profile_completed': self.is_profile_completed,
            'nickname': self.nickname,
            'dob': self.dob.isoformat() if self.dob else None,
            'gender': self.gender,
            'height': self.height,
            'weight': self.weight,
            'education': self.education,
            'marital_status': self.marital_status,
            'marriage_other': self.marriage_other,
            'has_children': self.has_children,
            'children_count': self.children_count,
            'economic_status': self.economic_status,
            'family_structure': self.family_structure,
            'family_other': self.family_other,
            'has_job': self.has_job,
            'salary_range': self.salary_range,
            'location_city': self.location_city,
            'location_district': self.location_district,
            'living_situation': self.living_situation,
            'cohabitant_count': self.cohabitant_count,
            'religion': self.religion,
            'religion_other': self.religion_other,
            'group': self.group,
            'consecutive_days': self.calculate_streak()
        }

    def calculate_streak(self):
        """Calculate consecutive days of assessments"""
        if not self.histories:
            return 0
            
        # Get unique dates
        dates = sorted(list(set([h.completed_at.date() for h in self.histories])), reverse=True)
        if not dates:
            return 0
            
        from datetime import datetime
        today = datetime.now().date()
        
        # If no assessment today or yesterday, streak is broken (or 0 if strictly consecutive ending recently)
        # But if they login today, and last test was yesterday, is streak active? 
        # Usually streak allows 1 day gap (today not done yet).
        # Check if most recent is today or yesterday
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
        """Convert assessment history to dictionary"""
        percentage = round((self.total_score / self.max_score) * 100) if self.max_score > 0 else 0
        return {
            'id': self.id,
            'total_score': self.total_score,
            'max_score': self.max_score,
            'level': self.level,
            'percentage': percentage,
            'answers': json.loads(self.answers) if self.answers else [],
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'is_deleted': self.is_deleted,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
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
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'mood': self.mood,
            'content': self.content,
            'images': json.loads(self.images) if self.images else [],
            'period_marker': self.period_marker,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
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
        """Convert alert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'alert_date': self.alert_date.strftime('%Y-%m-%d') if self.alert_date else None,
            'daily_average': self.daily_average,
            'exceeded_lines': json.loads(self.exceeded_lines) if self.exceeded_lines else [],
            'alert_type': self.alert_type,
            'is_read': self.is_read,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
