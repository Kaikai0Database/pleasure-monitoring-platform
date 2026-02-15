from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, AssessmentHistory
from sqlalchemy import func, desc
from datetime import datetime, timedelta

admin_dashboard_bp = Blueprint('admin_dashboard', __name__)


def verify_admin():
    """Helper function to verify admin token"""
    identity = get_jwt_identity()
    if not identity.startswith('admin_'):
        return None
    return int(identity.replace('admin_', ''))


@admin_dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get overall statistics for dashboard"""
    try:
        staff_id = verify_admin()
        if not staff_id:
            return jsonify({'success': False, 'message': '無效的管理員權限'}), 403
        
        # Total patients
        total_patients = User.query.count()
        
        # Active patients today (had assessment today)
        today = datetime.now().date()
        active_today = db.session.query(AssessmentHistory.user_id).filter(
            func.date(AssessmentHistory.completed_at) == today,
            AssessmentHistory.is_deleted == False
        ).distinct().count()
        
        # Total assessments
        total_assessments = AssessmentHistory.query.filter_by(is_deleted=False).count()
        
        # Average score across all assessments
        avg_score = db.session.query(
            func.avg(AssessmentHistory.total_score)
        ).filter_by(is_deleted=False).scalar()
        
        # Get watchlist count for this staff member
        from app.admin_models import PatientWatchlist
        watchlist_count = PatientWatchlist.query.filter_by(
            staff_id=staff_id
        ).count()
        
        # Get recent assessments for activity chart (last 7 days)
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_activity = []
        
        for i in range(7):
            date = datetime.now().date() - timedelta(days=6-i)
            count = AssessmentHistory.query.filter(
                func.date(AssessmentHistory.completed_at) == date,
                AssessmentHistory.is_deleted == False
            ).count()
            
            recent_activity.append({
                'date': date.isoformat(),
                'count': count
            })
        
        # Get patients with recent assessments (last 7 days)
        recent_patient_assessments = db.session.query(
            User,
            AssessmentHistory
        ).join(
            AssessmentHistory, User.id == AssessmentHistory.user_id
        ).filter(
            AssessmentHistory.completed_at >= seven_days_ago,
            AssessmentHistory.is_deleted == False
        ).order_by(
            desc(AssessmentHistory.completed_at)
        ).limit(10).all()
        
        recent_patients = []
        seen_patients = set()
        for user, assessment in recent_patient_assessments:
            if user.id not in seen_patients:
                patient_data = user.to_dict()
                patient_data['latest_assessment'] = assessment.to_dict()
                
                # Check if patient has been inactive for 5+ days
                inactive_warning = False
                if user.last_login_date:
                    days_since_login = (today - user.last_login_date).days
                    if days_since_login >= 5:
                        inactive_warning = True
                else:
                    # If never logged in, also mark as inactive
                    inactive_warning = True
                
                patient_data['inactive_warning'] = inactive_warning
                recent_patients.append(patient_data)
                seen_patients.add(user.id)
        
        return jsonify({
            'success': True,
            'stats': {
                'total_patients': total_patients,
                'active_today': active_today,
                'total_assessments': total_assessments,
                'average_score': round(float(avg_score), 2) if avg_score else 0,
                'watchlist_count': watchlist_count,
                'recent_activity': recent_activity,
                'recent_patients': recent_patients
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'獲取統計數據失敗: {str(e)}'}), 500
