import React, { useMemo } from 'react';
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

interface DailyScoreChartProps {
    history: any[]; // Using any for flexibility with admin assessment history type
}

export const DailyScoreChart: React.FC<DailyScoreChartProps> = ({ history }) => {
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

    return (
        <div className="chart-section">
            <h3 className="section-title">
                近30天每日平均分數
            </h3>
            {daysWithData > 0 ? (
                <>
                    <ResponsiveContainer width="100%" height={300}>
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

