from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, AssessmentHistory
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import json

admin_patients_bp = Blueprint('admin_patients', __name__)

def verify_admin():
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
    db.session.rollback() # 一進來先重設
    try:
        staff_id = verify_admin()
        if not staff_id: return jsonify({'success': False, 'message': '權限不足'}), 403
        
        from app.admin_models import HealthcareStaff, PatientWatchlist, PatientAssignment
        staff = HealthcareStaff.query.get(staff_id)
        
        # 1. 一次性抓出所有權限內的病人
        if staff.role == 'super_admin':
            patients = User.query.all()
        else:
            assignments = PatientAssignment.query.filter_by(staff_id=staff_id).all()
            p_ids = [a.patient_id for a in assignments]
            if not p_ids: return jsonify({'success': True, 'patients': []}), 200
            patients = User.query.filter(User.id.in_(p_ids)).all()

        p_ids = [p.id for p in patients]
        
        # 批量獲取 Watchlist 狀態
        watch_list_records = PatientWatchlist.query.filter(
            PatientWatchlist.staff_id == staff_id,
            PatientWatchlist.patient_id.in_(p_ids)
        ).all() if p_ids else []
        watched_pids = {w.patient_id for w in watch_list_records}

        # 批量獲取最新 AssessmentHistory (以每個 user_id 依據 completed_at 取第一筆)
        # 用 dict 加快讀取。考慮效能，用一條 Query 做出來，也可以全都拉出來按時間排序取第一筆
        # 我們直接取這批人的所有記錄，用 Python 去重：
        histories = AssessmentHistory.query.filter(
            AssessmentHistory.user_id.in_(p_ids),
            AssessmentHistory.is_deleted == False
        ).order_by(desc(AssessmentHistory.completed_at)).all() if p_ids else []
        
        latest_map = {}
        for h in histories:
            if h.user_id not in latest_map:
                latest_map[h.user_id] = h

        # 2. 獲取所有人的最新評估 (不在迴圈內部打 SQL)
        result = []
        today = datetime.now().date()

        for patient in patients:
            try:
                # 這裡只抓最核心的資料，不再用 db 查詢
                latest = latest_map.get(patient.id)
                
                # 計算未登入天數 (防禦性寫法)
                last_login = patient.last_login_date
                inactive = False
                if last_login:
                    if isinstance(last_login, str):
                        try: last_login = datetime.strptime(last_login[:10], '%Y-%m-%d').date()
                        except: last_login = None
                    elif hasattr(last_login, 'date'):
                        last_login = last_login.date()

                    if last_login and (today - last_login).days >= 5:
                        inactive = True
                else: inactive = True

                # 組裝資料，如果 patient.to_dict() 壞了，我們手動組
                p_data = {
                    'id': patient.id,
                    'name': patient.name,
                    'email': patient.email,
                    'group': patient.group,
                    'inactive_warning': inactive,
                    'latest_assessment': latest.to_dict() if latest else None,
                    'is_in_watchlist': patient.id in watched_pids
                }
                result.append(p_data)
            except Exception as item_err:
                print(f"跳過錯誤個案 {patient.id}: {item_err}")
                continue # 某個病人資料壞了不要卡住整頁
            
        return jsonify({'success': True, 'patients': result}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '伺服器繁忙，請稍後再試'}), 500


@admin_patients_bp.route('/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_patient_detail(patient_id):
    db.session.rollback()
    try:
        # 修正：直接從 User 表查，不要加太多複雜的關聯
        patient = User.query.filter_by(id=patient_id).first()
        if not patient:
            # 如果真的查不到，日誌會顯示 ID
            print(f"❌ 查無此個案 ID: {patient_id}")
            return jsonify({'success': False, 'message': '個案不存在'}), 404
        
        # 使用我們修正後的安全 to_dict
        return jsonify({
            'success': True,
            'patient': patient.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"🔥 讀取詳情崩潰: {str(e)}")
        return jsonify({'success': False, 'message': '讀取失敗'}), 500


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
