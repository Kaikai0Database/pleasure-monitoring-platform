from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, AssessmentHistory
from sqlalchemy import func, desc
from datetime import datetime, timedelta

admin_patients_bp = Blueprint('admin_patients', __name__)


def verify_admin():
    """Helper function to verify admin token"""
    identity = get_jwt_identity()
    if not identity.startswith('admin_'):
        return None
    return int(identity.replace('admin_', ''))


@admin_patients_bp.route('', methods=['GET'])
@jwt_required()
def get_patients():
    """Get all patients with their latest assessment info"""
    try:
        staff_id = verify_admin()
        if not staff_id:
            return jsonify({'success': False, 'message': '無效的管理員權限'}), 403
        
        # Get staff object to check role
        from app.admin_models import HealthcareStaff, PatientWatchlist, PatientAssignment
        staff = HealthcareStaff.query.get(staff_id)
        
        if not staff:
            return jsonify({'success': False, 'message': '找不到管理員資料'}), 403
        
        # Filter patients based on role
        if staff.role == 'super_admin':
            # Super admin can see all patients
            patients = User.query.all()
        else:
            # Regular nurse can only see assigned patients
            assignments = PatientAssignment.query.filter_by(staff_id=staff_id).all()
            patient_ids = [a.patient_id for a in assignments]
            
            if not patient_ids:
                # No assignments, return empty list
                return jsonify({
                    'success': True,
                    'patients': []
                }), 200
            
            patients = User.query.filter(User.id.in_(patient_ids)).all()
        
        result = []
        today = datetime.now().date()
        
        for patient in patients:
            # Get latest assessment
            latest_assessment = AssessmentHistory.query.filter_by(
                user_id=patient.id,
                is_deleted=False
            ).order_by(desc(AssessmentHistory.completed_at)).first()
            
            # Get total assessments count
            total_assessments = AssessmentHistory.query.filter_by(
                user_id=patient.id,
                is_deleted=False
            ).count()
            
            # Calculate average score
            avg_score = db.session.query(
                func.avg(AssessmentHistory.total_score)
            ).filter_by(
                user_id=patient.id,
                is_deleted=False
            ).scalar()
            
            patient_data = patient.to_dict()
            patient_data['latest_assessment'] = latest_assessment.to_dict() if latest_assessment else None
            patient_data['total_assessments'] = total_assessments
            patient_data['average_score'] = round(float(avg_score), 2) if avg_score else None
            
            # Check if patient has been inactive for 5+ days
            inactive_warning = False
            if patient.last_login_date:
                days_since_login = (today - patient.last_login_date).days
                if days_since_login >= 5:
                    inactive_warning = True
            else:
                # If never logged in, also mark as inactive
                inactive_warning = True
            
            patient_data['inactive_warning'] = inactive_warning
            
            # Check if patient is in this staff's watchlist
            is_in_watchlist = PatientWatchlist.query.filter_by(
                staff_id=staff_id,
                patient_id=patient.id
            ).first() is not None
            
            patient_data['is_in_watchlist'] = is_in_watchlist
            result.append(patient_data)
        
        return jsonify({
            'success': True,
            'patients': result
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'獲取病人列表失敗: {str(e)}'}), 500


@admin_patients_bp.route('/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_patient_detail(patient_id):
    """Get detailed information about a specific patient"""
    try:
        staff_id = verify_admin()
        if not staff_id:
            return jsonify({'success': False, 'message': '無效的管理員權限'}), 403
        
        patient = User.query.get(patient_id)
        if not patient:
            return jsonify({'success': False, 'message': '病人不存在'}), 404
        
        return jsonify({
            'success': True,
            'patient': patient.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'獲取病人詳情失敗: {str(e)}'}), 500


@admin_patients_bp.route('/<int:patient_id>/history', methods=['GET'])
@jwt_required()
def get_patient_history(patient_id):
    """Get patient's assessment history"""
    try:
        staff_id = verify_admin()
        if not staff_id:
            return jsonify({'success': False, 'message': '無效的管理員權限'}), 403
        
        # Verify patient exists
        patient = User.query.get(patient_id)
        if not patient:
            return jsonify({'success': False, 'message': '病人不存在'}), 404
        
        # Get assessment history
        histories = AssessmentHistory.query.filter_by(
            user_id=patient_id,
            is_deleted=False
        ).order_by(desc(AssessmentHistory.completed_at)).all()
        
        return jsonify({
            'success': True,
            'history': [h.to_dict() for h in histories]
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'獲取病人歷史記錄失敗: {str(e)}'}), 500


@admin_patients_bp.route('/<int:patient_id>/statistics', methods=['GET'])
@jwt_required()
def get_patient_statistics(patient_id):
    """Get patient's statistical data"""
    try:
        staff_id = verify_admin()
        if not staff_id:
            return jsonify({'success': False, 'message': '無效的管理員權限'}), 403
        
        # Verify patient exists
        patient = User.query.get(patient_id)
        if not patient:
            return jsonify({'success': False, 'message': '病人不存在'}), 404
        
        # Get all assessments
        assessments = AssessmentHistory.query.filter_by(
            user_id=patient_id,
            is_deleted=False
        ).order_by(AssessmentHistory.completed_at).all()
        
        if not assessments:
            return jsonify({
                'success': True,
                'statistics': {
                    'total_count': 0,
                    'average_score': None,
                    'highest_score': None,
                    'lowest_score': None,
                    'trend': []
                }
            }), 200
        
        # Calculate statistics
        scores = [a.total_score for a in assessments]
        avg_score = sum(scores) / len(scores)
        
        # Trend data - Group by date and calculate daily averages
        # Changed from 30 days filter to show all historical data
        # This allows viewing complete history including older test data
        
        # Group assessments by date (YYYY-MM-DD)
        from collections import defaultdict
        daily_assessments = defaultdict(list)
        for a in assessments:  # Use all assessments, not just recent ones
            date_key = a.completed_at.date()  # Get date without time
            daily_assessments[date_key].append(a)
        
        # Calculate daily averages
        trend_data = []
        for date_key in sorted(daily_assessments.keys()):
            day_assessments = daily_assessments[date_key]
            
            # Calculate average score for the day
            avg_score = sum(a.total_score for a in day_assessments) / len(day_assessments)
            # Assume max_score is consistent (use the first assessment's max_score)
            max_score = day_assessments[0].max_score
            avg_percentage = round((avg_score / max_score) * 100) if max_score > 0 else 0
            
            trend_data.append({
                'date': date_key.isoformat(),
                'score': round(avg_score, 2),
                'max_score': max_score,
                'percentage': avg_percentage
            })
        
        return jsonify({
            'success': True,
            'statistics': {
                'total_count': len(assessments),
                'average_score': round(avg_score, 2),
                'highest_score': max(scores),
                'lowest_score': min(scores),
                'trend': trend_data
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'獲取統計數據失敗: {str(e)}'}), 500


@admin_patients_bp.route('/alert-counts', methods=['GET'])
@jwt_required()
def get_patients_alert_counts():
    """Get unread alert details for all patients, including which lines were exceeded"""
    try:
        staff_id = verify_admin()
        if not staff_id:
            return jsonify({'success': False, 'message': '無效的管理員權限'}), 403
        
        from app.models import ScoreAlert
        import json
        
        # Get all unread alerts
        alerts = ScoreAlert.query.filter(
            ScoreAlert.is_read == False
        ).all()
        
        # Organize by patient_id and alert_type
        alert_details = {}
        
        for alert in alerts:
            patient_id = alert.user_id
            
            if patient_id not in alert_details:
                alert_details[patient_id] = {
                    'high': {'count': 0, 'lines': []},
                    'low': {'count': 0, 'lines': []}
                }
            
            # Parse exceeded_lines
            try:
                exceeded = json.loads(alert.exceeded_lines) if alert.exceeded_lines else {}
            except:
                exceeded = {}
            
            line_names = list(exceeded.keys())  # ['7日', '14日', '30日']
            
            if alert.alert_type == 'high':
                alert_details[patient_id]['high']['count'] += 1
                if line_names:
                    alert_details[patient_id]['high']['lines'].extend(line_names)
            else:
                alert_details[patient_id]['low']['count'] += 1
                if line_names:
                    alert_details[patient_id]['low']['lines'].extend(line_names)
        
        return jsonify({
            'success': True,
            'alert_counts': alert_details
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'獲取警告數量失敗: {str(e)}'}), 500

@admin_patients_bp.route('/<int:patient_id>/alerts', methods=['GET'])
@jwt_required()
def get_patient_alerts(patient_id):
    """Get alerts for a specific patient"""
    try:
        staff_id = verify_admin()
        if not staff_id:
            return jsonify({'success': False, 'message': '無效的管理員權限'}), 403
        
        from app.models import ScoreAlert
        
        # Get all alerts for this patient (ordered by date desc)
        alerts = ScoreAlert.query.filter_by(
            user_id=patient_id
        ).order_by(desc(ScoreAlert.alert_date)).all()
        
        return jsonify({
            'success': True,
            'alerts': [alert.to_dict() for alert in alerts]
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'獲取警告失敗: {str(e)}'}), 500
