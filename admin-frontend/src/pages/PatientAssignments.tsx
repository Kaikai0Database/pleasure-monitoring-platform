import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { patientsAPI } from '../services/api';
import { assignmentAPI } from '../services/assignmentAPI';
import './PatientAssignments.css';

interface Patient {
    id: number;
    name: string;
    email: string;
    nickname?: string;
}

interface Staff {
    id: number;
    name: string;
    email: string;
    role: string;
}

interface Assignment {
    id: number;
    patient_id: number;
    staff_id: number;
    patient?: Patient;
    staff?: Staff;
}

export default function PatientAssignments() {
    const navigate = useNavigate();
    const [patients, setPatients] = useState<Patient[]>([]);
    const [staffList, setStaffList] = useState<Staff[]>([]);
    const [assignments, setAssignments] = useState<Assignment[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            setLoading(true);
            const [patientsRes, staffRes, assignmentsRes] = await Promise.all([
                patientsAPI.getAll(),
                assignmentAPI.getStaffList(),
                assignmentAPI.getAll(),
            ]);

            if (patientsRes.data.success) {
                setPatients(patientsRes.data.patients);
            } else {
                console.error('[PatientAssignments] Patients response error:', patientsRes.data);
            }

            if (staffRes.data.success) {
                // 顯示所有 clinical 角色的醫護人員（醫師、護理師、心理師等）
                const clinicalStaff = staffRes.data.staff.filter((s: Staff) => s.role === 'clinical');
                setStaffList(clinicalStaff);
            } else {
                console.error('[PatientAssignments] Staff list error:', staffRes.data);
                // Show specific error message
                if (staffRes.data.message) {
                    alert(staffRes.data.message);
                }
            }

            if (assignmentsRes.data.success) {
                setAssignments(assignmentsRes.data.assignments);
            } else {
                console.error('[PatientAssignments] Assignments response error:', assignmentsRes.data);
            }
        } catch (err: any) {
            console.error('[PatientAssignments] Fetch error:', err);
            console.error('[PatientAssignments] Error response:', err.response);

            const errorMessage = err.response?.data?.message || '載入失敗';
            alert(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    const handleAssign = async (patientId: number, staffId: number) => {
        if (!staffId) {
            alert('請選擇醫護人員');
            return;
        }

        try {
            await assignmentAPI.assign(patientId, staffId);
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

    // Get assigned staff for a patient
    const getAssignedStaff = (patientId: number): Assignment[] => {
        return assignments.filter(a => a.patient_id === patientId);
    };

    if (loading) {
        return (
            <div className="assignments-container">
                <div className="loading">載入中...</div>
            </div>
        );
    }

    return (
        <div className="assignments-container">
            <div className="assignments-header">
                <h1>個案分配管理</h1>
                <p>將個案分配給醫護人員，醫護人員只能查看分配給自己的個案</p>
            </div>

            <div className="assignments-table-container">
                <table className="assignments-table">
                    <thead>
                        <tr>
                            <th>個案姓名</th>
                            <th>郵箱</th>
                            <th>已分配醫護人員</th>
                            <th>分配新醫護人員</th>
                        </tr>
                    </thead>
                    <tbody>
                        {patients.map((patient) => {
                            const assignedStaff = getAssignedStaff(patient.id);

                            return (
                                <tr key={patient.id}>
                                    <td>{patient.nickname || patient.name}</td>
                                    <td className="email-cell">{patient.email}</td>
                                    <td>
                                        {assignedStaff.length > 0 ? (
                                            <div className="assigned-staff-list">
                                                {assignedStaff.map((assignment) => (
                                                    <div key={assignment.id} className="assigned-staff-item">
                                                        <span>{assignment.staff?.name}</span>
                                                        <button
                                                            onClick={() => handleUnassign(assignment.id)}
                                                            className="unassign-btn"
                                                            title="取消分配"
                                                        >
                                                            ✕
                                                        </button>
                                                    </div>
                                                ))}
                                            </div>
                                        ) : (
                                            <span className="no-assignment">未分配</span>
                                        )}
                                    </td>
                                    <td>
                                        <div className="assign-controls">
                                            <select
                                                id={`staff-select-${patient.id}`}
                                                className="staff-select"
                                                defaultValue=""
                                            >
                                                <option value="">選擇醫護人員...</option>
                                                {staffList.map((staff) => (
                                                    <option key={staff.id} value={staff.id}>
                                                        {staff.name} ({staff.email})
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

                {patients.length === 0 && (
                    <div className="no-data">目前沒有個案資料</div>
                )}
            </div>

            <div className="staff-summary">
                <h3>醫護人員列表</h3>
                <div className="staff-list">
                    {staffList.map((staff) => {
                        const assignedCount = assignments.filter(
                            (a) => a.staff_id === staff.id
                        ).length;
                        return (
                            <div
                                key={staff.id}
                                className="staff-card clickable"
                                onClick={() => navigate(`/nurse/${staff.id}`)}
                            >
                                <div className="staff-name">{staff.name}</div>
                                <div className="staff-email">{staff.email}</div>
                                <div className="staff-assignments">
                                    已分配個案: {assignedCount} 位
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
