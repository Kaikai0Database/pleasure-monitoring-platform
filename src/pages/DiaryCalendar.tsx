import React, { useState, useEffect } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { diaryService } from '../services/diaryService';
import type { Diary } from '../types/diary';
import { getMoodIcon, getMoodName, PERIOD_MARKER } from '../types/diary';
import { DiarySelectionModal } from '../components/DiarySelectionModal';

export const DiaryCalendar: React.FC = () => {
    const { user } = useAuth();
    const navigate = useNavigate();

    const [currentYear, setCurrentYear] = useState(new Date().getFullYear());
    const [currentMonth, setCurrentMonth] = useState(new Date().getMonth() + 1);
    const [diaries, setDiaries] = useState<Diary[]>([]);

    // 輪播狀態：記錄每個日期當前顯示的日記索引
    const [rotatingIndexes, setRotatingIndexes] = useState<Map<number, number>>(new Map());

    // 選擇彈窗狀態
    const [selectedDateDiaries, setSelectedDateDiaries] = useState<Diary[] | null>(null);

    useEffect(() => {
        loadDiaries();
    }, [currentYear, currentMonth]);

    const loadDiaries = async () => {
        try {
            const data = await diaryService.getAllDiaries(currentYear, currentMonth);
            setDiaries(data);
        } catch (err) {
            console.error('載入日記失敗:', err);
        }
    };

    // 生成日曆格子
    const generateCalendar = () => {
        const firstDay = new Date(currentYear, currentMonth - 1, 1);
        const lastDay = new Date(currentYear, currentMonth, 0);
        const daysInMonth = lastDay.getDate();
        const startingDayOfWeek = firstDay.getDay(); // 0 = 週日

        const calendar: (number | null)[][] = [];
        let currentWeek: (number | null)[] = [];

        // 填充第一週的空白
        for (let i = 0; i < startingDayOfWeek; i++) {
            currentWeek.push(null);
        }

        // 填充日期
        for (let day = 1; day <= daysInMonth; day++) {
            currentWeek.push(day);
            if (currentWeek.length === 7) {
                calendar.push(currentWeek);
                currentWeek = [];
            }
        }

        // 填充最後一週的空白
        if (currentWeek.length > 0) {
            while (currentWeek.length < 7) {
                currentWeek.push(null);
            }
            calendar.push(currentWeek);
        }

        return calendar;
    };

    // 獲取特定日期的所有日記（支援多筆）
    const getDiariesForDate = (day: number): Diary[] => {
        const dateStr = `${currentYear}-${String(currentMonth).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        return diaries.filter(d => d.date === dateStr);
    };

    // 自動輪播：每 2 秒切換一次
    useEffect(() => {
        const interval = setInterval(() => {
            setRotatingIndexes(prev => {
                const newMap = new Map(prev);
                const calendar = generateCalendar();

                calendar.flat().forEach(day => {
                    if (day) {
                        const dayDiaries = getDiariesForDate(day);
                        if (dayDiaries.length > 1) {
                            const currentIndex = prev.get(day) || 0;
                            const nextIndex = (currentIndex + 1) % dayDiaries.length;
                            newMap.set(day, nextIndex);
                        }
                    }
                });

                return newMap;
            });
        }, 2000); // 每 2 秒切換

        return () => clearInterval(interval);
    }, [diaries, currentYear, currentMonth]);

    // 處理日期點擊（支援多筆日記）
    const handleDateClick = (day: number) => {
        const dateStr = `${currentYear}-${String(currentMonth).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        const dayDiaries = getDiariesForDate(day);

        if (dayDiaries.length === 0) {
            // 沒有日記：新增
            navigate(`/diary/new?date=${dateStr}`);
        } else if (dayDiaries.length === 1) {
            // 一篇日記：直接編輯
            navigate(`/diary/edit/${dayDiaries[0].id}`);
        } else {
            // 多筆日記：顯示選擇彈窗
            setSelectedDateDiaries(dayDiaries);
        }
    };

    // 處理「再寫一篇」按鈕點擊
    const handleAddAnother = (day: number, e?: React.MouseEvent) => {
        if (e) e.stopPropagation();
        const dateStr = `${currentYear}-${String(currentMonth).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        navigate(`/diary/new?date=${dateStr}`);
        setSelectedDateDiaries(null);
    };

    // 上個月
    const previousMonth = () => {
        if (currentMonth === 1) {
            setCurrentMonth(12);
            setCurrentYear(currentYear - 1);
        } else {
            setCurrentMonth(currentMonth - 1);
        }
    };

    // 下個月
    const nextMonth = () => {
        if (currentMonth === 12) {
            setCurrentMonth(1);
            setCurrentYear(currentYear + 1);
        } else {
            setCurrentMonth(currentMonth + 1);
        }
    };

    if (!user) {
        return <Navigate to="/login" replace />;
    }

    const calendar = generateCalendar();
    const weekDays = ['週日', '週一', '週二', '週三', '週四', '週五', '週六'];

    return (
        <>
            <style>{`
                /* DiaryCalendar Mobile Responsive Styles */
                @media (max-width: 600px) {
                    /* Calendar header container - flex space-between layout */
                    .calendar-header-nav {
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        width: 100%;
                        gap: 2vw;
                        padding: 0 0.25rem;
                    }
                    
                    /* Month navigation buttons - prevent overflow */
                    .calendar-nav-button {
                        white-space: nowrap;
                        min-width: max-content;
                        width: max-content;
                        padding: 4px 8px !important;
                        font-size: 0.85rem;
                        flex-shrink: 0;
                    }
                    
                    /* Year/Month title - fluid font-size with clamp */
                    .calendar-date-title {
                        font-size: clamp(0.9rem, 3.5vw, 1.2rem) !important;
                        letter-spacing: -0.02em;
                        flex: 1;
                        text-align: center;
                        white-space: nowrap;
                        min-width: fit-content;
                        padding: 0 8px;
                        box-sizing: border-box;
                        overflow: visible;
                    }
                    
                    /* Subtitle text */
                    .calendar-subtitle {
                        font-size: 0.875rem;
                    }
                    
                    /* Calendar grid layout - percentage gap for perfect fit */
                    .calendar-grid {
                        display: grid;
                        grid-template-columns: repeat(7, 1fr);
                        column-gap: 1%;
                        row-gap: 1%;
                        width: 100%;
                    }
                    
                    /* Date cell square ratio with minimal padding */
                    .calendar-date-cell {
                        aspect-ratio: 1 / 1;
                        font-size: 0.75rem;
                        padding: 2px;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                    }
                    
                    /* Weekday header - 15% smaller on mobile */
                    .calendar-weekday {
                        font-size: 0.85rem;  /* 15% smaller than 1rem */
                        padding: 0.25rem;
                        text-align: center;
                    }
                }
                
                @media (max-width: 480px) {
                    .calendar-date-title {
                        font-size: 1rem !important; /* even smaller for tiny screens */
                    }
                    
                    .calendar-nav-button {
                        font-size: 0.75rem;
                        padding: 0.4rem 0.6rem !important;
                    }
                }
                
                @media (max-width: 360px) {
                    .calendar-nav-button {
                        font-size: 0.7rem;
                        padding: 3px 6px !important;
                    }
                    
                    .calendar-date-cell {
                        font-size: 0.7rem;
                        padding: 0.15rem;
                    }
                    
                    .calendar-weekday {
                        font-size: 0.7rem;
                    }
                }
            `}</style>
            <div className="min-h-[calc(100vh-100px)] py-8">
                <div className="max-w-6xl mx-auto">
                    {/* 返回主選單按鈕 */}
                    <div className="mb-6">
                        <button
                            onClick={() => navigate('/')}
                            className="px-6 py-3 bg-blue-400 border-4 border-blue-600 rounded-lg font-bold hover:bg-blue-500 transition-colors"
                        >
                            ← 返回主選單
                        </button>
                    </div>

                    {/* 標題和月份導航 */}
                    <div className="mb-8">
                        <div className="flex items-center justify-between mb-4 calendar-header-nav">
                            <button
                                onClick={previousMonth}
                                className="px-4 py-2 bg-gray-300 border-4 border-gray-500 rounded-lg font-bold hover:bg-gray-400 calendar-nav-button"
                            >
                                ← 上個月
                            </button>

                            <h1 className="text-4xl font-bold calendar-date-title">
                                {currentYear} 年 {currentMonth} 月
                            </h1>

                            <button
                                onClick={nextMonth}
                                className="px-4 py-2 bg-gray-300 border-4 border-gray-500 rounded-lg font-bold hover:bg-gray-400 calendar-nav-button"
                            >
                                下個月 →
                            </button>
                        </div>
                        <p className="text-lg opacity-80 text-center calendar-subtitle">點擊日期記錄今天的心情</p>
                    </div>

                    {/* 日曆 */}
                    <div className="bg-white border-4 border-gray-300 rounded-lg p-6">
                        {/* 星期標題 */}
                        <div className="grid grid-cols-7 gap-2 mb-4">
                            {weekDays.map((day) => (
                                <div key={day} className="text-center font-bold py-2 bg-yellow-100 border-2 border-yellow-400 rounded">
                                    {day}
                                </div>
                            ))}
                        </div>

                        {/* 日期格子 */}
                        <div className="space-y-2">
                            {calendar.map((week, weekIndex) => (
                                <div key={weekIndex} className="grid grid-cols-7 gap-2">
                                    {week.map((day, dayIndex) => {
                                        if (day === null) {
                                            return <div key={dayIndex} className="aspect-square" />;
                                        }

                                        // 獲取該日期的所有日記
                                        const dayDiaries = getDiariesForDate(day);
                                        // 獲取當前輪播索引
                                        const currentIndex = rotatingIndexes.get(day) || 0;
                                        // 獲取當前顯示的日記
                                        const diary = dayDiaries[currentIndex];
                                        const isToday =
                                            day === new Date().getDate() &&
                                            currentMonth === new Date().getMonth() + 1 &&
                                            currentYear === new Date().getFullYear();

                                        return (
                                            <div
                                                key={dayIndex}
                                                className={`
                        aspect-square border-4 rounded-lg p-2 relative
                        ${isToday
                                                        ? 'border-blue-500 bg-blue-50'
                                                        : diary
                                                            ? 'border-yellow-400 bg-yellow-50'
                                                            : 'border-gray-300 bg-white hover:border-yellow-300'
                                                    }
                      `}
                                            >
                                                <div className="text-sm font-bold mb-1">{day}</div>

                                                {/* 生理期標記 - 總是顯示（如果有的話） */}
                                                {diary?.period_marker && (
                                                    <img
                                                        src={PERIOD_MARKER.icon}
                                                        alt={PERIOD_MARKER.name}
                                                        className="w-5 h-5 pixelated absolute top-1 right-1"
                                                    />
                                                )}

                                                {/* 情緒圖標 */}
                                                {diary && diary.mood && (
                                                    <button
                                                        onClick={() => handleDateClick(day)}
                                                        className="w-full flex flex-col items-center hover:scale-105 transition-transform"
                                                    >
                                                        <img
                                                            src={getMoodIcon(diary.mood)}
                                                            alt={getMoodName(diary.mood)}
                                                            className="w-12 h-12 pixelated"
                                                        />
                                                    </button>
                                                )}



                                                {/* 已有日記：顯示「再寫一篇」按鈕 */}
                                                {dayDiaries.length > 0 && (
                                                    <button
                                                        onClick={(e) => handleAddAnother(day, e)}
                                                        className="absolute bottom-1 right-1 w-6 h-6 bg-green-500 text-white rounded-full text-xs font-bold hover:bg-green-600 transition-colors flex items-center justify-center"
                                                        title="再寫一篇"
                                                    >
                                                        +
                                                    </button>
                                                )}

                                                {/* 沒有日記時顯示 + 號 */}
                                                {!diary && (
                                                    <button
                                                        onClick={() => handleDateClick(day)}
                                                        className="w-full h-full flex items-center justify-center hover:scale-105 transition-transform"
                                                    >
                                                        <div className="text-3xl opacity-30">+</div>
                                                    </button>
                                                )}
                                            </div>
                                        );
                                    })}
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* 說明 */}
                    <div className="mt-6 p-4 bg-yellow-100 border-4 border-yellow-400 rounded-lg">
                        <div className="flex items-start gap-3">
                            <span className="text-2xl">💡</span>
                            <div>
                                <div className="font-bold mb-1">每日提醒</div>
                                <div className="text-sm">記得每天都記錄心情，幫助追蹤情緒變化！</div>
                            </div>
                        </div>
                    </div>
                </div>
                {/* 日記選擇彈窗 */}
                {selectedDateDiaries && (
                    <DiarySelectionModal
                        diaries={selectedDateDiaries}
                        onSelect={(diaryId) => {
                            navigate(`/diary/edit/${diaryId}`);
                            setSelectedDateDiaries(null);
                        }}
                        onAddNew={() => {
                            // 從彈窗新增，需要解析日期
                            const date = new Date(selectedDateDiaries[0].date);
                            handleAddAnother(date.getDate());
                        }}
                        onClose={() => setSelectedDateDiaries(null)}
                    />
                )}
            </div>
        </>
    );
};

