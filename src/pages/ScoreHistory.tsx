import React, { useEffect, useState } from 'react';
import { useNavigate, Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { historyApi } from '../services/api';
import type { AssessmentHistory } from '../types/api';
import { PixelCard } from '../components/ui/PixelCard';
import { PixelButton } from '../components/ui/PixelButton';
import { DeleteReasonModal } from '../components/DeleteReasonModal';
import { getScoreInterpretation } from '../data/questions';
import { ScoreTrendChart } from '../components/ScoreTrendChart';
import { Footer } from '../components/Footer';


export const ScoreHistory: React.FC = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();
    const [history, setHistory] = useState<AssessmentHistory[]>([]);
    const [trash, setTrash] = useState<AssessmentHistory[]>([]);

    const [view, setView] = useState<'active' | 'trash' | 'chart'>(() => {
        const params = new URLSearchParams(location.search);
        const viewParam = params.get('view');
        return (viewParam === 'active' || viewParam === 'trash' || viewParam === 'chart') ? viewParam : 'active';
    });
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');

    // Modal State
    const [deleteModalOpen, setDeleteModalOpen] = useState(false);
    const [selectedId, setSelectedId] = useState<number | null>(null);
    const [isPermanentDelete, setIsPermanentDelete] = useState(false);

    const fetchAllData = async () => {
        setIsLoading(true);
        setError('');
        try {
            const [historyRes, trashRes] = await Promise.all([
                historyApi.getHistory(),
                historyApi.getTrash()
            ]);

            if (historyRes.success && historyRes.history) {
                setHistory(historyRes.history);
            }
            if (trashRes.success && trashRes.history) {
                setTrash(trashRes.history);
            }
        } catch (err) {
            setError('無法載入資料');
            console.error('Failed to fetch data:', err);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        if (!user) {
            setIsLoading(false);
            return;
        }
        fetchAllData();
    }, [user]);

    const handleDeleteClick = (id: number, permanent: boolean = false) => {
        setSelectedId(id);
        setIsPermanentDelete(permanent);
        setDeleteModalOpen(true);
    };

    const handleConfirmDelete = async (reason: string) => {
        if (!selectedId) return;

        try {
            await historyApi.deleteHistory(selectedId, reason, isPermanentDelete);
            await fetchAllData(); // Refresh list
        } catch (err) {
            alert('刪除失敗，請稍後再試');
            console.error('Failed to delete history:', err);
        }
    };

    const handleRestore = async (id: number) => {
        try {
            await historyApi.restoreHistory(id);
            await fetchAllData(); // Refresh list
        } catch (err) {
            alert('還原失敗，請稍後再試');
            console.error('Failed to restore history:', err);
        }
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('zh-TW', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
        });
    };



    if (!user) {
        return <Navigate to="/login" replace />;
    }

    const currentList = view === 'active' ? history : trash;

    return (
        <div className="min-h-screen bg-gradient-to-br from-purple-100 to-blue-100 p-8">
            <div className="max-w-6xl mx-auto space-y-6">
                {/* Header */}
                <div className="flex items-center justify-between mb-8">
                    <div className="flex items-center gap-4">
                        <h1 className="text-4xl font-bold">
                            {view === 'trash' ? '資源回收桶' : view === 'chart' ? '心情趨勢圖' : '分數歷史'}
                        </h1>

                        <div className="flex bg-white rounded-lg border-2 border-black p-1">
                            <button
                                onClick={() => setView('active')}
                                className={`px-4 py-1 rounded ${view === 'active' ? 'bg-black text-white' : 'hover:bg-gray-100'}`}
                            >
                                列表
                            </button>
                            <button
                                onClick={() => setView('chart')}
                                className={`px-4 py-1 rounded ${view === 'chart' ? 'bg-black text-white' : 'hover:bg-gray-100'}`}
                            >
                                圖表
                            </button>
                            <button
                                onClick={() => setView('trash')}
                                className={`px-4 py-1 rounded flex items-center gap-2 ${view === 'trash' ? 'bg-black text-white' : 'hover:bg-gray-100'}`}
                            >
                                <span>🗑️</span>
                                <span>({trash.length})</span>
                            </button>
                        </div>
                    </div>
                    <PixelButton onClick={() => navigate('/')} variant="secondary">
                        返回主選單
                    </PixelButton>
                </div>

                {/* Loading State */}
                {isLoading && (
                    <PixelCard className="bg-white text-center py-8">
                        <p className="text-xl">載入中...</p>
                    </PixelCard>
                )}

                {/* Error State */}
                {error && !isLoading && (
                    <PixelCard className="bg-red-100 border-red-500">
                        <p className="text-red-700">{error}</p>
                    </PixelCard>
                )}

                {/* Chart View */}
                {!isLoading && !error && view === 'chart' && (
                    <ScoreTrendChart history={history} />
                )}

                {/* Empty State (Only for list views) */}
                {!isLoading && !error && view !== 'chart' && currentList.length === 0 && (
                    <PixelCard className="bg-white text-center py-12">
                        <div className="text-6xl mb-4">
                            {view === 'active' ? '📊' : '🗑️'}
                        </div>
                        <p className="text-xl mb-4">
                            {view === 'active' ? '尚無歷史記錄' : '回收桶是空的'}
                        </p>
                        {view === 'active' && (
                            <PixelButton onClick={() => navigate('/game/assessment')}>
                                開始評估
                            </PixelButton>
                        )}
                    </PixelCard>
                )}

                {/* Trash Warning Banner */}
                {view === 'trash' && trash.length > 0 && (
                    <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 mb-4" role="alert">
                        <p className="font-bold">注意</p>
                        <p>垃圾桶中的項目將在刪除後的 10 天內自動永久移除。</p>
                    </div>
                )}

                {/* History List */}
                {!isLoading && !error && view !== 'chart' && currentList.length > 0 && (
                    <div className="space-y-4">
                        {currentList.map((record) => {
                            // Calculate days remaining if in trash
                            let daysRemaining = null;
                            if (view === 'trash' && record.deleted_at) {
                                const deleteDate = new Date(record.deleted_at);
                                const expirationDate = new Date(deleteDate);
                                expirationDate.setDate(deleteDate.getDate() + 10);
                                const now = new Date();
                                const diffTime = expirationDate.getTime() - now.getTime();
                                daysRemaining = Math.max(0, Math.ceil(diffTime / (1000 * 60 * 60 * 24)));
                            }

                            // Re-calculate level and color based on current rules
                            // Use backend record.level to ensure correct group threshold is applied
                            const interpretation = getScoreInterpretation(record.total_score, record.level);
                            const displayLevel = interpretation.level;
                            const displayColor = interpretation.color;

                            return (
                                <PixelCard key={record.id} className="bg-white">
                                    <div className="flex items-center justify-between">
                                        <div className="flex-1">
                                            <div className="flex items-center gap-4 mb-2">
                                                <div className={`px-4 py-2 ${displayColor} text-white font-bold border-2 border-black`}>
                                                    {displayLevel}
                                                </div>
                                                <div className="text-sm text-gray-600">
                                                    {formatDate(record.completed_at || '')}
                                                </div>
                                                {view === 'trash' && (
                                                    <>
                                                        <span className="text-xs text-red-500 bg-red-50 px-2 py-1 rounded border border-red-200">
                                                            刪除原因: {record.delete_reason}
                                                        </span>
                                                        {daysRemaining !== null && (
                                                            <span className="text-xs text-orange-600 bg-orange-100 px-2 py-1 rounded border border-orange-200 font-bold">
                                                                剩餘 {daysRemaining} 天
                                                            </span>
                                                        )}
                                                    </>
                                                )}
                                            </div>

                                            <div className="flex items-center gap-6">
                                                <div>
                                                    <span className="text-3xl font-bold text-purple-600">
                                                        {record.total_score}
                                                    </span>
                                                    <span className="text-gray-600"> / {record.max_score}</span>
                                                </div>

                                                <div className="flex-1 h-8 bg-gray-300 border-2 border-black relative overflow-hidden max-w-md">
                                                    <div
                                                        className={`h-full ${displayColor} transition-all`}
                                                        style={{ width: `${record.percentage}%` }}
                                                    >
                                                        <div className="h-full w-full bg-[repeating-linear-gradient(90deg,transparent,transparent_4px,rgba(0,0,0,0.1)_4px,rgba(0,0,0,0.1)_8px)]"></div>
                                                    </div>
                                                    <div className="absolute inset-0 flex items-center justify-center text-sm font-bold">
                                                        {record.percentage}%
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        <div className="flex flex-col gap-2 ml-4">
                                            {view === 'active' ? (
                                                <PixelButton
                                                    onClick={() => handleDeleteClick(record.id)}
                                                    variant="danger"
                                                    size="sm"
                                                >
                                                    刪除
                                                </PixelButton>
                                            ) : (
                                                <>
                                                    <PixelButton
                                                        onClick={() => handleRestore(record.id)}
                                                        variant="primary"
                                                        size="sm"
                                                    >
                                                        還原
                                                    </PixelButton>
                                                    <PixelButton
                                                        onClick={() => handleDeleteClick(record.id, true)}
                                                        variant="secondary" // Use secondary for permanent delete visually to distinguish? Or danger? Let's use danger but clarify text
                                                        className="bg-red-900 text-white hover:bg-red-800"
                                                        size="sm"
                                                    >
                                                        永久刪除
                                                    </PixelButton>
                                                </>
                                            )}
                                        </div>
                                    </div>
                                </PixelCard>
                            );
                        })}
                    </div>
                )}
            </div>

            <DeleteReasonModal
                isOpen={deleteModalOpen}
                onClose={() => setDeleteModalOpen(false)}
                onConfirm={handleConfirmDelete}
                isPermanent={isPermanentDelete}
            />
        </div>
    );
};
