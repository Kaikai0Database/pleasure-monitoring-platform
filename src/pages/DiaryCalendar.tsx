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
                /* ── DiaryCalendar: unified calendar grid ── */

                /* Header nav: always single row */
                .calendar-header-nav {
                    display: flex;
                    flex-direction: row;
                    align-items: center;
                    justify-content: center;
                    width: 100%;
                    gap: 0.5rem;
                }

                /* Nav buttons: never shrink or wrap */
                .calendar-nav-button {
                    white-space: nowrap;
                    flex-shrink: 0;
                }

                /* Year/month title: single row, never clips */
                h1.calendar-date-title {
                    flex: 1;
                    display: flex;
                    flex-direction: row;
                    align-items: center;
                    justify-content: center;
                    gap: 4px;
                    white-space: nowrap;
                    overflow: visible;
                    text-align: center;
                    font-size: 1.5rem;   /* desktop default */
                    line-height: 1.2;
                    margin: 0;
                }

                /* Unified 7-column grid for the entire calendar */
                .calendar-grid {
                    display: grid;
                    grid-template-columns: repeat(7, 1fr);
                    gap: 2px;
                    width: 100%;
                    max-width: 100vw;
                    box-sizing: border-box;
                }

                /* Weekday header cells */
                .calendar-weekday {
                    text-align: center;
                    font-weight: bold;
                    padding: 0.3rem 0.1rem;
                    font-size: clamp(0.6rem, 2vw, 1rem);
                    background: #fef9c3;
                    border: 2px solid #facc15;
                    border-radius: 4px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    word-break: keep-all;
                }

                /* Date cells: top = date number, bottom = + sign */
                .calendar-date-cell {
                    aspect-ratio: 1 / 1.2;
                    border-width: 3px;
                    border-style: solid;
                    border-radius: 6px;
                    padding: 2px 2px 3px;
                    position: relative;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: space-between;
                    box-sizing: border-box;
                    min-height: 0;
                    cursor: pointer;
                    image-rendering: pixelated;
                }

                /* Empty placeholder cells */
                .calendar-empty-cell {
                    aspect-ratio: 1 / 1.2;
                }

                /* Date number label */
                .calendar-day-number {
                    font-size: clamp(0.55rem, 2.5vw, 0.875rem);
                    font-weight: bold;
                    line-height: 1;
                    align-self: flex-start;
                    padding: 1px 2px;
                }

                /* Mood icon sizing relative to cell */
                .calendar-mood-img {
                    width: clamp(18px, 5vw, 48px);
                    height: clamp(18px, 5vw, 48px);
                    image-rendering: pixelated;
                }

                /* Period marker icon */
                .calendar-period-img {
                    width: clamp(10px, 3vw, 20px);
                    height: clamp(10px, 3vw, 20px);
                    image-rendering: pixelated;
                    position: absolute;
                    top: 2px;
                    right: 2px;
                }

                /* Green + add-another button */
                .calendar-add-btn {
                    position: absolute;
                    bottom: 2px;
                    right: 2px;
                    width: clamp(14px, 4vw, 24px);
                    height: clamp(14px, 4vw, 24px);
                    background: #22c55e;
                    color: white;
                    border-radius: 50%;
                    font-size: clamp(0.5rem, 2vw, 0.75rem);
                    font-weight: bold;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    line-height: 1;
                    border: none;
                    cursor: pointer;
                }
                .calendar-add-btn:hover { background: #16a34a; }

                /* + for empty dates – pinned to bottom, centered */
                .calendar-plus-label {
                    font-size: clamp(0.85rem, 4vw, 1.5rem);
                    opacity: 0.35;
                    line-height: 1;
                    /* ensure it sits at the bottom half of the cell */
                    margin-top: auto;
                }

                /* Subtitle text */
                .calendar-subtitle {
                    font-size: 0.875rem;
                }

                /* Mobile overrides ≤600px */
                @media (max-width: 600px) {
                    h1.calendar-date-title {
                        font-size: 1.2rem !important;  /* 20px – clearly readable */
                    }
                    .calendar-nav-button {
                        padding: 8px 12px !important;
                        font-size: 0.85rem;
                    }
                    .calendar-subtitle {
                        font-size: 0.8rem;
                    }
                }

                /* Very small phones ≤380px */
                @media (max-width: 380px) {
                    h1.calendar-date-title {
                        font-size: 1rem !important;
                    }
                    .calendar-nav-button {
                        font-size: 0.75rem;
                        padding: 6px 8px !important;
                    }
                }
            `}</style>
            <div className="min-h-[calc(100vh-100px)] py-8 px-3 sm:px-0">
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
                        {/* Nav row: always single horizontal line */}
                        <div
                            className="mb-4"
                            style={{
                                display: 'flex',
                                flexDirection: 'row',
                                alignItems: 'center',
                                justifyContent: 'center',
                                gap: '0.5rem',
                                width: '100%',
                            }}
                        >
                            <button
                                onClick={previousMonth}
                                className="bg-gray-300 border-4 border-gray-500 rounded-lg font-bold hover:bg-gray-400"
                                style={{
                                    padding: '12px 16px',
                                    fontSize: '0.95rem',
                                    whiteSpace: 'nowrap',
                                    flexShrink: 0,
                                    cursor: 'pointer',
                                }}
                            >
                                ← 上個月
                            </button>

                            {/* Year/month title – inline styles win over everything */}
                            <h1
                                className="font-bold"
                                style={{
                                    display: 'flex',
                                    flexDirection: 'row',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    gap: '4px',
                                    whiteSpace: 'nowrap',
                                    overflow: 'visible',
                                    fontSize: '1.4rem',   /* 22px – always visible */
                                    flex: 1,
                                    margin: 0,
                                    minWidth: 'fit-content',
                                }}
                            >
                                <span>{currentYear}</span>
                                <span>年</span>
                                <span>{currentMonth}</span>
                                <span>月</span>
                            </h1>

                            <button
                                onClick={nextMonth}
                                className="bg-gray-300 border-4 border-gray-500 rounded-lg font-bold hover:bg-gray-400"
                                style={{
                                    padding: '12px 16px',
                                    fontSize: '0.95rem',
                                    whiteSpace: 'nowrap',
                                    flexShrink: 0,
                                    cursor: 'pointer',
                                }}
                            >
                                下個月 →
                            </button>
                        </div>
                        <p className="text-lg opacity-80 text-center calendar-subtitle">點擊日期記錄今天的心情</p>
                    </div>

                    {/* 日曆 - 統一 7 欄格線 */}
                    <div className="bg-white border-4 border-gray-300 rounded-lg p-2 sm:p-4" style={{ width: '100%', boxSizing: 'border-box', overflowX: 'hidden' }}>
                        <div className="calendar-grid">
                            {/* 星期標題列 */}
                            {weekDays.map((day) => (
                                <div key={day} className="calendar-weekday">
                                    {day}
                                </div>
                            ))}

                            {/* 日期格子（攤平為單一格線） */}
                            {calendar.flat().map((day, idx) => {
                                if (day === null) {
                                    return <div key={`empty-${idx}`} className="calendar-empty-cell" />;
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

                                const borderColor = isToday
                                    ? '#3b82f6'
                                    : diary
                                        ? '#facc15'
                                        : '#d1d5db';
                                const bgColor = isToday
                                    ? '#eff6ff'
                                    : diary
                                        ? '#fefce8'
                                        : '#ffffff';

                                return (
                                    <div
                                        key={`day-${idx}`}
                                        onClick={() => handleDateClick(day)}
                                        style={{
                                            borderWidth: '3px',
                                            borderStyle: 'solid',
                                            borderColor,
                                            background: bgColor,
                                            borderRadius: '6px',
                                            padding: '3px',
                                            position: 'relative',
                                            display: 'flex',
                                            flexDirection: 'column',
                                            alignItems: 'center',
                                            justifyContent: 'space-between',
                                            boxSizing: 'border-box',
                                            aspectRatio: '1 / 1.2',
                                            cursor: 'pointer',
                                            imageRendering: 'pixelated',
                                            minHeight: 0,
                                        }}
                                    >
                                        {/* Date number – top-left */}
                                        <span
                                            style={{
                                                fontSize: 'clamp(0.5rem, 2.2vw, 0.85rem)',
                                                fontWeight: 'bold',
                                                lineHeight: 1,
                                                alignSelf: 'flex-start',
                                                padding: '1px 2px',
                                            }}
                                        >{day}</span>

                                        {/* 生理期標記 */}
                                        {diary?.period_marker && (
                                            <img
                                                src={PERIOD_MARKER.icon}
                                                alt={PERIOD_MARKER.name}
                                                className="calendar-period-img"
                                            />
                                        )}

                                        {/* 情緒圖標 – centre of cell */}
                                        {diary && diary.mood && (
                                            <div
                                                style={{
                                                    flex: 1,
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'center',
                                                }}
                                                className="hover:scale-105 transition-transform"
                                            >
                                                <img
                                                    src={getMoodIcon(diary.mood)}
                                                    alt={getMoodName(diary.mood)}
                                                    style={{
                                                        width: 'clamp(16px, 4.5vw, 44px)',
                                                        height: 'clamp(16px, 4.5vw, 44px)',
                                                        imageRendering: 'pixelated',
                                                    }}
                                                />
                                            </div>
                                        )}

                                        {/* 已有日記：「再寫一篇」綠色 + 按鈕（position: absolute, 底右） */}
                                        {dayDiaries.length > 0 && (
                                            <button
                                                onClick={(e) => handleAddAnother(day, e)}
                                                title="再寫一篇"
                                                style={{
                                                    position: 'absolute',
                                                    bottom: '2px',
                                                    right: '2px',
                                                    width: 'clamp(14px, 3.5vw, 22px)',
                                                    height: 'clamp(14px, 3.5vw, 22px)',
                                                    background: '#22c55e',
                                                    color: 'white',
                                                    borderRadius: '50%',
                                                    fontSize: 'clamp(0.5rem, 1.8vw, 0.75rem)',
                                                    fontWeight: 'bold',
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'center',
                                                    border: 'none',
                                                    cursor: 'pointer',
                                                    lineHeight: 1,
                                                }}
                                            >
                                                +
                                            </button>
                                        )}

                                        {/* 沒有日記時：大 + 號，底部居中 */}
                                        {!diary && (
                                            <span
                                                style={{
                                                    marginTop: 'auto',
                                                    fontSize: 'clamp(0.8rem, 3.8vw, 1.4rem)',
                                                    opacity: 0.35,
                                                    lineHeight: 1,
                                                    paddingBottom: '2px',
                                                }}
                                            >+</span>
                                        )}
                                    </div>
                                );
                            })}
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

