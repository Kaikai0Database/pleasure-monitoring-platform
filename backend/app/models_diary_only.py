"""
Diary model
"""
from datetime import datetime
from . import db
import json

class Diary(db.Model):
    """Diary model - 支援一天多筆日記"""
    __tablename__ = 'diaries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    mood = db.Column(db.String(50), nullable=True)
    content = db.Column(db.Text, nullable=True)
    images = db.Column(db.Text, nullable=True)
    period_marker = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 明確禁用任何約束
    __table_args__ = {'extend_existing': True}
    
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
