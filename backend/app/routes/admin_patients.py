from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, AssessmentHistory
from sqlalchemy import func, desc, cast, Date
from datetime import datetime, timedelta
import json

admin_patients_bp = Blueprint('admin_patients', __name__)


def verify_admin():
    """Helper function to verify admin token"""
    identity = get_jwt_identity()
    if not (identity and str(identity).startswith('admin_')):
        return None
    try:
        return int(str(identity).replace('admin_', ''))
    except:
        return None


@admin_patients_bp.route('', methods=['GET'])
@jwt_required()
def get_patients():
    """Get all patients with their latest assessment info"""
    # 核心修正：進入前先重設連線，清除可能卡住的 Transaction Error
    db.session.rollback()
    
    try:
        staff_id = verify_admin()
        if not staff_id:
            return jsonify({'success': False, 'message': '無效的管理員權限'}), 403
        
        from app.admin_models import HealthcareStaff, PatientWatchlist, PatientAssignment
        staff = HealthcareStaff.query.get(staff_id)
        
        if not staff:
            return jsonify({'success': False, 'message': '找不到管理員資料'}), 403
        
        if staff.role == 'super_admin':
            patients = User.query.all()
        else:
            assignments = PatientAssignment.query.filter_by(staff_id=staff_id).all()
            patient_ids = [a.patient_id for a in assignments]
            
            if not patient_ids:
                return jsonify({'success': True, 'patients': []}), 200
            
            patients = User.query.filter(User.id.in_(patient_ids)).all()
        
        result = []
        today = datetime.now().date()
        
        for patient in patients:
            # 獲取最新評估與統計 (使用 filter)
            latest_assessment = AssessmentHistory.query.filter_by(
                user_id=patient.id, is_deleted=False
            ).order_by(desc(AssessmentHistory.completed_at)).first()
            
            total_assessments = AssessmentHistory.query.filter_by(
                user_id=patient.id, is_deleted=False
            ).count()
            
            avg_score = db.session.query(func.avg(AssessmentHistory.total_score)).filter_by(
                user_id=patient.id, is_deleted=False
            ).scalar()
            
            patient_data = patient.to_dict()
            patient_data['latest_assessment'] = latest_assessment.to_dict() if latest_assessment else None
            patient_data['total_assessments'] = total_assessments
            patient_data['average_score'] = round(float(avg_score), 2) if avg_score else None
            
            # --- 核心修正：安全計算未登入天數 ---
            inactive_warning = False
            last_login = patient.last_login_date
            
            if last_login:
                # 如果是字串格式，手動轉換為 date 物件
                if isinstance(last_login, str):
                    try:
                        last_login = datetime.strptime(last_login[:10], '%Y-%m-%d').date()
                    except:
                        last_login = None
                
                # 只有在成功取得日期物件後才進行減法
                if last_login and hasattr(last_login, 'year'):
                    days_since_login = (today - last_login).days
                    if days_since_login >= 5:
                        inactive_warning = True
                else:
                    inactive_warning = True
            else:
                inactive_warning = True
            
            patient_data['inactive_warning'] = inactive_warning
            
            # 檢查追蹤名單
            is_in_watchlist = PatientWatchlist.query.filter_by(
                staff_id=staff_id, patient_id=patient.id
            ).first() is not None
            
            patient_data['is_in_watchlist'] = is_in_watchlist
            result.append(patient_data)
        
        return jsonify({'success': True, 'patients': result}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'獲取病人列表失敗: {str(e)}'}), 500


@admin_patients_bp.route('/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_patient_detail(patient_id):
    db.session.rollback()
    try:
        staff_id = verify_admin()
        if not staff_id:
            return jsonify({'success': False, 'message': '無效的管理員權限'}), 403
        
        patient = User.query.get(patient_id)
        if not patient:
            return jsonify({'success': False, 'message': '病人不存在'}), 404
        
        return jsonify({'success': True, 'patient': patient.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'獲取病人詳情失敗: {str(e)}'}), 500


@admin_patients_bp.route('/<int:patient_id>/statistics', methods=['GET'])
@jwt_required()
def get_patient_statistics(patient_id):
    db.session.rollback()
    try:
        staff_id = verify_admin()
        if not staff_id:
            return jsonify({'success': False, 'message': '無效的管理員權限'}), 403
        
        patient = User.query.get(patient_id)
        if not patient:
            return jsonify({'success': False, 'message': '病人不存在'}), 404
        
        assessments = AssessmentHistory.query.filter_by(
            user_id=patient_id, is_deleted=False
        ).order_by(AssessmentHistory.completed_at).all()
        
        if not assessments:
            return jsonify({
                'success': True,
                'statistics': {'total_count': 0, 'average_score': None, 'trend': []}
            }), 200
        
        scores = [a.total_score for a in assessments]
        from collections import defaultdict
        daily_assessments = defaultdict(list)
        
        for a in assessments:
            # --- 核心修正：安全處理 completed_at 轉日期 ---
            dt = a.completed_at
            if isinstance(dt, str):
                try:
                    dt_obj = datetime.strptime(dt[:10], '%Y-%m-%d').date()
                except:
                    continue
            else:
                dt_obj = dt.date() if hasattr(dt, 'date') else None
                
            if dt_obj:
                daily_assessments[dt_obj].append(a)
        
        trend_data = []
        for date_key in sorted(daily_assessments.keys()):
            day_assessments = daily_assessments[date_key]
            day_avg = sum(a.total_score for a in day_assessments) / len(day_assessments)
            max_score = day_assessments[0].max_score
            avg_percentage = round((day_avg / max_score) * 100) if max_score > 0 else 0
            
            trend_data.append({
                'date': date_key.isoformat(),
                'score': round(day_avg, 2),
                'max_score': max_score,
                'percentage': avg_percentage
            })
        
        return jsonify({
            'success': True,
            'statistics': {
                'total_count': len(assessments),
                'average_score': round(sum(scores)/len(scores), 2),
                'highest_score': max(scores),
                'lowest_score': min(scores),
                'trend': trend_data
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'獲取統計數據失敗: {str(e)}'}), 500


@admin_patients_bp.route('/alert-counts', methods=['GET'])
@jwt_required()
def get_patients_alert_counts():
    db.session.rollback()
    try:
        staff_id = verify_admin()
        if not staff_id:
            return jsonify({'success': False, 'message': '無效的管理員權限'}), 403
        
        from app.models import ScoreAlert
        # 修正：加上 db.session.rollback() 預防之前的格式錯誤堵塞
        alerts = ScoreAlert.query.filter(ScoreAlert.is_read == False).all()
        
        alert_details = {}
        for alert in alerts:
            p_id = alert.user_id
            if p_id not in alert_details:
                alert_details[p_id] = {'high': {'count': 0, 'lines': []}, 'low': {'count': 0, 'lines': []}}
            
            try:
                exceeded = json.loads(alert.exceeded_lines) if alert.exceeded_lines else {}
            except:
                exceeded = {}
            
            line_names = list(exceeded.keys())
            if alert.alert_type == 'high':
                alert_details[p_id]['high']['count'] += 1
                alert_details[p_id]['high']['lines'].extend(line_names)
            else:
                alert_details[p_id]['low']['count'] += 1
                alert_details[p_id]['low']['lines'].extend(line_names)
        
        return jsonify({'success': True, 'alert_counts': alert_details}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'獲獲取警告數量失敗: {str(e)}'}), 500
