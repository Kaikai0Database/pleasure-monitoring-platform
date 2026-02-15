import React, { useMemo, useRef } from 'react';
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
import { downloadCSV, downloadChartAsPNG } from '../utils/chartDownloadUtils';

interface DailyScoreChartProps {
    history: any[]; // Using any for flexibility with admin assessment history type
}

export const DailyScoreChart: React.FC<DailyScoreChartProps> = ({ history }) => {
    const chartRef = useRef<HTMLDivElement>(null);

    // 準備每日圖表數據（近30天）
    const dailyChartData = useMemo(() => {
        const today = new Date();
        const thirtyDaysAgo = new Date(today);
        thirtyDaysAgo.setDate(today.getDate() - 29); // 包含今天共30天
        thirtyDaysAgo.setHours(0, 0, 0, 0);

        // 過濾出近30天的記錄
        const recentRecords = history.filter(record => {
            if (!record || !record.completed_at) return false;
            const dateObj = new Date(record.completed_at);
            if (isNaN(dateObj.getTime())) return false;
            return dateObj >= thirtyDaysAgo;
        });

        // 按日期分組並計算每日平均分
        const dailyScores: { [date: string]: number[] } = {};

        recentRecords.forEach(record => {
            const dateObj = new Date(record.completed_at);
            const dateKey = dateObj.toLocaleDateString('zh-TW', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit'
            });

            if (!dailyScores[dateKey]) {
                dailyScores[dateKey] = [];
            }
            dailyScores[dateKey].push(record.total_score);
        });

        // 生成近30天的數據，包括沒有記錄的日期
        const chartData = [];
        for (let i = 29; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(today.getDate() - i);
            date.setHours(0, 0, 0, 0);

            const dateKey = date.toLocaleDateString('zh-TW', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit'
            });

            const scores = dailyScores[dateKey];

            // 計算當天的平均分數
            const avgScore = scores && scores.length > 0
                ? scores.reduce((sum, score) => sum + score, 0) / scores.length
                : null;

            chartData.push({
                日期: `${date.getMonth() + 1}/${date.getDate()}`,
                分數: avgScore !== null ? parseFloat(avgScore.toFixed(1)) : null,
                完整日期: dateKey
            });
        }

        return chartData;
    }, [history]);

    // 計算有數據的天數
    const daysWithData = dailyChartData.filter(d => d.分數 !== null).length;

    const handleDownloadCSV = () => {
        downloadCSV(dailyChartData, '近30天每日平均分數');
    };

    const handleDownloadPNG = async () => {
        if (chartRef.current) {
            await downloadChartAsPNG(chartRef.current, '近30天每日平均分數');
        }
    };

    return (
        <div className="chart-section" ref={chartRef}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <h3 className="section-title" style={{ margin: 0 }}>
                    近30天每日平均分數
                </h3>
                {daysWithData > 0 && (
                    <div style={{ display: 'flex', gap: '8px' }}>
                        <button
                            onClick={handleDownloadCSV}
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
                            onClick={handleDownloadPNG}
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
                )}
            </div>
            {daysWithData > 0 ? (
                <>
                    <div style={{ width: '100%', overflowX: 'auto', overflowY: 'hidden' }}>
                        <ResponsiveContainer
                            width={dailyChartData.length > 30 ? dailyChartData.length * 30 : '100%'}
                            height={300}
                        >
                            <LineChart data={dailyChartData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis
                                    dataKey="日期"
                                    label={{ value: '日期', position: 'insideBottom', offset: -5 }}
                                    angle={-45}
                                    textAnchor="end"
                                    height={80}
                                />
                                <YAxis
                                    label={{ value: '分數', angle: -90, position: 'insideLeft' }}
                                    ticks={[12, 24, 45]}
                                    domain={[0, 56]}
                                />
                                <Tooltip
                                    formatter={(value: any) => value !== null ? value : '無數據'}
                                    labelFormatter={(label) => {
                                        const dataPoint = dailyChartData.find(d => d.日期 === label);
                                        return dataPoint ? dataPoint.完整日期 : label;
                                    }}
                                />
                                <Legend />
                                <Line
                                    type="monotone"
                                    dataKey="分數"
                                    stroke="#f59e0b"
                                    strokeWidth={3}
                                    name="每日平均分數"
                                    dot={{ fill: '#f59e0b', r: 4 }}
                                    connectNulls={true}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="text-center text-sm text-gray-600 mt-2">
                        近30天內有 {daysWithData} 天有評估記錄
                    </div>
                </>
            ) : (
                <div className="text-center py-12 text-gray-400">
                    <div className="text-4xl mb-2">📊</div>
                    <p>近30天內尚無評估記錄</p>
                    <p className="text-xs mt-2">患者完成評估後，此處將顯示近30天的每日平均分數趨勢</p>
                </div>
            )}
        </div>
    );
};

