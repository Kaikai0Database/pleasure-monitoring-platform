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
            }

            if (staffRes.data.success) {
                // Filter out super admins, only show nurses
                const nurses = staffRes.data.staff.filter((s: Staff) => s.role === 'nurse');
                setStaffList(nurses);
            }

            if (assignmentsRes.data.success) {
                setAssignments(assignmentsRes.data.assignments);
            }
        } catch (err: any) {
            console.error('Failed to fetch data:', err);
            alert(err.response?.data?.message || '載入失敗');
        } finally {
            setLoading(false);
        }
    };

    const handleAssign = async (patientId: number, staffId: number) => {
        if (!staffId) {
            alert('請選擇護理師');
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
                <h1>病人分配管理</h1>
                <p>將病人分配給護理師，護理師只能查看分配給自己的病人</p>
            </div>

            <div className="assignments-table-container">
                <table className="assignments-table">
                    <thead>
                        <tr>
                            <th>病人姓名</th>
                            <th>郵箱</th>
                            <th>已分配護理師</th>
                            <th>分配新護理師</th>
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
                                                <option value="">選擇護理師...</option>
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
                    <div className="no-data">目前沒有病人資料</div>
                )}
            </div>

            <div className="staff-summary">
                <h3>護理師列表</h3>
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
                                    已分配病人: {assignedCount} 位
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
