from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, AssessmentHistory, User
from app.admin_models import PatientAssignment, PatientWatchlist, HealthcareStaff
from sqlalchemy import desc
from datetime import datetime, timedelta
import json

history_bp = Blueprint('history', __name__)

@history_bp.route('', methods=['GET'])
@jwt_required()
def get_history():
    """Get user's assessment history (active only)"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # 1. 自動清理垃圾桶 (加入 rollback 保護)
        try:
            ten_days_ago = datetime.now() - timedelta(days=10)
            
            # 這裡我們用比較保險的過濾方式
            old_trash = AssessmentHistory.query.filter(
                AssessmentHistory.is_deleted == True,
                AssessmentHistory.deleted_at < ten_days_ago
            ).all()
            
            for item in old_trash:
                db.session.delete(item)
            
            if old_trash:
                db.session.commit()
        except Exception as e:
            db.session.rollback() # 重要：出錯立刻回滾，不影響下面的查詢
            print(f"Auto-cleanup failed: {e}")

        # 2. 獲取正常歷史紀錄
        # 加上 try-except 以防止 is_deleted 類型衝突導致 Transaction Aborted
        try:
            histories = AssessmentHistory.query.filter_by(
                user_id=current_user_id,
                is_deleted=False
            ).order_by(AssessmentHistory.completed_at.desc()).all()
            
            return jsonify({
                'success': True,
                'history': [h.to_dict() for h in histories]
            }), 200
        except Exception as inner_e:
            db.session.rollback() # 如果這裡失敗，也必須回滾
            print(f"Database query failed: {inner_e}")
            return jsonify({'success': False, 'message': '資料庫讀取異常'}), 500
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'獲取歷史記錄失敗: {str(e)}'}), 500


@history_bp.route('/trash', methods=['GET'])
@jwt_required()
def get_trash():
    """Get user's deleted history (recycle bin)"""
    try:
        current_user_id = int(get_jwt_identity())
        
        trash_items = AssessmentHistory.query.filter_by(
            user_id=current_user_id,
            is_deleted=True
        ).order_by(AssessmentHistory.deleted_at.desc()).all()
        
        return jsonify({
            'success': True,
            'history': [h.to_dict() for h in trash_items]
        }), 200
        
    except Exception as e:
        db.session.rollback() # 確保出錯時清理連線
        return jsonify({'success': False, 'message': f'獲取回收桶失敗: {str(e)}'}), 500


@history_bp.route('', methods=['POST'])
@jwt_required()
def save_history():
    """Save new assessment result"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data or not all(key in data for key in ['total_score', 'max_score', 'answers']):
            return jsonify({'success': False, 'message': '缺少必要欄位'}), 400
        
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'success': False, 'message': '找不到用戶'}), 404
        
        total_score = data['total_score']
        if user.group == 'student':
            level = '需要關注' if total_score >= 23 else '良好'
        else:
            level = '需要關注' if total_score >= 30 else '良好'
        
        new_history = AssessmentHistory(
            user_id=current_user_id,
            total_score=total_score,
            max_score=data['max_score'],
            level=level,
            answers=json.dumps(data['answers'], ensure_ascii=False),
            completed_at=datetime.now()
        )
        
        db.session.add(new_history)
        db.session.commit()
        
        # --- 自動關注邏輯 (加入保護) ---
        try:
            threshold_met = False
            if user.group == 'student' and total_score >= 23:
                threshold_met = True
            elif user.group == 'clinical' and total_score >= 30:
                threshold_met = True
                
            if threshold_met:
                target_staff_ids = []
                assignments = PatientAssignment.query.filter_by(patient_id=current_user_id).all()
                if assignments:
                    target_staff_ids = [a.staff_id for a in assignments]
                
                if not target_staff_ids:
                    super_admin = HealthcareStaff.query.filter_by(role='super_admin').first()
                    if super_admin:
                        target_staff_ids.append(super_admin.id)
                
                for staff_id in target_staff_ids:
                    exists = PatientWatchlist.query.filter_by(staff_id=staff_id, patient_id=current_user_id).first()
                    if not exists:
                        max_order = db.session.query(db.func.max(PatientWatchlist.display_order)).filter_by(staff_id=staff_id).scalar() or 0
                        new_watchlist = PatientWatchlist(
                            staff_id=staff_id,
                            patient_id=current_user_id,
                            notes=f"自動關注：分數達標 ({total_score}分 - {user.group})",
                            display_order=max_order + 1
                        )
                        db.session.add(new_watchlist)
                db.session.commit()
        except Exception as w_err:
            db.session.rollback() # 自動關注失敗不應影響主流程
            print(f"Auto-watchlist failed: {w_err}")

        # --- 提醒通知邏輯 (加入強壯日期保護) ---
        try:
            from app.utils.alert_utils import check_and_create_alert
            # 確保傳入的是 date 物件，避開類型衝突
            test_date = new_history.completed_at
            if hasattr(test_date, 'date'):
                test_date = test_date.date()
            
            alerts = check_and_create_alert(current_user_id, test_date)
            if alerts:
                for alert in alerts:
                    print(f"Alert created for user {current_user_id}")
        except Exception as alert_error:
            db.session.rollback() # 提醒失敗也要重設連線
            print(f"Alert check failed: {alert_error}")
        
        return jsonify({
            'success': True,
            'history_id': new_history.id,
            'level': level,
            'message': '評估結果已保存'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'保存失敗: {str(e)}'}), 500


@history_bp.route('/<int:history_id>', methods=['DELETE'])
@jwt_required()
def delete_history(history_id):
    """Soft delete a history record"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        delete_reason = data.get('reason', '未指定原因')
        permanent = data.get('permanent', False)
        
        history = AssessmentHistory.query.get(history_id)
        if not history:
            return jsonify({'success': False, 'message': '記錄不存在'}), 404
        
        if history.user_id != current_user_id:
            return jsonify({'success': False, 'message': '無權限刪除此記錄'}), 403
        
        if permanent:
            db.session.delete(history)
            message = '記錄已永久刪除'
        else:
            history.is_deleted = True
            history.deleted_at = datetime.now()
            history.delete_reason = delete_reason
            message = '記錄已移至回收桶'
        
        db.session.commit()
        return jsonify({'success': True, 'message': message}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'刪除失敗: {str(e)}'}), 500


@history_bp.route('/<int:history_id>/restore', methods=['POST'])
@jwt_required()
def restore_history(history_id):
    """Restore a deleted history record"""
    try:
        current_user_id = int(get_jwt_identity())
        history = AssessmentHistory.query.get(history_id)
        
        if not history:
            return jsonify({'success': False, 'message': '記錄不存在'}), 404
        
        if history.user_id != current_user_id:
            return jsonify({'success': False, 'message': '無權限操作此記錄'}), 403
            
        history.is_deleted = False
        history.deleted_at = None
        history.delete_reason = None
        
        user = User.query.get(current_user_id)
        if user and user.group == 'student':
            history.level = '需要關注' if history.total_score >= 23 else '良好'
        else:
            history.level = '需要關注' if history.total_score >= 30 else '良好'
        
        db.session.commit()
        return jsonify({'success': True, 'message': '記錄已還原'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'還原失敗: {str(e)}'}), 500
