import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { assignmentAPI } from '../services/assignmentAPI';
import { patientsAPI } from '../services/api';
import { type Patient, type HealthcareStaff } from '../types';
import './NurseDetail.css';

interface Assignment {
    id: number;
    patient_id: number;
    staff_id: number;
    patient?: Patient;
}

export default function NurseDetail() {
    const { nurseId } = useParams<{ nurseId: string }>();
    const navigate = useNavigate();
    const [nurse, setNurse] = useState<HealthcareStaff | null>(null);
    const [allPatients, setAllPatients] = useState<Patient[]>([]);
    const [assignments, setAssignments] = useState<Assignment[]>([]);
    const [staffList, setStaffList] = useState<HealthcareStaff[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
    }, [nurseId]);

    const fetchData = async () => {
        try {
            setLoading(true);
            const [staffRes, patientsRes, assignmentsRes] = await Promise.all([
                assignmentAPI.getStaffList(),
                patientsAPI.getAll(),
                assignmentAPI.getAll(),
            ]);

            if (staffRes.data.success) {
                const nurses = staffRes.data.staff;
                setStaffList(nurses);

                // Find current nurse
                const currentNurse = nurses.find((s: HealthcareStaff) => s.id === parseInt(nurseId || '0'));
                setNurse(currentNurse || null);
            }

            if (patientsRes.data.success) {
                setAllPatients(patientsRes.data.patients);
            }

            if (assignmentsRes.data.success) {
                // Filter assignments for this nurse
                const nurseAssignments = assignmentsRes.data.assignments.filter(
                    (a: Assignment) => a.staff_id === parseInt(nurseId || '0')
                );
                setAssignments(nurseAssignments);
            }
        } catch (err: any) {
            console.error('Failed to fetch data:', err);
            alert(err.response?.data?.message || '載入失敗');
        } finally {
            setLoading(false);
        }
    };

    const handleAssign = async (patientId: number, newStaffId: number) => {
        if (!newStaffId) {
            alert('請選擇護理師');
            return;
        }

        try {
            await assignmentAPI.assign(patientId, newStaffId);
            alert('分配成功');
            fetchData(); // Refresh
        } catch (err: any) {
            alert(err.response?.data?.message || '分配失敗');
        }
    };

    const handleUnassign = async (assignmentId: number) => {
        if (!confirm('確定要取消此分配嗎？')) {
            return;
        }

        try {
            await assignmentAPI.unassign(assignmentId);
            alert('取消分配成功');
            fetchData(); // Refresh
        } catch (err: any) {
            alert(err.response?.data?.message || '取消分配失敗');
        }
    };

    // Get assignment for a patient
    const getAssignment = (patientId: number) => {
        return assignments.find(a => a.patient_id === patientId);
    };

    if (loading) {
        return (
            <div className="nurse-detail-container">
                <div className="loading">載入中...</div>
            </div>
        );
    }

    if (!nurse) {
        return (
            <div className="nurse-detail-container">
                <div className="error">找不到護理師資料</div>
            </div>
        );
    }

    // Patients assigned to this nurse
    const assignedPatientIds = assignments.map(a => a.patient_id);
    const assignedPatients = allPatients.filter(p => assignedPatientIds.includes(p.id));

    return (
        <div className="nurse-detail-container">
            <div className="nurse-header">
                <button onClick={() => navigate(-1)} className="back-button">
                    ← 返回
                </button>
                <div className="nurse-info">
                    <h1>{nurse.name} 的病人列表</h1>
                    <p className="nurse-email">{nurse.email}</p>
                    <p className="patient-count">已分配 {assignedPatients.length} 位病人</p>
                </div>
            </div>

            <div className="patients-table-container">
                <table className="patients-table">
                    <thead>
                        <tr>
                            <th>病人姓名</th>
                            <th>郵箱</th>
                            <th>已分配護理師</th>
                            <th>分配護理師</th>
                        </tr>
                    </thead>
                    <tbody>
                        {assignedPatients.map((patient) => {
                            const assignment = getAssignment(patient.id);

                            return (
                                <tr key={patient.id}>
                                    <td>{patient.nickname || patient.name}</td>
                                    <td className="email-cell">{patient.email}</td>
                                    <td>
                                        {assignment ? (
                                            <div className="assigned-nurse">
                                                <span>{nurse.name}</span>
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleUnassign(assignment.id);
                                                    }}
                                                    className="unassign-small-btn"
                                                    title="取消分配"
                                                >
                                                    ✕
                                                </button>
                                            </div>
                                        ) : (
                                            <span className="not-assigned">未分配</span>
                                        )}
                                    </td>
                                    <td>
                                        <div className="assign-controls">
                                            <select
                                                id={`staff-select-${patient.id}`}
                                                className="staff-select"
                                                defaultValue=""
                                            >
                                                <option value="">選擇護理師...</option>
                                                {staffList.filter(s => s.role === 'nurse').map((staff) => (
                                                    <option key={staff.id} value={staff.id}>
                                                        {staff.name}
                                                    </option>
                                                ))}
                                            </select>
                                            <button
                                                onClick={() => {
                                                    const select = document.getElementById(
                                                        `staff-select-${patient.id}`
                                                    ) as HTMLSelectElement;
                                                    const staffId = parseInt(select.value);
                                                    if (staffId) {
                                                        handleAssign(patient.id, staffId);
                                                    }
                                                }}
                                                className="assign-btn"
                                            >
                                                分配
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>

                {assignedPatients.length === 0 && (
                    <div className="no-data">此護理師目前沒有分配的病人</div>
                )}
            </div>
        </div>
    );
}
