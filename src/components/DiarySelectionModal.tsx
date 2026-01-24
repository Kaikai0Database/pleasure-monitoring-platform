import React from 'react';
import type { Diary } from '../types/diary';
import { getMoodIcon } from '../types/diary';

interface DiarySelectionModalProps {
    diaries: Diary[];
    onSelect: (diaryId: number) => void;
    onAddNew: () => void;
    onClose: () => void;
}

export const DiarySelectionModal: React.FC<DiarySelectionModalProps> = ({
    diaries,
    onSelect,
    onAddNew,
    onClose
}) => {
    // 阻止點擊冒泡，避免點擊內容時關閉彈窗
    const handleContentClick = (e: React.MouseEvent) => {
        e.stopPropagation();
    };

    return (
        <div
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
            onClick={onClose}
        >
            <div
                className="bg-white rounded-xl shadow-2xl p-6 max-w-md w-full max-h-[80vh] overflow-y-auto"
                onClick={handleContentClick}
            >
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold text-gray-800">
                        {diaries.length > 0 ? diaries[0].date : '日記列表'}
                    </h2>
                    <button
                        onClick={onClose}
                        className="text-gray-500 hover:text-gray-700 p-2 rounded-full hover:bg-gray-100 transition-colors"
                    >
                        ✕
                    </button>
                </div>

                <div className="space-y-4 mb-6">
                    {diaries.map((diary, index) => (
                        <button
                            key={diary.id}
                            onClick={() => onSelect(diary.id)}
                            className="w-full p-4 border-4 border-gray-200 rounded-xl hover:border-yellow-400 hover:bg-yellow-50 transition-all text-left group"
                        >
                            <div className="flex items-center gap-4">
                                <div className="w-16 h-16 flex-shrink-0 bg-gray-100 rounded-lg flex items-center justify-center overflow-hidden border-2 border-gray-200">
                                    {diary.mood ? (
                                        <img
                                            src={getMoodIcon(diary.mood)}
                                            alt={diary.mood}
                                            className="w-full h-full object-cover pixelated"
                                        />
                                    ) : (
                                        <span className="text-2xl">📝</span>
                                    )}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center justify-between mb-1">
                                        <span className="font-bold text-gray-800 text-lg">
                                            日記 #{index + 1}
                                        </span>
                                        {diary.period_marker && (
                                            <span className="bg-pink-100 text-pink-600 text-xs px-2 py-1 rounded-full font-bold">
                                                生理期
                                            </span>
                                        )}
                                    </div>
                                    <div className="text-sm text-gray-600 truncate">
                                        {diary.content || (diary.images ? '僅有圖片' : '無內容')}
                                    </div>
                                    <div className="text-xs text-gray-400 mt-1">
                                        {new Date(diary.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </div>
                                </div>
                                <div className="text-gray-300 group-hover:text-yellow-500 text-xl font-bold">
                                    →
                                </div>
                            </div>
                        </button>
                    ))}
                </div>

                <button
                    onClick={onAddNew}
                    className="w-full py-4 bg-green-500 text-white rounded-xl font-bold hover:bg-green-600 transition-colors flex items-center justify-center gap-2 text-lg shadow-md hover:shadow-lg transform active:scale-[0.98]"
                >
                    <span className="text-2xl">+</span> 再寫一篇日記
                </button>
            </div>
        </div>
    );
};
