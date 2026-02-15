import React from 'react';

interface DatePickerProps {
    selectedDate: string; // YYYY-MM-DD
    onDateChange: (date: string) => void;
}

export const DatePicker: React.FC<DatePickerProps> = ({ selectedDate, onDateChange }) => {
    // 解析日期
    const parseDate = (dateStr: string) => {
        const date = new Date(dateStr);
        return {
            year: date.getFullYear(),
            month: date.getMonth() + 1,
            day: date.getDate(),
        };
    };

    const { year, month, day } = selectedDate ? parseDate(selectedDate) : {
        year: new Date().getFullYear(),
        month: new Date().getMonth() + 1,
        day: new Date().getDate(),
    };

    // 生成年份選項（過去 100 年到今年）
    const currentYear = new Date().getFullYear();
    const years = Array.from({ length: 101 }, (_, i) => currentYear - i);

    // 生成月份選項
    const months = Array.from({ length: 12 }, (_, i) => i + 1);

    // 生成日期選項（根據年月）
    const getDaysInMonth = (year: number, month: number) => {
        return new Date(year, month, 0).getDate();
    };
    const days = Array.from({ length: getDaysInMonth(year, month) }, (_, i) => i + 1);

    // 處理日期變更
    const handleChange = (newYear: number, newMonth: number, newDay: number) => {
        // 確保日期不超過該月的最大天數
        const maxDay = getDaysInMonth(newYear, newMonth);
        const validDay = Math.min(newDay, maxDay);

        const dateStr = `${newYear}-${String(newMonth).padStart(2, '0')}-${String(validDay).padStart(2, '0')}`;
        onDateChange(dateStr);
    };

    // 今天的日期
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    return (
        <>
            <style>{`
                /* DatePicker Mobile Responsive Styles */
                @media (max-width: 600px) {
                    /* Prevent year number truncation */
                    .date-picker-select {
                        padding: 0.5rem 0.25rem !important;
                        width: 100%;
                        overflow: visible;
                        box-sizing: border-box;
                    }
                    
                    .date-picker-select option {
                        padding: 0.25rem 0.5rem;
                    }
                    
                    /* Date display area - force single line */
                    .date-display-text {
                        white-space: nowrap;
                        overflow: visible;
                        font-size: clamp(0.9rem, 4vw, 1.5rem);
                        letter-spacing: -0.02em;
                    }
                    
                    /* Grid spacing optimization */
                    .date-picker-grid {
                        gap: 0.5rem !important;
                    }
                    
                    /* Label text smaller */
                    .date-picker-label {
                        font-size: 0.875rem;
                        margin-bottom: 0.25rem;
                    }
                }
                
                @media (max-width: 360px) {
                    .date-display-text {
                        font-size: 0.85rem;
                        letter-spacing: -0.03em;
                    }
                }
            `}</style>
            <div className="space-y-4">
                <h3 className="text-xl font-bold">選擇日期</h3>

                <div className="grid grid-cols-3 gap-4 date-picker-grid">
                    {/* 年份選擇 */}
                    <div>
                        <label className="block text-sm font-medium mb-2 date-picker-label">年</label>
                        <select
                            value={year}
                            onChange={(e) => handleChange(Number(e.target.value), month, day)}
                            className="w-full p-3 border-4 border-gray-300 rounded-lg font-medium focus:border-yellow-500 focus:outline-none date-picker-select"
                        >
                            {years.map((y) => (
                                <option key={y} value={y}>
                                    {y}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* 月份選擇 */}
                    <div>
                        <label className="block text-sm font-medium mb-2 date-picker-label">月</label>
                        <select
                            value={month}
                            onChange={(e) => handleChange(year, Number(e.target.value), day)}
                            className="w-full p-3 border-4 border-gray-300 rounded-lg font-medium focus:border-yellow-500 focus:outline-none date-picker-select"
                        >
                            {months.map((m) => (
                                <option key={m} value={m}>
                                    {m}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* 日期選擇 */}
                    <div>
                        <label className="block text-sm font-medium mb-2 date-picker-label">日</label>
                        <select
                            value={day}
                            onChange={(e) => handleChange(year, month, Number(e.target.value))}
                            className="w-full p-3 border-4 border-gray-300 rounded-lg font-medium focus:border-yellow-500 focus:outline-none date-picker-select"
                        >
                            {days.map((d) => (
                                <option key={d} value={d}>
                                    {d}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* 顯示選中的日期 */}
                <div className="p-4 bg-blue-50 border-4 border-blue-200 rounded-lg">
                    <div className="text-center">
                        <div className="text-sm text-gray-600">選擇的日期</div>
                        <div className="text-2xl font-bold mt-1 date-display-text">
                            {year} 年 {month} 月 {day} 日
                        </div>
                        <div className="text-sm text-gray-600 mt-1">
                            {new Date(selectedDate).toLocaleDateString('zh-TW', { weekday: 'long' })}
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
};
