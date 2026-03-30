import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from 'recharts';
import { patientsAPI, watchlistAPI, diaryAPI } from '../services/api';
import { type Patient, type Assessment, type Statistics, type Diary } from '../types';
import { DailyScoreChart } from '../components/DailyScoreChart';
import { downloadCSV, downloadChartAsPNG } from '../utils/chartDownloadUtils';
import { CustomMATooltip } from '../components/CustomMATooltip';
import './PatientDetail.css';

type ViewTab = 'history' | 'profile' | 'diary';

export default function PatientDetail() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [patient, setPatient] = useState<Patient | null>(null);
    const [history, setHistory] = useState<Assessment[]>([]);
    const [statistics, setStatistics] = useState<Statistics | null>(null);
    const [diaries, setDiaries] = useState<Diary[]>([]);
    const [loading, setLoading] = useState(true);
    const [isInWatchlist, setIsInWatchlist] = useState(false);
    const [activeTab, setActiveTab] = useState<ViewTab>('history');
    const [latestHighAlert, setLatestHighAlert] = useState<any>(null);
    const [latestLowAlert, setLatestLowAlert] = useState<any>(null);
    const [selectedDiary, setSelectedDiary] = useState<Diary | null>(null);

    // Chart refs for PNG download
    const multiLineChartRef = useRef<HTMLDivElement>(null);
    const chart7DaysRef = useRef<HTMLDivElement>(null);
    const chart14DaysRef = useRef<HTMLDivElement>(null);
    const chart30DaysRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (id) {
            fetchPatientData(parseInt(id));
        }
    }, [id]);

    const fetchPatientData = async (patientId: number) => {
        try {
            setLoading(true);
            const [patientRes, historyRes, statsRes, diariesRes, alertsRes] = await Promise.all([
                patientsAPI.getDetail(patientId),
                patientsAPI.getHistory(patientId),
                patientsAPI.getStatistics(patientId),
                diaryAPI.getPatientDiaries(patientId),
                patientsAPI.getAlerts(patientId),
            ]);

            if (patientRes.data.success) setPatient(patientRes.data.patient);
            if (historyRes.data.success) setHistory(historyRes.data.history);
            if (statsRes.data.success) setStatistics(statsRes.data.statistics);
            if (diariesRes.data.success) setDiaries(diariesRes.data.diaries);

            // Get latest high and low alerts
            if (alertsRes.data.success && alertsRes.data.alerts && alertsRes.data.alerts.length > 0) {
                // 找出最新的一筆警報日期
                const latestAlertDate = alertsRes.data.alerts[0].alert_date;
                
                // 只過濾出「同一天」的最新警報，避免拿好幾天前的接近警報和今天的穿線警報混搭
                const currentAlerts = alertsRes.data.alerts.filter((a: any) => a.alert_date === latestAlertDate);

                const highAlerts = currentAlerts.filter((a: any) => a.alert_type === 'high');
                if (highAlerts.length > 0) {
                    setLatestHighAlert(highAlerts[0]);
                }

                const lowAlerts = currentAlerts.filter((a: any) => a.alert_type === 'low');
                if (lowAlerts.length > 0) {
                    setLatestLowAlert(lowAlerts[0]);
                }
            }
        } catch (err: any) {
            console.error('Failed to fetch patient data:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleAddToWatchlist = async () => {
        if (!id) return;

        try {
            await watchlistAPI.add(parseInt(id));
            setIsInWatchlist(true);
            alert('已添加到特別關注');
        } catch (err: any) {
            alert(err.response?.data?.message || '添加失敗');
        }
    };

    const handleRemoveFromWatchlist = async () => {
        if (!id) return;

        try {
            await watchlistAPI.remove(parseInt(id));
            setIsInWatchlist(false);
            alert('已從特別關注移除');
        } catch (err: any) {
            alert(err.response?.data?.message || '移除失敗');
        }
    };

    if (loading) {
        return (
            <div className="patient-detail-loading">
                <div className="spinner"></div>
                <p>載入中...</p>
            </div>
        );
    }

    if (!patient) {
        return <div className="patient-detail-error">個案不存在</div>;
    }

    // 準備不同時間範圍的移動平均數據
    const prepareChartData = (days: number) => {
        if (!statistics?.trend) return [];

        const trendData = statistics.trend;

        // 計算移動平均
        const results: Array<{ date: string; 分數: number }> = [];

        trendData.forEach((item, index) => {
            const windowSize = days;

            // 只有當有足夠數據時才計算移動平均
            if (index >= windowSize - 1) {
                const window = trendData.slice(index - windowSize + 1, index + 1);
                const scores = window.map(d => d.score).filter((s): s is number => s !== null);

                // 只有當完整的N天都有數據時才顯示
                if (scores.length === windowSize) {
                    const avg = Number((scores.reduce((a, b) => a + b, 0) / windowSize).toFixed(2));
                    results.push({
                        date: new Date(item.date).toLocaleDateString('zh-TW', {
                            month: 'numeric',
                            day: 'numeric',
                        }),
                        分數: avg,
                    });
                }
            }
        });

        return results;
    };

    // 準備7日、14日、30日移動平均數據
    const chart7Days = prepareChartData(7);
    const chart14Days = prepareChartData(14);
    const chart30Days = prepareChartData(30);

    return (
        <div className="patient-detail-container">
            <div
                className="detail-header"
                style={{
                    display: 'flex',
                    flexDirection: 'row',
                    alignItems: 'center',
                    gap: '8px',
                    width: '100%',
                    justifyContent: 'space-between',
                }}
            >
                <button
                    onClick={() => navigate(-1)}
                    className="back-button"
                    style={{
                        flex: '1 1 50%',
                        minWidth: 0,
                        whiteSpace: 'nowrap',
                        fontSize: 'clamp(0.8rem, 2.5vw, 1rem)',
                        textAlign: 'center',
                    }}
                >
                    ← 返回
                </button>
                <div
                    className="header-actions"
                    style={{ flex: '1 1 50%', minWidth: 0 }}
                >
                    {isInWatchlist ? (
                        <button
                            onClick={handleRemoveFromWatchlist}
                            className="watchlist-button remove"
                            style={{
                                width: '100%',
                                whiteSpace: 'nowrap',
                                fontSize: 'clamp(0.8rem, 2.5vw, 1rem)',
                            }}
                        >
                            ★ 移除特別關注
                        </button>
                    ) : (
                        <button
                            onClick={handleAddToWatchlist}
                            className="watchlist-button add"
                            style={{
                                width: '100%',
                                whiteSpace: 'nowrap',
                                fontSize: 'clamp(0.8rem, 2.5vw, 1rem)',
                            }}
                        >
                            ☆ 添加特別關注
                        </button>
                    )}
                </div>
            </div>

            <div className="patient-info-card">
                <div className="patient-avatar-large">
                    {patient.name[0]}
                </div>
                <div className="patient-details">
                    <h2 className="patient-name-large">
                        {patient.name} {patient.nickname && <span className="patient-nickname-badge">({patient.nickname})</span>}
                    </h2>
                    <div className="patient-meta">
                        <span className="meta-item">📧 {patient.email}</span>
                    </div>
                </div>
            </div>

            {/* Tab Navigation */}
            <div className="tab-navigation">
                <button
                    onClick={() => setActiveTab('history')}
                    className={`tab-button ${activeTab === 'history' ? 'active' : ''}`}
                >
                    遊戲歷史記錄
                </button>
                <button
                    onClick={() => setActiveTab('profile')}
                    className={`tab-button ${activeTab === 'profile' ? 'active' : ''}`}
                >
                    個案基本資料
                </button>
                <button
                    onClick={() => setActiveTab('diary')}
                    className={`tab-button ${activeTab === 'diary' ? 'active' : ''}`}
                >
                    個案日記
                </button>
            </div>

            {activeTab === 'history' ? (
                <>
                    {/* 綜合圖表：當日/7日/14日/30日線 */}
                    {statistics?.trend && statistics.trend.length > 0 && (() => {
                        // 準備綜合多線圖表數據
                        const trendData = statistics.trend.map(item => ({
                            ...item,
                            當日分數: item.score
                        }));

                        // 計算移動平均
                        const multiLineTrendData = trendData.map((item, index) => {
                            const result: any = { ...item };

                            // 7日移動平均：必須從第7天開始，且前面必須有完整的7天數據
                            if (index >= 6) {
                                const last7 = trendData.slice(index - 6, index + 1);
                                const scores = last7.map(d => d.score).filter((s: number | null) => s !== null) as number[];
                                // 只有當完整的7天都有數據時才顯示7日線
                                if (scores.length === 7) {
                                    result['7日平均'] = Number((scores.reduce((a: number, b: number) => a + b, 0) / 7).toFixed(1));
                                }
                            }

                            // 14日移動平均：必須從第14天開始，且前面必須有完整的14天數據
                            if (index >= 13) {
                                const last14 = trendData.slice(index - 13, index + 1);
                                const scores = last14.map(d => d.score).filter((s: number | null) => s !== null) as number[];
                                // 只有當完整的14天都有數據時才顯示14日線
                                if (scores.length === 14) {
                                    result['14日平均'] = Number((scores.reduce((a: number, b: number) => a + b, 0) / 14).toFixed(1));
                                }
                            }

                            // 30日移動平均：必須從第30天開始，且前面必須有完整的30天數據
                            if (index >= 29) {
                                const last30 = trendData.slice(index - 29, index + 1);
                                const scores = last30.map(d => d.score).filter((s: number | null) => s !== null) as number[];
                                // 只有當完整的30天都有數據時才顯示30日線
                                if (scores.length === 30) {
                                    result['30日平均'] = Number((scores.reduce((a: number, b: number) => a + b, 0) / 30).toFixed(1));
                                }
                            }

                            return result;
                        });

                        return (
                            <div className="chart-section" ref={multiLineChartRef}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                                    <h3 className="section-title" style={{ margin: 0 }}>
                                        綜合分數趨勢
                                        {latestHighAlert && latestHighAlert.exceeded_lines && (() => {
                                            const lines = latestHighAlert.exceeded_lines;
                                            if (typeof lines === 'object' && Object.keys(lines).length > 0) {
                                                return (
                                                    <span style={{ color: '#dc2626', fontWeight: 'bold', marginLeft: '16px' }}>
                                                        穿越{Object.keys(lines).join('線、')}線
                                                    </span>
                                                );
                                            }
                                            return null;
                                        })()}
                                        {latestLowAlert && latestLowAlert.exceeded_lines && (() => {
                                            const lines = latestLowAlert.exceeded_lines;
                                            if (typeof lines === 'object' && Object.keys(lines).length > 0) {
                                                return (
                                                    <span style={{ color: '#2563eb', fontWeight: 'bold', marginLeft: '16px' }}>
                                                        接近{Object.keys(lines).join('線、')}線
                                                    </span>
                                                );
                                            }
                                            return null;
                                        })()}
                                    </h3>
                                    <div style={{ display: 'flex', gap: '8px' }}>
                                        <button
                                            onClick={() => downloadCSV(multiLineTrendData, '綜合分數趨勢')}
                                            style={{
                                                padding: '6px 12px',
                                                fontSize: '13px',
                                                backgroundColor: '#22c55e',
                                                color: 'white',
                                                border: 'none',
                                                borderRadius: '4px',
                                                cursor: 'pointer',
                                                fontWeight: '500'
                                            }}
                                            title="下載 CSV 數據"
                                        >
                                            📊 下載 CSV
                                        </button>
                                        <button
                                            onClick={() => multiLineChartRef.current && downloadChartAsPNG(multiLineChartRef.current, '綜合分數趨勢')}
                                            style={{
                                                padding: '6px 12px',
                                                fontSize: '13px',
                                                backgroundColor: '#3b82f6',
                                                color: 'white',
                                                border: 'none',
                                                borderRadius: '4px',
                                                cursor: 'pointer',
                                                fontWeight: '500'
                                            }}
                                            title="下載 PNG 圖片"
                                        >
                                            🖼️ 下載 PNG
                                        </button>
                                    </div>
                                </div>
                                <div style={{ width: '100%', overflowX: 'auto', overflowY: 'hidden' }}>
                                    <ResponsiveContainer
                                        width={multiLineTrendData.length > 30 ? multiLineTrendData.length * 30 : '100%'}
                                        height={400}
                                    >
                                        <LineChart data={multiLineTrendData}>
                                            <CartesianGrid strokeDasharray="3 3" />
                                            <XAxis dataKey="date" />
                                            <YAxis label={{ value: '分數', angle: -90, position: 'insideLeft' }} ticks={[12, 24, 45]} domain={[0, 56]} />
                                            <Tooltip content={<CustomMATooltip />} />
                                            <Legend formatter={(value) => String(value).includes('-') ? String(value).split('-')[1] : value} />
                                            <Line
                                                type="monotone"
                                                dataKey="當日分數"
                                                stroke="#f59e0b"
                                                strokeWidth={2}
                                                name="1-當日分數"
                                                dot={{ r: 3 }}
                                                connectNulls
                                            />
                                            <Line
                                                type="monotone"
                                                dataKey="7日平均"
                                                stroke="#667eea"
                                                strokeWidth={2.5}
                                                name="2-7日平均"
                                                dot={false}
                                                connectNulls
                                            />
                                            <Line
                                                type="monotone"
                                                dataKey="14日平均"
                                                stroke="#48bb78"
                                                strokeWidth={2.5}
                                                name="3-14日平均"
                                                dot={false}
                                                connectNulls
                                            />
                                            <Line
                                                type="monotone"
                                                dataKey="30日平均"
                                                stroke="#9f7aea"
                                                strokeWidth={2.5}
                                                name="4-30日平均"
                                                dot={false}
                                                connectNulls
                                            />
                                        </LineChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>
                        );
                    })()}

                    {/* 每日線圖 - 近30天 */}
                    <DailyScoreChart history={history} />

                    {/* 7日線 */}
                    {chart7Days.length > 0 && (
                        <div className="chart-section" ref={chart7DaysRef}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                                <h3 className="section-title" style={{ margin: 0 }}>近7天分數趨勢</h3>
                                <div style={{ display: 'flex', gap: '8px' }}>
                                    <button
                                        onClick={() => downloadCSV(chart7Days, '近7天分數趨勢')}
                                        style={{
                                            padding: '6px 12px',
                                            fontSize: '13px',
                                            backgroundColor: '#22c55e',
                                            color: 'white',
                                            border: 'none',
                                            borderRadius: '4px',
                                            cursor: 'pointer',
                                            fontWeight: '500'
                                        }}
                                        title="下載 CSV 數據"
                                    >
                                        📊 下載 CSV
                                    </button>
                                    <button
                                        onClick={() => chart7DaysRef.current && downloadChartAsPNG(chart7DaysRef.current, '近7天分數趨勢')}
                                        style={{
                                            padding: '6px 12px',
                                            fontSize: '13px',
                                            backgroundColor: '#3b82f6',
                                            color: 'white',
                                            border: 'none',
                                            borderRadius: '4px',
                                            cursor: 'pointer',
                                            fontWeight: '500'
                                        }}
                                        title="下載 PNG 圖片"
                                    >
                                        🖼️ 下載 PNG
                                    </button>
                                </div>
                            </div>
                            <div style={{ width: '100%', overflowX: 'auto', overflowY: 'hidden' }}>
                                <ResponsiveContainer
                                    width={chart7Days.length > 30 ? chart7Days.length * 30 : '100%'}
                                    height={250}
                                >
                                    <LineChart data={chart7Days}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="date" />
                                        <YAxis ticks={[12, 24, 45]} domain={[0, 56]} />
                                        <Tooltip />
                                        <Legend />
                                        <Line
                                            type="monotone"
                                            dataKey="分數"
                                            stroke="#667eea"
                                            strokeWidth={2}
                                        />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    )}

                    {/* 14日線 */}
                    {chart14Days.length > 0 && (
                        <div className="chart-section" ref={chart14DaysRef}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                                <h3 className="section-title" style={{ margin: 0 }}>近14天分數趨勢</h3>
                                <div style={{ display: 'flex', gap: '8px' }}>
                                    <button
                                        onClick={() => downloadCSV(chart14Days, '近14天分數趨勢')}
                                        style={{
                                            padding: '6px 12px',
                                            fontSize: '13px',
                                            backgroundColor: '#22c55e',
                                            color: 'white',
                                            border: 'none',
                                            borderRadius: '4px',
                                            cursor: 'pointer',
                                            fontWeight: '500'
                                        }}
                                        title="下載 CSV 數據"
                                    >
                                        📊 下載 CSV
                                    </button>
                                    <button
                                        onClick={() => chart14DaysRef.current && downloadChartAsPNG(chart14DaysRef.current, '近14天分數趨勢')}
                                        style={{
                                            padding: '6px 12px',
                                            fontSize: '13px',
                                            backgroundColor: '#3b82f6',
                                            color: 'white',
                                            border: 'none',
                                            borderRadius: '4px',
                                            cursor: 'pointer',
                                            fontWeight: '500'
                                        }}
                                        title="下載 PNG 圖片"
                                    >
                                        🖼️ 下載 PNG
                                    </button>
                                </div>
                            </div>
                            <div style={{ width: '100%', overflowX: 'auto', overflowY: 'hidden' }}>
                                <ResponsiveContainer
                                    width={chart14Days.length > 30 ? chart14Days.length * 30 : '100%'}
                                    height={250}
                                >
                                    <LineChart data={chart14Days}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="date" />
                                        <YAxis ticks={[12, 24, 45]} domain={[0, 56]} />
                                        <Tooltip />
                                        <Legend />
                                        <Line
                                            type="monotone"
                                            dataKey="分數"
                                            stroke="#48bb78"
                                            strokeWidth={2}
                                        />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    )}

                    {/* 30日線 */}
                    {chart30Days.length > 0 && (
                        <div className="chart-section" ref={chart30DaysRef}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                                <h3 className="section-title" style={{ margin: 0 }}>近30天分數趨勢</h3>
                                <div style={{ display: 'flex', gap: '8px' }}>
                                    <button
                                        onClick={() => downloadCSV(chart30Days, '近30天分數趨勢')}
                                        style={{
                                            padding: '6px 12px',
                                            fontSize: '13px',
                                            backgroundColor: '#22c55e',
                                            color: 'white',
                                            border: 'none',
                                            borderRadius: '4px',
                                            cursor: 'pointer',
                                            fontWeight: '500'
                                        }}
                                        title="下載 CSV 數據"
                                    >
                                        📊 下載 CSV
                                    </button>
                                    <button
                                        onClick={() => chart30DaysRef.current && downloadChartAsPNG(chart30DaysRef.current, '近30天分數趨勢')}
                                        style={{
                                            padding: '6px 12px',
                                            fontSize: '13px',
                                            backgroundColor: '#3b82f6',
                                            color: 'white',
                                            border: 'none',
                                            borderRadius: '4px',
                                            cursor: 'pointer',
                                            fontWeight: '500'
                                        }}
                                        title="下載 PNG 圖片"
                                    >
                                        🖼️ 下載 PNG
                                    </button>
                                </div>
                            </div>
                            <div style={{ width: '100%', overflowX: 'auto', overflowY: 'hidden' }}>
                                <ResponsiveContainer
                                    width={chart30Days.length > 30 ? chart30Days.length * 30 : '100%'}
                                    height={250}
                                >
                                    <LineChart data={chart30Days}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="date" />
                                        <YAxis ticks={[12, 24, 45]} domain={[0, 56]} />
                                        <Tooltip />
                                        <Legend />
                                        <Line
                                            type="monotone"
                                            dataKey="分數"
                                            stroke="#9f7aea"
                                            strokeWidth={2}
                                        />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    )}

                    <div className="history-section">
                        <h3 className="section-title">評估歷史記錄</h3>
                        {history.length === 0 ? (
                            <p className="no-data">尚無評估記錄</p>
                        ) : (
                            <div className="history-table-container">
                                <table className="history-table">
                                    <thead>
                                        <tr>
                                            <th>日期時間</th>
                                            <th>分數</th>
                                            <th>等級</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {history.map((assessment) => (
                                            <tr key={assessment.id}>
                                                <td>{new Date(assessment.completed_at).toLocaleString('zh-TW')}</td>
                                                <td>
                                                    {assessment.total_score}/{assessment.max_score}
                                                </td>
                                                <td>
                                                    <span className={`level-badge ${getLevelClass(assessment.level)}`}>
                                                        {assessment.level}
                                                    </span>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                </>
            ) : activeTab === 'profile' ? (
                /* Patient Profile Tab */
                <div className="profile-section">
                    <h3 className="section-title">個案基本資料</h3>
                    <div className="profile-grid">
                        <div className="profile-item">
                            <span className="profile-label">身份</span>
                            <span className="profile-value">
                                {patient.group === 'student' ? '學校' : patient.group === 'clinical' ? '醫院' : '未分類'}
                            </span>
                        </div>
                        <div className="profile-item">
                            <span className="profile-label">姓名</span>
                            <span className="profile-value">{patient.name}</span>
                        </div>
                        <div className="profile-item">
                            <span className="profile-label">暱稱</span>
                            <span className="profile-value">{patient.nickname || '未設定'}</span>
                        </div>
                        <div className="profile-item">
                            <span className="profile-label">電子郵件</span>
                            <span className="profile-value">{patient.email}</span>
                        </div>
                        <div className="profile-item">
                            <span className="profile-label">出生日期</span>
                            <span className="profile-value">
                                {patient.dob
                                    ? new Date(patient.dob).toLocaleDateString('zh-TW')
                                    : '未提供'}
                            </span>
                        </div>
                        <div className="profile-item">
                            <span className="profile-label">性別</span>
                            <span className="profile-value">{patient.gender || '未提供'}</span>
                        </div>
                        <div className="profile-item">
                            <span className="profile-label">身高</span>
                            <span className="profile-value">
                                {patient.height ? `${patient.height} cm` : '未提供'}
                            </span>
                        </div>
                        <div className="profile-item">
                            <span className="profile-label">體重</span>
                            <span className="profile-value">
                                {patient.weight ? `${patient.weight} kg` : '未提供'}
                            </span>
                        </div>
                        <div className="profile-item">
                            <span className="profile-label">教育程度</span>
                            <span className="profile-value">{patient.education || '未提供'}</span>
                        </div>
                        <div className="profile-item">
                            <span className="profile-label">婚姻狀況</span>
                            <span className="profile-value">{patient.marital_status || '未提供'}</span>
                        </div>
                        <div className="profile-item">
                            <span className="profile-label">是否有子女</span>
                            <span className="profile-value">
                                {patient.has_children !== null && patient.has_children !== undefined
                                    ? patient.has_children
                                        ? '是'
                                        : '否'
                                    : '未提供'}
                            </span>
                        </div>
                        <div className="profile-item">
                            <span className="profile-label">經濟狀況</span>
                            <span className="profile-value">{patient.economic_status || '未提供'}</span>
                        </div>
                        <div className="profile-item">
                            <span className="profile-label">居住城市</span>
                            <span className="profile-value">
                                {patient.location_city && patient.location_district
                                    ? `${patient.location_city} ${patient.location_district}`
                                    : patient.location_city || '未提供'}
                            </span>
                        </div>
                        <div className="profile-item">
                            <span className="profile-label">居住狀況</span>
                            <span className="profile-value">{patient.living_situation || '未提供'}</span>
                        </div>
                        <div className="profile-item">
                            <span className="profile-label">是否有工作</span>
                            <span className="profile-value">
                                {patient.has_job !== null && patient.has_job !== undefined
                                    ? patient.has_job
                                        ? '是'
                                        : '否'
                                    : '未提供'}
                            </span>
                        </div>
                        <div className="profile-item">
                            <span className="profile-label">薪資範圍</span>
                            <span className="profile-value">{patient.salary_range || '未提供'}</span>
                        </div>
                        <div className="profile-item">
                            <span className="profile-label">註冊日期</span>
                            <span className="profile-value">
                                {new Date(patient.created_at).toLocaleDateString('zh-TW')}
                            </span>
                        </div>
                    </div>
                </div>
            ) : activeTab === 'diary' ? (
                /* Patient Diary Tab */
                <div className="diary-section">
                    <h3 className="section-title">個案日記 (只讀)</h3>
                    {diaries.length === 0 ? (
                        <p className="no-data">個案尚未撰寫日記</p>
                    ) : (
                        <div className="diaries-container">
                            {diaries.map((diary) => (
                                <div key={diary.id} className="diary-card" onClick={() => setSelectedDiary(diary)}>
                                    <div className="diary-header">
                                        <span className="diary-date">
                                            📅 {new Date(diary.date).toLocaleDateString('zh-TW')}
                                        </span>
                                        {diary.period_marker && (
                                            <span className="period-marker">🩸 生理期</span>
                                        )}
                                    </div>
                                    {diary.mood && (
                                        <div className="diary-mood">
                                            心情: {getMoodEmoji(diary.mood)} {getMoodLabel(diary.mood)}
                                        </div>
                                    )}
                                    {diary.content && (
                                        <div className="diary-content-preview">
                                            <p>{diary.content.length > 100 ? diary.content.substring(0, 100) + '...' : diary.content}</p>
                                        </div>
                                    )}
                                    {diary.images && diary.images.length > 0 && (
                                        <div className="diary-images-preview">
                                            {diary.images.slice(0, 3).map((img, idx) => {
                                                const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
                                                const imgUrl = img.startsWith('http://') || img.startsWith('https://')
                                                    ? img
                                                    : `${API_BASE_URL}${img}`;
                                                return (
                                                    <img key={idx} src={imgUrl} alt="預覽" className="diary-image-thumb" />
                                                );
                                            })}
                                            {diary.images.length > 3 && (
                                                <div className="diary-more-images">+{diary.images.length - 3}</div>
                                            )}
                                        </div>
                                    )}
                                    <div className="diary-footer">
                                        <span className="diary-timestamp">
                                            建立於 {new Date(diary.created_at).toLocaleString('zh-TW')}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Diary Detail Modal */}
                    {selectedDiary && (
                        <div className="modal-overlay" onClick={() => setSelectedDiary(null)}>
                            <div className="modal-content diary-modal" onClick={(e) => e.stopPropagation()}>
                                <button className="modal-close" onClick={() => setSelectedDiary(null)}>✕</button>

                                <div className="diary-modal-header">
                                    <h2 className="modal-title">日記詳情</h2>
                                    <span className="diary-modal-date">
                                        📅 {new Date(selectedDiary.date).toLocaleDateString('zh-TW')}
                                    </span>
                                </div>

                                <div className="diary-modal-body">
                                    <div className="diary-modal-meta">
                                        {selectedDiary.mood && (
                                            <div className="diary-detail-mood">
                                                <span className="detail-label">今日心情：</span>
                                                <span className="detail-value">
                                                    {getMoodEmoji(selectedDiary.mood)} {getMoodLabel(selectedDiary.mood)}
                                                </span>
                                            </div>
                                        )}
                                        {selectedDiary.period_marker && (
                                            <div className="diary-detail-tag">
                                                <span className="period-marker">🩸 生理期標記</span>
                                            </div>
                                        )}
                                    </div>

                                    {selectedDiary.content && (
                                        <div className="diary-detail-content">
                                            <h4 className="detail-subtitle">紀錄內容：</h4>
                                            <div className="content-text">
                                                {selectedDiary.content}
                                            </div>
                                        </div>
                                    )}

                                    {selectedDiary.images && selectedDiary.images.length > 0 && (
                                        <div className="diary-detail-images">
                                            <h4 className="detail-subtitle">照片紀錄：</h4>
                                            <div className="detail-images-grid">
                                                {selectedDiary.images.map((img, idx) => {
                                                    const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
                                                    const imgUrl = img.startsWith('http://') || img.startsWith('https://')
                                                        ? img
                                                        : `${API_BASE_URL}${img}`;
                                                    return (
                                                        <a key={idx} href={imgUrl} target="_blank" rel="noopener noreferrer">
                                                            <img src={imgUrl} alt={`附件 ${idx + 1}`} className="diary-full-image" />
                                                        </a>
                                                    );
                                                })}
                                            </div>
                                        </div>
                                    )}
                                </div>

                                <div className="diary-modal-footer">
                                    <span className="diary-timestamp">
                                        系統建立時間：{new Date(selectedDiary.created_at).toLocaleString('zh-TW')}
                                    </span>
                                    <button className="confirm-button" onClick={() => setSelectedDiary(null)}>關閉</button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            ) : null}
        </div>
    );
}

function getLevelClass(level: string): string {
    if (level === '良好') return 'level-good';
    if (level === '需要關注') return 'level-attention';
    return '';
}

function getMoodEmoji(mood: string): string {
    const moodMap: Record<string, string> = {
        'very_happy': '😊',
        'happy': '🙂',
        'neutral': '😐',
        'sad': '😔',
        'very_sad': '😢',
        'angry': '😠',
        'anxious': '😰',
        'tired': '😴',
    };
    return moodMap[mood] || '😐';
}

function getMoodLabel(mood: string): string {
    const labelMap: Record<string, string> = {
        'very_happy': '非常開心',
        'happy': '開心',
        'neutral': '平靜',
        'sad': '難過',
        'very_sad': '非常難過',
        'angry': '生氣',
        'anxious': '焦慮',
        'tired': '疲倦',
    };
    return labelMap[mood] || mood;
}

