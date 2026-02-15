import React from 'react';
import type { Diary } from '../types/diary';
import { getMoodIcon, getMoodName, PERIOD_MARKER } from '../types/diary';

interface DiaryCardProps {
    diary: Diary;
    onClick: () => void;
}

export const DiaryCard: React.FC<DiaryCardProps> = ({ diary, onClick }) => {
    // 解析日期
    const date = new Date(diary.date);
    const dayOfWeek = date.toLocaleDateString('zh-TW', { weekday: 'short' });
    const day = date.getDate();
    const monthYear = date.toLocaleDateString('zh-TW', { year: 'numeric', month: 'long' });

    // 預覽內容（最多 100 字）
    const contentPreview = diary.content
        ? diary.content.length > 100
            ? diary.content.substring(0, 100) + '...'
            : diary.content
        : '';

    // 取得第一張圖片作為縮圖
    const thumbnail = diary.images && diary.images.length > 0 ? diary.images[0] : null;

    return (
        <>
            <style>{`
                /* DiaryCard Mobile Responsive Styles */
                @media (max-width: 600px) {
                    /* Main card layout - vertical stacking */
                    .diary-card-container {
                        flex-direction: column !important;
                        gap: 1rem;
                    }
                    
                    /* Date box centered at top */
                    .diary-date-box {
                        align-self: center;
                        margin-bottom: 0.5rem;
                    }
                    
                    /* Content area full width */
                    .diary-content-area {
                        width: 100%;
                        min-width: 100%;
                    }
                    
                    /* Preview text limitation */
                    .diary-content-preview {
                        display: -webkit-box;
                        -webkit-line-clamp: 3;
                        -webkit-box-orient: vertical;
                        overflow: hidden;
                        width: 100%;
                    }
                    
                    /* Thumbnail image scaling */
                    .diary-thumbnail {
                        max-width: 100% !important;
                        width: 100% !important;
                        height: auto !important;
                        margin-top: 0.5rem;
                    }
                    
                    /* Header with mood and period marker */
                    .diary-header {
                        justify-content: space-between;
                        width: 100%;
                    }
                }
            `}</style>
            <div
                onClick={onClick}
                className="bg-white border-4 border-gray-300 rounded-lg p-4 hover:border-yellow-500 hover:shadow-lg transition-all cursor-pointer group"
            >
                <div className="flex gap-4 diary-card-container">
                    {/* 左側：日期 */}
                    <div className="flex-shrink-0 text-center diary-date-box">
                        <div className="w-16 h-16 bg-yellow-100 border-4 border-yellow-400 rounded-lg flex flex-col items-center justify-center">
                            <div className="text-xs font-medium text-yellow-700">{dayOfWeek}</div>
                            <div className="text-2xl font-bold">{day}</div>
                        </div>
                    </div>

                    {/* 中間：內容 */}
                    <div className="flex-1 min-w-0 diary-content-area">
                        <div className="flex items-start gap-2 mb-2 diary-header">
                            {/* 情緒圖標 */}
                            {diary.mood && (
                                <>
                                    <img
                                        src={getMoodIcon(diary.mood)}
                                        alt={getMoodName(diary.mood)}
                                        className="w-8 h-8 pixelated"
                                    />
                                    <div>
                                        <h3 className="font-bold text-lg">{getMoodName(diary.mood)}</h3>
                                        <div className="text-sm text-gray-600">{monthYear}</div>
                                    </div>
                                </>
                            )}
                            {!diary.mood && (
                                <div>
                                    <h3 className="font-bold text-lg text-gray-400">無情緒記錄</h3>
                                    <div className="text-sm text-gray-600">{monthYear}</div>
                                </div>
                            )}
                            {/* 生理期標記 */}
                            {diary.period_marker && (
                                <img
                                    src={PERIOD_MARKER.icon}
                                    alt={PERIOD_MARKER.name}
                                    className="w-6 h-6 pixelated ml-auto"
                                    title={PERIOD_MARKER.name}
                                />
                            )}
                        </div>

                        {/* 內容預覽 */}
                        {contentPreview && (
                            <p className="text-sm text-gray-700 line-clamp-2 mb-2 diary-content-preview">{contentPreview}</p>
                        )}

                        {/* 圖片指示器 */}
                        {diary.images && diary.images.length > 0 && (
                            <div className="flex items-center gap-1 text-xs text-gray-500">
                                <span>📷</span>
                                <span>{diary.images.length} 張照片</span>
                            </div>
                        )}
                    </div>

                    {/* 右側：縮圖（如果有） */}
                    {thumbnail && (
                        <div className="flex-shrink-0 diary-thumbnail-container">
                            <img
                                src={thumbnail}
                                alt="縮圖"
                                className="w-20 h-20 object-cover border-2 border-gray-300 rounded-lg diary-thumbnail"
                            />
                        </div>
                    )}

                    {/* 操作按鈕 */}
                    <div className="flex flex-col justify-center ml-2 border-l-2 border-gray-100 pl-2">
                        <button
                            className="p-2 text-gray-400 hover:text-yellow-600 hover:bg-yellow-50 rounded-full transition-colors"
                            title="查看與編輯"
                        >
                            ✏️
                        </button>
                    </div>
                </div>
            </div>
        </>
    );
};

