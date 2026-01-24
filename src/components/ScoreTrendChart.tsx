import React, { useMemo, useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { PixelCard } from './ui/PixelCard';
import { alertsApi } from '../services/api';
import type { AssessmentHistory, ScoreAlert } from '../types/api';

interface ScoreTrendChartProps {
    history: AssessmentHistory[];
}

export const ScoreTrendChart: React.FC<ScoreTrendChartProps> = ({ history }) => {
    const [viewMode, setViewMode] = useState<'daily' | 7 | 14 | 30 | 'all'>('all');
    const [latestHighAlert, setLatestHighAlert] = useState<ScoreAlert | null>(null);
    const [latestLowAlert, setLatestLowAlert] = useState<ScoreAlert | null>(null);

    // Fetch latest high and low alerts
    useEffect(() => {
        const fetchLatestAlerts = async () => {
            try {
                const response = await alertsApi.getAlerts();
                if (response.success && response.alerts && response.alerts.length > 0) {
                    // Get latest high alert
                    const highAlerts = response.alerts.filter(a => a.alert_type === 'high');
                    if (highAlerts.length > 0) {
                        setLatestHighAlert(highAlerts[0]);
                    }

                    // Get latest low alert
                    const lowAlerts = response.alerts.filter(a => a.alert_type === 'low');
                    if (lowAlerts.length > 0) {
                        setLatestLowAlert(lowAlerts[0]);
                    }
                }
            } catch (error) {
                console.error('Failed to fetch alerts:', error);
            }
        };
        fetchLatestAlerts();
    }, []);

    // Helper to format crossed/approached lines text
    const getAlertText = (alert: ScoreAlert) => {
        if (!alert.exceeded_lines) return '';
        try {
            const lines = typeof alert.exceeded_lines === 'string'
                ? JSON.parse(alert.exceeded_lines)
                : alert.exceeded_lines;
            const lineNames = Object.keys(lines);
            if (lineNames.length === 0) return '';

            const action = alert.alert_type === 'high' ? '穿越' : '接近';
            return `${action}${lineNames.join('線、')}線`;
        } catch (e) {
            return '';
        }
    };

    // 準備圖表數據：按日期分組並計算每日平均
    const prepareChartData = (days: number) => {
        const now = new Date();
        const rangeDate = new Date();
        rangeDate.setDate(now.getDate() - days);

        // 按日期分組
        const groupedByDate: { [key: string]: { total: number; count: number } } = {};

        history.forEach(record => {
            if (!record || !record.completed_at) return;
            const dateObj = new Date(record.completed_at);
            if (isNaN(dateObj.getTime())) return;
            if (dateObj < rangeDate) return;

            const dateKey = dateObj.toLocaleDateString('zh-TW', {
                month: 'numeric',
                day: 'numeric',
            });

            if (!groupedByDate[dateKey]) {
                groupedByDate[dateKey] = { total: 0, count: 0 };
            }

            groupedByDate[dateKey].total += record.total_score;
            groupedByDate[dateKey].count += 1;
        });

        // 計算每日平均並轉換為圖表數據，按實際日期排序
        const sortedDates = Object.keys(groupedByDate).sort((a, b) => {
            // 從實際記錄中找到對應的日期
            const recordA = history.find(r => {
                if (!r.completed_at) return false;
                const d = new Date(r.completed_at);
                if (d < rangeDate) return false;
                const key = d.toLocaleDateString('zh-TW', { month: 'numeric', day: 'numeric' });
                return key === a;
            });
            const recordB = history.find(r => {
                if (!r.completed_at) return false;
                const d = new Date(r.completed_at);
                if (d < rangeDate) return false;
                const key = d.toLocaleDateString('zh-TW', { month: 'numeric', day: 'numeric' });
                return key === b;
            });
            if (!recordA || !recordB) return 0;
            return new Date(recordA.completed_at).getTime() - new Date(recordB.completed_at).getTime();
        });

        return sortedDates.map(dateKey => ({
            date: dateKey,
            分數: Number((groupedByDate[dateKey].total / groupedByDate[dateKey].count).toFixed(1)),
        }));
    };

    // 準備不同時間範圍的數據
    const chart7Days = useMemo(() => prepareChartData(7), [history]);
    const chart14Days = useMemo(() => prepareChartData(14), [history]);
    const chart30Days = useMemo(() => prepareChartData(30), [history]);

    // 準備綜合圖表數據 - 合併4條線的數據
    const combinedChartData = useMemo(() => {
        // 收集所有歷史數據（不限制天數）
        const dateMap = new Map();

        // 收集所有日期的數據
        history.forEach(record => {
            if (!record || !record.completed_at) return;
            const dateObj = new Date(record.completed_at);
            if (isNaN(dateObj.getTime())) return;

            const dateKey = dateObj.toLocaleDateString('zh-TW', {
                month: 'numeric',
                day: 'numeric',
            });

            if (!dateMap.has(dateKey)) {
                dateMap.set(dateKey, []);
            }
            dateMap.get(dateKey).push(record.total_score);
        });

        // 轉換為圖表數據格式並按實際日期排序
        const dates = Array.from(dateMap.keys()).sort((a, b) => {
            // 從 history 中獲取對應日期的實際完整日期進行排序
            const recordA = history.find(r => {
                if (!r.completed_at) return false;
                const d = new Date(r.completed_at);
                const key = d.toLocaleDateString('zh-TW', { month: 'numeric', day: 'numeric' });
                return key === a;
            });
            const recordB = history.find(r => {
                if (!r.completed_at) return false;
                const d = new Date(r.completed_at);
                const key = d.toLocaleDateString('zh-TW', { month: 'numeric', day: 'numeric' });
                return key === b;
            });
            if (!recordA || !recordB) return 0;
            return new Date(recordA.completed_at).getTime() - new Date(recordB.completed_at).getTime();
        });

        return dates.map(date => {
            const scores = dateMap.get(date) || [];
            const avgScore = scores.length > 0
                ? Number((scores.reduce((a: number, b: number) => a + b, 0) / scores.length).toFixed(1))
                : null;

            return {
                date,
                當日平均: avgScore,
            };
        });
    }, [history]);

    // 為綜合圖表添加不同時間範圍的移動平均線
    const multiLineChartData = useMemo(() => {
        if (combinedChartData.length === 0) return [];

        // 計算7日、14日、30日移動平均
        return combinedChartData.map((item, index) => {
            const result: any = { ...item };

            // 7日移動平均：必須從第7天開始，且前面必須有完整的7天數據
            if (index >= 6) {
                const last7 = combinedChartData.slice(index - 6, index + 1);
                const scores = last7.map(d => d.當日平均).filter(s => s !== null) as number[];
                // 只有當完整的7天都有數據時才顯示7日線
                if (scores.length === 7) {
                    result['7日平均'] = Number((scores.reduce((a, b) => a + b, 0) / 7).toFixed(1));
                }
            }

            // 14日移動平均：必須從第14天開始，且前面必須有完整的14天數據
            if (index >= 13) {
                const last14 = combinedChartData.slice(index - 13, index + 1);
                const scores = last14.map(d => d.當日平均).filter(s => s !== null) as number[];
                // 只有當完整的14天都有數據時才顯示14日線
                if (scores.length === 14) {
                    result['14日平均'] = Number((scores.reduce((a, b) => a + b, 0) / 14).toFixed(1));
                }
            }

            // 30日移動平均：必須從第30天開始，且前面必須有完整的30天數據
            if (index >= 29) {
                const last30 = combinedChartData.slice(index - 29, index + 1);
                const scores = last30.map(d => d.當日平均).filter(s => s !== null) as number[];
                // 只有當完整的30天都有數據時才顯示30日線
                if (scores.length === 30) {
                    result['30日平均'] = Number((scores.reduce((a, b) => a + b, 0) / 30).toFixed(1));
                }
            }

            return result;
        });
    }, [combinedChartData]);

    return (
        <PixelCard className="bg-white p-6">
            <div className="flex flex-col items-center mb-6">
                <div className="flex items-center gap-4 mb-4 flex-wrap justify-center">
                    <h3 className="text-xl font-bold">
                        {viewMode === 'all' ? '綜合分數趨勢（當日/7日/14日/30日）' : viewMode === 'daily' ? '每日平均分數' : `近 ${viewMode} 日分數走勢`}
                    </h3>
                    {latestHighAlert && (
                        <span className="text-lg font-bold text-red-600">
                            {getAlertText(latestHighAlert)}
                        </span>
                    )}
                    {latestLowAlert && (
                        <span className="text-lg font-bold text-blue-600">
                            {getAlertText(latestLowAlert)}
                        </span>
                    )}
                </div>
                <div className="flex gap-2 text-sm">
                    <button
                        onClick={() => setViewMode('all')}
                        className={`px-3 py-1 rounded border border-black ${viewMode === 'all' ? 'bg-black text-white' : 'bg-white hover:bg-gray-100'}`}
                    >
                        綜合
                    </button>
                    <button
                        onClick={() => setViewMode('daily')}
                        className={`px-3 py-1 rounded border border-black ${viewMode === 'daily' ? 'bg-black text-white' : 'bg-white hover:bg-gray-100'}`}
                    >
                        每日
                    </button>
                    <button
                        onClick={() => setViewMode(7)}
                        className={`px-3 py-1 rounded border border-black ${viewMode === 7 ? 'bg-black text-white' : 'bg-white hover:bg-gray-100'}`}
                    >
                        7日
                    </button>
                    <button
                        onClick={() => setViewMode(14)}
                        className={`px-3 py-1 rounded border border-black ${viewMode === 14 ? 'bg-black text-white' : 'bg-white hover:bg-gray-100'}`}
                    >
                        14日
                    </button>
                    <button
                        onClick={() => setViewMode(30)}
                        className={`px-3 py-1 rounded border border-black ${viewMode === 30 ? 'bg-black text-white' : 'bg-white hover:bg-gray-100'}`}
                    >
                        30日
                    </button>
                </div>
            </div>

            {/* 綜合圖表 - 4條線 */}
            {viewMode === 'all' && multiLineChartData.length > 0 && (
                <div className="mb-6">
                    <ResponsiveContainer width="100%" height={400}>
                        <LineChart data={multiLineChartData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="date" />
                            <YAxis
                                label={{ value: '分數', angle: -90, position: 'insideLeft' }}
                                ticks={[12, 24, 45]}
                                domain={[0, 56]}
                            />
                            <Tooltip formatter={(value, name) => [value, String(name).includes('-') ? String(name).split('-')[1] : name]} />
                            <Legend formatter={(value) => String(value).includes('-') ? String(value).split('-')[1] : value} />
                            <Line
                                type="monotone"
                                dataKey="當日平均"
                                stroke="#f59e0b"
                                strokeWidth={2}
                                name="1-當日平均"
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
            )}

            {/* 每日線 - 單獨顯示 */}
            {viewMode === 'daily' && combinedChartData.length > 0 && (
                <div className="mb-6">
                    <ResponsiveContainer width="100%" height={400}>
                        <LineChart data={combinedChartData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="date" />
                            <YAxis
                                label={{ value: '分數', angle: -90, position: 'insideLeft' }}
                                ticks={[12, 24, 45]}
                                domain={[0, 56]}
                            />
                            <Tooltip />
                            <Legend />
                            <Line
                                type="monotone"
                                dataKey="當日平均"
                                stroke="#f59e0b"
                                strokeWidth={3}
                                name="當日平均"
                                dot={{ fill: '#f59e0b', r: 4 }}
                                connectNulls
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            )}

            {/* 7日線 */}
            {viewMode === 7 && chart7Days.length > 0 && (
                <div>
                    <ResponsiveContainer width="100%" height={300}>
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
            )}

            {/* 14日線 */}
            {viewMode === 14 && chart14Days.length > 0 && (
                <div>
                    <ResponsiveContainer width="100%" height={300}>
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
            )}

            {/* 30日線 */}
            {viewMode === 30 && chart30Days.length > 0 && (
                <div>
                    <ResponsiveContainer width="100%" height={300}>
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
            )}

            {/* 無數據提示 */}
            {((viewMode === 'all' && combinedChartData.length === 0) ||
                (viewMode === 'daily' && combinedChartData.length === 0) ||
                (viewMode === 7 && chart7Days.length === 0) ||
                (viewMode === 14 && chart14Days.length === 0) ||
                (viewMode === 30 && chart30Days.length === 0)) && (
                    <div className="text-center py-12 text-gray-400">
                        暫無資料
                    </div>
                )}
        </PixelCard>
    );
};
