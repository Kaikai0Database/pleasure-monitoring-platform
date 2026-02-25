import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useSearchParams, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { DatePicker } from '../components/DatePicker';
import { MoodSelector } from '../components/MoodSelector';
import { ImageUploader } from '../components/ImageUploader';
import { diaryService } from '../services/diaryService';
import type { DiaryFormData } from '../types/diary';

export const DiaryEditor: React.FC = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const { id } = useParams<{ id: string }>();
    const [searchParams] = useSearchParams();
    const isEditing = !!id;

    // 從 URL 獲取預設日期
    const defaultDate = searchParams.get('date') || new Date().toISOString().split('T')[0];

    // 表單狀態
    const [date, setDate] = useState(defaultDate);
    const [mood, setMood] = useState('');
    const [content, setContent] = useState('');
    const [images, setImages] = useState<string[]>([]);
    const [periodMarker, setPeriodMarker] = useState(false);

    // UI 狀態
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);

    // 載入現有日記資料（編輯模式）
    useEffect(() => {
        const loadDiary = async () => {
            if (isEditing && id) {
                try {
                    setLoading(true);
                    const diary = await diaryService.getDiaryById(parseInt(id));

                    // 填充表單資料
                    setDate(diary.date);
                    setMood(diary.mood || '');
                    setContent(diary.content || '');
                    setImages(diary.images || []);
                    setPeriodMarker(diary.period_marker);
                } catch (err) {
                    setError(err instanceof Error ? err.message : '載入日記失敗');
                } finally {
                    setLoading(false);
                }
            }
        };

        loadDiary();
    }, [id, isEditing]);

    const handleSubmit = async () => {
        // 驗證 - 至少要有心情或生理期標記
        if (!mood && !periodMarker) {
            setError('請至少選擇心情或標記生理期');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const diaryData: DiaryFormData = {
                date,
                mood: mood || undefined,  // 允許為空
                content: content || undefined,
                images: images,
                period_marker: periodMarker,
            };

            if (isEditing && id) {
                await diaryService.updateDiary(parseInt(id), diaryData);
            } else {
                await diaryService.createDiary(diaryData);
                // 日記創建成功，不再給予XP獎勵
            }

            setSuccess(true);
            setTimeout(() => {
                navigate('/diary');
            }, 1000);
        } catch (err) {
            setError(err instanceof Error ? err.message : '儲存失敗');
        } finally {
            setLoading(false);
        }
    };

    if (!user) {
        return <Navigate to="/login" replace />;
    }

    return (
        <>
            <style>{`
                /* DiaryEditor Mobile Responsive Styles */
                @media (max-width: 600px) {
                    /* Container optimization - prevent overflow */
                    .diary-editor-container {
                        max-width: 95%;
                        width: 95%;
                        margin: 0 auto;
                        box-sizing: border-box;
                        padding: 1rem 0.5rem;
                    }
                    
                    /* Dynamic height */
                    .diary-card {
                        min-height: fit-content;
                        height: auto;
                    }
                    
                    /* Year display - prevent truncation */
                    .diary-date-display {
                        white-space: nowrap;
                        flex-basis: auto;
                        overflow: visible;
                    }
                    
                    /* Mood icon lock - prevent distortion */
                    .diary-mood-icon {
                        flex-shrink: 0 !important;
                        object-fit: contain;
                        width: 40px !important;
                        height: 40px !important;
                    }
                    
                    /* Date and mood row alignment */
                    .diary-header-row {
                        align-items: center;
                        gap: 0.75rem;
                    }
                    
                    /* Image adaptive sizing */
                    .diary-image {
                        width: 100% !important;
                        max-height: 300px;
                        object-fit: cover;
                    }
                    
                    /* Media player scaling */
                    .diary-audio-player {
                        width: 100%;
                        max-width: 100%;
                    }
                    
                    /* Content area */
                    .diary-content-area {
                        width: 100%;
                        word-break: break-word;
                    }
                }

                /* ── Button row: always horizontal on ALL screen sizes ── */
                .diary-button-container {
                    display: flex;
                    flex-direction: row !important;
                    flex-wrap: nowrap !important;
                    gap: 12px;
                    width: 100%;
                }

                .diary-button {
                    flex: 1;
                    min-width: 0;
                    /* scale font so text never wraps inside button */
                    font-size: clamp(0.85rem, 3.5vw, 1.125rem) !important;
                    padding: 1rem 0.5rem !important;
                    white-space: nowrap;
                    text-align: center;
                }
                
                @media (max-width: 480px) {
                    .diary-editor-container {
                        max-width: 98%;
                        width: 98%;
                        padding: 0.75rem 0.25rem;
                    }
                    
                    .diary-mood-icon {
                        width: 36px !important;
                        height: 36px !important;
                    }
                }
            `}</style>
            <div className="min-h-[calc(100vh-100px)] py-8 diary-editor-container">
                <div className="max-w-4xl mx-auto">
                    {/* 標題 */}
                    <div className="mb-8">
                        <h1 className="text-xl sm:text-4xl font-bold mb-2">
                            {isEditing ? '編輯日記' : '寫日記'}
                        </h1>
                        <p className="text-lg opacity-80">記錄今天的心情與故事</p>
                    </div>

                    {/* 表單 */}
                    <div className="space-y-8">
                        {/* 1. 選擇日期 */}
                        <div className="p-6 bg-white border-4 border-gray-300 rounded-lg">
                            <DatePicker selectedDate={date} onDateChange={setDate} />
                        </div>

                        {/* 2. 選擇心情與生理期標記 */}
                        <div className="p-6 bg-white border-4 border-gray-300 rounded-lg">
                            <MoodSelector
                                selectedMood={mood}
                                onMoodSelect={setMood}
                                periodMarker={periodMarker}
                                onPeriodToggle={setPeriodMarker}
                            />
                        </div>

                        {/* 3. 文字內容（只要選了心情或生理期就顯示） */}
                        {(mood || periodMarker) && (
                            <>
                                <div className="p-6 bg-white border-4 border-gray-300 rounded-lg">
                                    <h3 className="text-xl font-bold mb-4">寫下今天的故事（選填）</h3>
                                    <textarea
                                        value={content}
                                        onChange={(e) => setContent(e.target.value)}
                                        placeholder="今天發生了什麼事？有什麼想記錄的嗎？"
                                        rows={8}
                                        className="w-full p-4 border-4 border-gray-300 rounded-lg resize-none focus:border-yellow-500 focus:outline-none font-medium"
                                    />
                                </div>

                                {/* 4. 上傳照片 */}
                                <div className="p-6 bg-white border-4 border-gray-300 rounded-lg">
                                    <ImageUploader images={images} onImagesChange={setImages} />
                                </div>
                            </>
                        )}

                        {/* 訊息提示 */}
                        {error && (
                            <div className="p-4 bg-red-100 border-4 border-red-400 rounded-lg text-red-700 font-medium">
                                ❌ {error}
                            </div>
                        )}

                        {success && (
                            <div className="p-4 bg-green-100 border-4 border-green-400 rounded-lg text-green-700 font-medium">
                                ✅ 儲存成功！即將返回日曆...
                            </div>
                        )}

                        {/* 按鈕 \u2013 inline styles guarantee single row */}
                        <div
                            style={{
                                display: 'flex',
                                flexDirection: 'row',
                                flexWrap: 'nowrap',
                                gap: '12px',
                                width: '100%',
                                padding: '0 0',
                            }}
                        >
                            <button
                                onClick={() => navigate('/diary')}
                                disabled={loading}
                                className="bg-gray-300 border-4 border-gray-500 rounded-lg font-bold hover:bg-gray-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                style={{
                                    flex: 1,
                                    minWidth: 0,
                                    padding: '1rem 0.5rem',
                                    fontSize: 'clamp(0.85rem, 3.5vw, 1.125rem)',
                                    whiteSpace: 'nowrap',
                                    textAlign: 'center',
                                    cursor: loading ? 'not-allowed' : 'pointer',
                                }}
                            >
                                取消
                            </button>
                            <button
                                onClick={handleSubmit}
                                disabled={loading || (!mood && !periodMarker)}
                                className="bg-yellow-400 border-4 border-yellow-600 rounded-lg font-bold hover:bg-yellow-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                style={{
                                    flex: 1,
                                    minWidth: 0,
                                    padding: '1rem 0.5rem',
                                    fontSize: 'clamp(0.85rem, 3.5vw, 1.125rem)',
                                    whiteSpace: 'nowrap',
                                    textAlign: 'center',
                                    cursor: (loading || (!mood && !periodMarker)) ? 'not-allowed' : 'pointer',
                                }}
                            >
                                {loading ? '儲存中...' : isEditing ? '更新日記' : '儲存日記'}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
};

