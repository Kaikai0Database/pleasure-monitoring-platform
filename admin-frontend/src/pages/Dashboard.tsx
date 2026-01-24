import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { dashboardAPI, patientsAPI, watchlistAPI } from '../services/api';
import { type DashboardStats, type Patient } from '../types';
import './Dashboard.css';

export default function Dashboard() {
    const navigate = useNavigate();
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [allPatients, setAllPatients] = useState<Patient[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [groupFilter, setGroupFilter] = useState<'all' | 'student' | 'clinical'>('all');
    const [alertCounts, setAlertCounts] = useState<{
        [key: number]: {
            high: { count: number; lines: string[] };
            low: { count: number; lines: string[] }
        }
    }>({});

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            setLoading(true);
            const [statsRes, patientsRes, alertCountsRes] = await Promise.all([
                dashboardAPI.getStats(),
                patientsAPI.getAll(),
                patientsAPI.getAlertCounts(),
            ]);

            if (statsRes.data.success) {
                setStats(statsRes.data.stats);
            }
            if (patientsRes.data.success) {
                // 顯示所有病人，不篩選
                setAllPatients(patientsRes.data.patients);
            }
            if (alertCountsRes.data.success) {
                setAlertCounts(alertCountsRes.data.alert_counts || {});
            }
        } catch (err: any) {
            setError(err.response?.data?.message || '獲取數據失敗');
        } finally {
            setLoading(false);
        }
    };

    const handleAddToWatchlist = async (patientId: number, e: React.MouseEvent) => {
        e.stopPropagation(); // 防止觸發病人卡片點擊
        try {
            await watchlistAPI.add(patientId);
            alert('已添加到特別關注');
            // Refresh data to update button state
            fetchData();
        } catch (err: any) {
            alert(err.response?.data?.message || '添加失敗');
        }
    };

    const handlePatientClick = (patientId: number) => {
        navigate(`/patient/${patientId}`);
    };

    // Filter patients based on selected group
    const filteredPatients = allPatients.filter(patient => {
        if (groupFilter === 'all') return true;
        return patient.group === groupFilter;
    });

    const getFilterLabel = () => {
        switch (groupFilter) {
            case 'student': return '大學生組';
            case 'clinical': return '臨床組';
            case 'clinical': return '臨床組';
            default: return '總覽';
        }
    };

    if (loading) {
        return (
            <div className="dashboard-loading">
                <div className="spinner"></div>
                <p>載入中...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="dashboard-error">
                <p>❌ {error}</p>
                <button onClick={fetchData} className="retry-button">
                    重試
                </button>
            </div>
        );
    }

    return (
        <div className="dashboard-container">
            <div className="page-header">
                <h2 className="page-title">{getFilterLabel()}</h2>
                <div className="header-controls">
                    <select
                        className="group-filter-select"
                        value={groupFilter}
                        onChange={(e) => setGroupFilter(e.target.value as 'all' | 'student' | 'clinical')}
                    >
                        <option value="all">總覽</option>
                        <option value="clinical">🏥 臨床組</option>
                        <option value="student">🎓 大學生組</option>
                    </select>
                </div>
            </div>

            {/* 統計卡片 */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon-wrapper">
                        <div className="stat-icon">👥</div>
                    </div>
                    <div className="stat-content">
                        <div className="stat-label">總病人數</div>
                        <div className="stat-value">{stats?.total_patients || 0}</div>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon-wrapper">
                        <div className="stat-icon">🟢</div>
                    </div>
                    <div className="stat-content">
                        <div className="stat-label">今日活躍</div>
                        <div className="stat-value">{stats?.active_today || 0}</div>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon-wrapper">
                        <div className="stat-icon">📝</div>
                    </div>
                    <div className="stat-content">
                        <div className="stat-label">總評估次數</div>
                        <div className="stat-value">{stats?.total_assessments || 0}</div>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon-wrapper">
                        <div className="stat-icon">📊</div>
                    </div>
                    <div className="stat-content">
                        <div className="stat-label">平均分數</div>
                        <div className="stat-value">{stats?.average_score?.toFixed(1) || '0'}</div>
                    </div>
                </div>

                <div className="stat-card alert">
                    <div className="stat-icon-wrapper">
                        <div className="stat-icon">⭐</div>
                    </div>
                    <div className="stat-content">
                        <div className="stat-label">特別關注病人</div>
                        <div className="stat-value">{stats?.watchlist_count || 0}</div>
                    </div>
                </div>
            </div>

            {/* 所有病人列表 */}
            <div className="recent-patients-section">
                <h3 className="section-title">
                    {groupFilter === 'all' ? '所有病人' :
                        groupFilter === 'student' ? '大學生組病人' : '臨床組病人'}
                    <span className="patient-count">（{filteredPatients.length}人）</span>
                </h3>

                {filteredPatients.length === 0 ? (
                    <p className="no-data">
                        {groupFilter === 'all' ? '暫無病人數據' :
                            `目前${groupFilter === 'student' ? '大學生組' : '臨床組'}沒有病人`}
                    </p>
                ) : (
                    <div className="patients-table">
                        {filteredPatients.map((patient) => (
                            <div
                                key={patient.id}
                                className="patient-row"
                                onClick={() => handlePatientClick(patient.id)}
                            >
                                <div className="patient-info-section">
                                    <div className="patient-name-email">
                                        <div className="patient-name-text">
                                            {patient.name} {patient.nickname && <span className="patient-nickname-text">({patient.nickname})</span>}
                                            {patient.inactive_warning && (
                                                <span className="inactive-warning-icon" title="5天未登入">
                                                    ⚠️
                                                </span>
                                            )}
                                            {groupFilter === 'all' && patient.group && (
                                                <span
                                                    className={`group-badge ${patient.group}`}
                                                    title={patient.group === 'student' ? '大學生組（門檻≥24分）' : '臨床組（門檻≥29分）'}
                                                >
                                                    {patient.group === 'student' ? '🎓 大學生組' : '🏥 臨床組'}
                                                </span>
                                            )}
                                            {alertCounts[patient.id]?.high?.count > 0 && (
                                                <span
                                                    className="alert-bell-icon"
                                                    title={`穿越${alertCounts[patient.id].high.lines.join('線、')}線`}
                                                >
                                                    🔔
                                                </span>
                                            )}
                                            {alertCounts[patient.id]?.low?.count > 0 && (
                                                <span
                                                    className="alert-low-icon"
                                                    title={`接近${alertCounts[patient.id].low.lines.join('線、')}線`}
                                                >
                                                    📉
                                                </span>
                                            )}
                                        </div>
                                        <div className="patient-email-text">{patient.email}</div>
                                    </div>
                                </div>

                                <div className="patient-score-section">
                                    {patient.latest_assessment && (
                                        <>
                                            <span className="score-label">最新分數</span>
                                            <span className="score-text">
                                                {patient.latest_assessment.total_score}/{patient.latest_assessment.max_score}
                                            </span>
                                        </>
                                    )}
                                    {!patient.latest_assessment && (
                                        <span className="no-assessment">尚無評估</span>
                                    )}
                                </div>

                                <div className="patient-actions">
                                    <button
                                        onClick={(e) => handleAddToWatchlist(patient.id, e)}
                                        className={patient.is_in_watchlist ? 'watchlist-add-btn active' : 'watchlist-add-btn inactive'}
                                        title={patient.is_in_watchlist ? '已在特別關注' : '添加到特別關注'}
                                    >
                                        {patient.is_in_watchlist ? '⭐ 已關注' : '☆ 特別關注'}
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

