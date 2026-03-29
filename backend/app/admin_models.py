from app.models import db
from datetime import datetime

class HealthcareStaff(db.Model):
    """Healthcare staff model for admin users"""
    __tablename__ = 'healthcare_staff'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=True)  # 醫生、護理師等
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationship
    watchlist_items = db.relationship('PatientWatchlist', backref='staff', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert healthcare staff to dictionary - Safe version"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            # 修正點：使用 str() 避開 .isoformat() 的類型衝突
            'created_at': str(self.created_at) if self.created_at else None,
            'last_login': str(self.last_login) if hasattr(self, 'last_login') and self.last_login else None
        }


class PatientWatchlist(db.Model):
    """Patient watchlist model for tracking special attention patients"""
    __tablename__ = 'patient_watchlist'
    
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('healthcare_staff.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notes = db.Column(db.Text, nullable=True)  # 備註
    display_order = db.Column(db.Integer, default=0)  # 自訂顯示順序
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Ensure one staff can't add same patient twice
    __table_args__ = (
        db.UniqueConstraint('staff_id', 'patient_id', name='unique_staff_patient_watch'),
    )
    
    def to_dict(self):
        """Convert assignment to dictionary"""
        return {
            'id': self.id,
            'staff_id': self.staff_id,
            'patient_id': self.patient_id,
            'assigned_at': str(self.assigned_at) if self.assigned_at else None,
            # 如果有關聯對象，也一併回傳
            'patient_name': self.patient.name if hasattr(self, 'patient') and self.patient else None,
            'staff_name': self.staff.name if hasattr(self, 'staff') and self.staff else None
        }


class PatientAssignment(db.Model):
    """Patient-Nurse assignment model"""
    __tablename__ = 'patient_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('healthcare_staff.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_by = db.Column(db.Integer, db.ForeignKey('healthcare_staff.id'), nullable=True)  # Who assigned
    assigned_at = db.Column(db.DateTime, default=datetime.now)
    notes = db.Column(db.Text, nullable=True)
    
    # Ensure one patient can't be assigned to same nurse twice
    __table_args__ = (
        db.UniqueConstraint('staff_id', 'patient_id', name='unique_staff_patient_assignment'),
    )
    
    def to_dict(self):
        """Convert watchlist item to dictionary"""
        return {
            'id': self.id,
            'staff_id': self.staff_id,
            'patient_id': self.patient_id,
            'notes': self.notes,
            'display_order': self.display_order,
            'added_at': str(self.added_at) if hasattr(self, 'added_at') and self.added_at else None,
            # 確保布林值正確傳遞
            'is_active': bool(self.is_active) if hasattr(self, 'is_active') else True
        }

