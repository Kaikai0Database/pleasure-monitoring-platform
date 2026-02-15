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
        """Convert staff to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
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
        """Convert watchlist item to dictionary"""
        return {
            'id': self.id,
            'staff_id': self.staff_id,
            'patient_id': self.patient_id,
            'notes': self.notes,
            'display_order': self.display_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
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
        """Convert assignment to dictionary"""
        return {
            'id': self.id,
            'staff_id': self.staff_id,
            'patient_id': self.patient_id,
            'assigned_by': self.assigned_by,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'notes': self.notes
        }

