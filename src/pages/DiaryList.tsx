import React, { useState, useEffect } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { DiaryCard } from '../components/DiaryCard';
import { diaryService } from '../services/diaryService';
import type { Diary } from '../types/diary';

export const DiaryList: React.FC = () => {
    const { user } = useAuth();
    const navigate = useNavigate();

    const [diaries, setDiaries] = useState<Diary[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // 篩選狀態
    const currentDate = new Date();
    const [selectedYear, setSelectedYear] = useState(currentDate.getFullYear());
    const [selectedMonth, setSelectedMonth] = useState<number | null>(null);

    useEffect(() => {
        loadDiaries();
    }, [selectedYear, selectedMonth]);

    const loadDiaries = async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await diaryService.getAllDiaries(
                selectedYear,
                selectedMonth || undefined
            );
            setDiaries(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : '載入日記失敗');
        } finally {
            setLoading(false);
        }
    };

    // 按月份分組
    const groupedDiaries = diaries.reduce((groups, diary) => {
        const date = new Date(diary.date);
        const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
        if (!groups[monthKey]) {
            groups[monthKey] = [];
        }
        groups[monthKey].push(diary);
        return groups;
    }, {} as Record<string, Diary[]>);

    // 生成年份選項
    const years = Array.from({ length: 10 }, (_, i) => currentDate.getFullYear() - i);
    const months = Array.from({ length: 12 }, (_, i) => i + 1);

    if (!user) {
        return <Navigate to="/login" replace />;
    }

    return (
        <div className="min-h-[calc(100vh-100px)] py-8">
            <div className="max-w-6xl mx-auto">
                {/* 標題與新增按鈕 */}
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-4xl font-bold mb-2">我的日記</h1>
                        <p className="text-lg opacity-80">回顧過去的心情與故事</p>
                    </div>
                    <button
                        onClick={() => navigate('/diary/new')}
                        className="px-6 py-3 bg-yellow-400 border-4 border-yellow-600 rounded-lg font-bold text-lg hover:bg-yellow-500 transition-colors"
                    >
                        ✏️ 寫日記
                    </button>
                </div>

                {/* 篩選器 */}
                <div className="mb-6 p-4 bg-white border-4 border-gray-300 rounded-lg">
                    <div className="flex gap-4 items-center">
                        <span className="font-bold">篩選：</span>

                        <select
                            value={selectedYear}
                            onChange={(e) => setSelectedYear(Number(e.target.value))}
                            className="px-4 py-2 border-4 border-gray-300 rounded-lg font-medium focus:border-yellow-500 focus:outline-none"
                        >
                            {years.map((year) => (
                                <option key={year} value={year}>
                                    {year} 年
                                </option>
                            ))}
                        </select>

                        <select
                            value={selectedMonth || ''}
                            onChange={(e) => setSelectedMonth(e.target.value ? Number(e.target.value) : null)}
                            className="px-4 py-2 border-4 border-gray-300 rounded-lg font-medium focus:border-yellow-500 focus:outline-none"
                        >
                            <option value="">全部月份</option>
                            {months.map((month) => (
                                <option key={month} value={month}>
                                    {month} 月
                                </option>
                            ))}
                        </select>

                        {selectedMonth && (
                            <button
                                onClick={() => setSelectedMonth(null)}
                                className="text-sm text-gray-600 hover:text-gray-800 underline"
                            >
                                清除篩選
                            </button>
                        )}
                    </div>
                </div>

                {/* 載入中 */}
                {loading && (
                    <div className="text-center py-12">
                        <div className="text-4xl mb-4">📖</div>
                        <div className="text-lg text-gray-600">載入中...</div>
                    </div>
                )}

                {/* 錯誤訊息 */}
                {error && (
                    <div className="p-4 bg-red-100 border-4 border-red-400 rounded-lg text-red-700 font-medium">
                        ❌ {error}
                    </div>
                )}

                {/* 日記列表 */}
                {!loading && !error && (
                    <>
                        {diaries.length === 0 ? (
                            <div className="text-center py-12 bg-gray-50 border-4 border-gray-300 rounded-lg">
                                <div className="text-6xl mb-4">📝</div>
                                <div className="text-xl font-bold mb-2">還沒有日記</div>
                                <div className="text-gray-600 mb-4">開始記錄你的心情吧！</div>
                                <button
                                    onClick={() => navigate('/diary/new')}
                                    className="px-6 py-3 bg-yellow-400 border-4 border-yellow-600 rounded-lg font-bold hover:bg-yellow-500 transition-colors"
                                >
                                    寫下第一篇日記
                                </button>
                            </div>
                        ) : (
                            <div className="space-y-8">
                                {Object.entries(groupedDiaries)
                                    .sort(([a], [b]) => b.localeCompare(a))
                                    .map(([monthKey, monthDiaries]) => {
                                        const [year, month] = monthKey.split('-');
                                        return (
                                            <div key={monthKey}>
                                                <h2 className="text-2xl font-bold mb-4 pb-2 border-b-4 border-gray-300">
                                                    {year} 年 {parseInt(month)} 月
                                                </h2>
                                                <div className="space-y-4">
                                                    {monthDiaries.map((diary) => (
                                                        <DiaryCard
                                                            key={diary.id}
                                                            diary={diary}
                                                            onClick={() => navigate(`/diary/edit/${diary.id}`)}
                                                        />
                                                    ))}
                                                </div>
                                            </div>
                                        );
                                    })}
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
};
