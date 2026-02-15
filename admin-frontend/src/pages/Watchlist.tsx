import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { watchlistAPI, patientsAPI } from '../services/api';
import { type WatchlistItem } from '../types';
import {
    DndContext,
    closestCenter,
    PointerSensor,
    useSensor,
    useSensors,
    type DragEndEvent,
} from '@dnd-kit/core';
import {
    SortableContext,
    verticalListSortingStrategy,
    useSortable,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import './Watchlist.css';

// Sortable Patient Row Component
function SortablePatientRow({
    item,
    onRemove,
    onViewDetail,
    showGroupBadge,
    alertCount,
}: {
    item: WatchlistItem;
    onRemove: (patientId: number, e: React.MouseEvent) => void;
    onViewDetail: (patientId: number) => void;
    showGroupBadge: boolean;
    alertCount: { high: { count: number; lines: string[] }; low: { count: number; lines: string[] } };
}) {
    const {
        attributes,
        listeners,
        setNodeRef,
        transform,
        transition,
        isDragging,
    } = useSortable({ id: item.patient_id });

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.5 : 1,
    };

    return (
        <div
            ref={setNodeRef}
            style={style}
            className={`patient-row ${isDragging ? 'dragging' : ''}`}
            onClick={() => onViewDetail(item.patient_id)}
            {...attributes}
            {...listeners}
        >
            <div className="patient-info-section">
                <div className="patient-name-email">
                    <div className="patient-name-text">
                        {item.patient?.name} {item.patient?.nickname && <span className="patient-nickname-text">({item.patient.nickname})</span>}
                        {item.patient?.inactive_warning && (
                            <span className="inactive-warning-icon" title="5天未登入">
                                ⚠️
                            </span>
                        )}
                        {alertCount.high.count > 0 && (
                            <span
                                className="alert-bell-icon"
                                title={`穿越${alertCount.high.lines.join('線、')}線`}
                            >
                                🔔
                            </span>
                        )}
                        {alertCount.low.count > 0 && (
                            <span
                                className="alert-low-icon"
                                title={`接近${alertCount.low.lines.join('線、')}線`}
                            >
                                📉
                            </span>
                        )}
                        {showGroupBadge && item.patient?.group && (
                            <span
                                className={`group-badge ${item.patient.group}`}
                                title={item.patient.group === 'student' ? '大學生組（門檻≥24分）' : '臨床組（門檻≥30分）'}
                            >
                                {item.patient.group === 'student' ? '🎓 大學生組' : '🏥 臨床組'}
                            </span>
                        )}
                    </div>
                    <div className="patient-email-text">{item.patient?.email}</div>
                </div>
            </div>

            <div className="patient-score-section">
                {item.latest_assessment && (
                    <>
                        <span className="score-label">最新分數</span>
                        <span className="score-text">
                            {item.latest_assessment.total_score}/{item.latest_assessment.max_score}
                        </span>
                    </>
                )}
                {!item.latest_assessment && (
                    <span className="no-assessment">尚無評估</span>
                )}
            </div>

            <div className="patient-actions">
                <button
                    onClick={(e) => onRemove(item.patient_id, e)}
                    className="watchlist-remove-btn"
                    title="移除特別關注"
                >
                    ✕
                </button>
            </div>
        </div>
    );
}

export default function Watchlist() {
    const navigate = useNavigate();
    const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [groupFilter, setGroupFilter] = useState<'all' | 'student' | 'clinical'>('all');
    const [alertCounts, setAlertCounts] = useState<{
        [key: number]: {
            high: { count: number; lines: string[] };
            low: { count: number; lines: string[] }
        }
    }>({});

    // Configure sensors for drag and drop with delay for long-press
    const sensors = useSensors(
        useSensor(PointerSensor, {
            activationConstraint: {
                delay: 500, // 500ms long-press to activate drag
                tolerance: 5, // Allow 5px movement before cancelling
            },
        })
    );

    useEffect(() => {
        fetchWatchlist();
    }, []);

    const fetchWatchlist = async () => {
        try {
            setLoading(true);
            const [watchlistRes, alertCountsRes] = await Promise.all([
                watchlistAPI.getAll(),
                patientsAPI.getAlertCounts(),
            ]);
            if (watchlistRes.data.success) {
                setWatchlist(watchlistRes.data.watchlist);
            }
            if (alertCountsRes.data.success) {
                setAlertCounts(alertCountsRes.data.alert_counts || {});
            }
        } catch (err: any) {
            setError(err.response?.data?.message || '獲取特別關注列表失敗');
        } finally {
            setLoading(false);
        }
    };

    const handleDragEnd = async (event: DragEndEvent) => {
        const { active, over } = event;

        if (!over || active.id === over.id) {
            return;
        }

        const oldIndex = watchlist.findIndex((item) => item.patient_id === active.id);
        const newIndex = watchlist.findIndex((item) => item.patient_id === over.id);

        if (oldIndex === -1 || newIndex === -1) {
            return;
        }

        // Reorder the list locally
        const reorderedList = [...watchlist];
        const [movedItem] = reorderedList.splice(oldIndex, 1);
        reorderedList.splice(newIndex, 0, movedItem);

        // Update display_order based on new positions (higher index = higher display_order)
        const orderData = reorderedList.map((item, index) => ({
            patient_id: item.patient_id,
            display_order: reorderedList.length - index, // Reverse so first item has highest order
        }));

        // Optimistically update the UI
        setWatchlist(reorderedList);

        // Send to backend
        try {
            await watchlistAPI.reorder(orderData);
        } catch (err: any) {
            console.error('Reorder failed:', err);
            alert('更新順序失敗，請重新整理頁面');
            // Revert to original order on error
            fetchWatchlist();
        }
    };

    const handleRemove = async (patientId: number, e: React.MouseEvent) => {
        e.stopPropagation(); // 防止觸發個案卡片點擊

        console.log('Attempting to remove patient:', patientId);

        if (!confirm('確定要從特別關注中移除此個案嗎？')) {
            console.log('User cancelled removal');
            return;
        }

        try {
            console.log('Calling watchlist remove API for patient:', patientId);
            const response = await watchlistAPI.remove(patientId);
            console.log('Remove API response:', response);

            // Filter out the removed patient
            const updatedList = watchlist.filter((item) => item.patient_id !== patientId);
            console.log('Updated watchlist:', updatedList);
            setWatchlist(updatedList);

            alert('已從特別關注移除');
        } catch (err: any) {
            console.error('Remove failed:', err);
            alert(err.response?.data?.message || '移除失敗: ' + (err.message || '未知錯誤'));
        }
    };

    const viewPatientDetail = (patientId: number) => {
        navigate(`/patient/${patientId}`);
    };

    // Filter watchlist based on selected group
    const filteredWatchlist = watchlist.filter(item => {
        if (groupFilter === 'all') return true;
        return item.patient?.group === groupFilter;
    });

    const getFilterLabel = () => {
        switch (groupFilter) {
            case 'student': return '大學生組';
            case 'clinical': return '臨床組';
            default: return '特別關注個案';
        }
    };

    if (loading) {
        return (
            <div className="watchlist-loading">
                <div className="spinner"></div>
                <p>載入中...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="watchlist-error">
                <p>❌ {error}</p>
                <button onClick={fetchWatchlist} className="retry-button">
                    重試
                </button>
            </div>
        );
    }

    return (
        <div className="watchlist-container">
            <div className="page-header">
                <h2 className="page-title">特別關注個案總覽</h2>
                <div className="header-controls">
                    <select
                        className="group-filter-select"
                        value={groupFilter}
                        onChange={(e) => setGroupFilter(e.target.value as 'all' | 'student' | 'clinical')}
                    >
                        <option value="all">總覽</option>
                        <option value="clinical">🏥 臨床組</option>
                        <option value="student">🎓 大學生組</option>
                    </select>
                </div>
            </div>
            <div className="watchlist-count">共 {filteredWatchlist.length} 位個案</div>

            {
                filteredWatchlist.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-icon">⭐</div>
                        <p className="empty-text">
                            {groupFilter === 'all'
                                ? '尚未添加任何特別關注個案'
                                : `目前${groupFilter === 'student' ? '大學生組' : '臨床組'}沒有特別關注個案`}
                        </p>
                        <p className="empty-hint">您可以在總覽頁面添加特別關注</p>
                    </div>
                ) : (
                    <div className="watchlist-patients-section">
                        <DndContext
                            sensors={sensors}
                            collisionDetection={closestCenter}
                            onDragEnd={handleDragEnd}
                        >
                            <SortableContext
                                items={filteredWatchlist.map((item) => item.patient_id)}
                                strategy={verticalListSortingStrategy}
                            >
                                <div className="patients-table">
                                    {filteredWatchlist.map((item) => (
                                        <SortablePatientRow
                                            key={item.patient_id}
                                            item={item}
                                            onRemove={handleRemove}
                                            onViewDetail={viewPatientDetail}
                                            showGroupBadge={groupFilter === 'all'}
                                            alertCount={alertCounts[item.patient_id] || { high: { count: 0, lines: [] }, low: { count: 0, lines: [] } }}
                                        />
                                    ))}
                                </div>
                            </SortableContext>
                        </DndContext>
                    </div>
                )
            }
        </div >
    );
}
