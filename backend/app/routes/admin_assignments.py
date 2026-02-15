from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User
from app.admin_models import HealthcareStaff, PatientAssignment
from datetime import datetime

admin_assignments_bp = Blueprint('admin_assignments', __name__)


def verify_admin():
    """Helper function to verify admin token and return staff object"""
    identity = get_jwt_identity()
    if not identity.startswith('admin_'):
        return None
    staff_id = int(identity.replace('admin_', ''))
    return HealthcareStaff.query.get(staff_id)


@admin_assignments_bp.route('', methods=['GET'])
@jwt_required()
def get_assignments():
    """Get all assignments (super_admin) or own assignments (nurse)"""
    try:
        staff = verify_admin()
        if not staff:
            return jsonify({'success': False, 'message': '無效的管理員權限'}), 403
        
        if staff.role == 'super_admin':
            # Super admin sees all assignments
            assignments = PatientAssignment.query.all()
        else:
            # Nurse sees only their own assignments
            assignments = PatientAssignment.query.filter_by(staff_id=staff.id).all()
        
        # Get patient and staff info for each assignment
        result = []
        for assignment in assignments:
            patient = User.query.get(assignment.patient_id)
            assigned_staff = HealthcareStaff.query.get(assignment.staff_id)
            
            assignment_dict = assignment.to_dict()
            assignment_dict['patient'] = patient.to_dict() if patient else None
            assignment_dict['staff'] = assigned_staff.to_dict() if assigned_staff else None
            
            result.append(assignment_dict)
        
        return jsonify({
            'success': True,
            'assignments': result
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'獲取分配列表失敗: {str(e)}'}), 500


@admin_assignments_bp.route('', methods=['POST'])
@jwt_required()
def create_assignment():
    """Assign a patient to a nurse (super_admin only)"""
    try:
        staff = verify_admin()
        if not staff:
            return jsonify({'success': False, 'message': '無效的管理員權限'}), 403
        
        # Only super admin can assign
        if staff.role != 'super_admin':
            return jsonify({'success': False, 'message': '只有超級管理員可以分配病人'}), 403
        
        data = request.get_json()
        patient_id = data.get('patient_id')
        staff_id = data.get('staff_id')
        notes = data.get('notes', '')
        
        if not patient_id or not staff_id:
            return jsonify({'success': False, 'message': '缺少必要參數'}), 400
        
        # Check if patient exists
        patient = User.query.get(patient_id)
        if not patient:
            return jsonify({'success': False, 'message': '病人不存在'}), 404
        
        # Check if target staff exists
        target_staff = HealthcareStaff.query.get(staff_id)
        if not target_staff:
            return jsonify({'success': False, 'message': '護理師不存在'}), 404
        
        # Check if assignment already exists
        existing = PatientAssignment.query.filter_by(
            staff_id=staff_id,
            patient_id=patient_id
        ).first()
        
        if existing:
            return jsonify({'success': False, 'message': '此病人已分配給該護理師'}), 400
        
        # Create assignment
        assignment = PatientAssignment(
            staff_id=staff_id,
            patient_id=patient_id,
            assigned_by=staff.id,
            notes=notes
        )
        
        db.session.add(assignment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '分配成功',
            'assignment': assignment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'分配失敗: {str(e)}'}), 500


@admin_assignments_bp.route('/<int:assignment_id>', methods=['DELETE'])
@jwt_required()
def delete_assignment(assignment_id):
    """Remove an assignment (super_admin only)"""
    try:
        staff = verify_admin()
        if not staff:
            return jsonify({'success': False, 'message': '無效的管理員權限'}), 403
        
        # Only super admin can unassign
        if staff.role != 'super_admin':
            return jsonify({'success': False, 'message': '只有超級管理員可以取消分配'}), 403
        
        assignment = PatientAssignment.query.get(assignment_id)
        if not assignment:
            return jsonify({'success': False, 'message': '分配記錄不存在'}), 404
        
        db.session.delete(assignment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '取消分配成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'取消分配失敗: {str(e)}'}), 500


@admin_assignments_bp.route('/staff', methods=['GET'])
@jwt_required()
def get_staff_list():
    """Get list of all staff (for dropdown)"""
    try:
        staff = verify_admin()
        if not staff:
            return jsonify({'success': False, 'message': '無效的管理員權限'}), 403
        
        # Only super admin can see staff list
        if staff.role != 'super_admin':
            return jsonify({'success': False, 'message': '無權限查看護理師列表'}), 403
        
        # Get all staff members
        all_staff = HealthcareStaff.query.all()
        
        return jsonify({
            'success': True,
            'staff': [s.to_dict() for s in all_staff]
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'獲取護理師列表失敗: {str(e)}'}), 500
