import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { historyApi } from '../services/api';
import { diaryService } from '../services/diaryService';
import { loadGamificationData, calculateRequiredXP } from '../utils/gamification';

export const PlayerInfo: React.FC = () => {
    const { user, logout } = useAuth();
    const [gameCount, setGameCount] = useState(0);
    const [diaryCount, setDiaryCount] = useState(0);
    const [gamificationRefresh, setGamificationRefresh] = useState(0);

    useEffect(() => {
        const fetchStats = async () => {
            if (!user) return;
            try {
                // Fetch Game History Count
                const historyRes = await historyApi.getHistory();
                if (historyRes.success && historyRes.history) {
                    setGameCount(historyRes.history.length);
                }

                // Fetch Diary Count
                const diaries = await diaryService.getAllDiaries();
                if (diaries) {
                    setDiaryCount(diaries.length);
                }
            } catch (error) {
                console.error('Failed to fetch player stats:', error);
            }
        };

        fetchStats();
    }, [user]);

    // 監聽遊戲化數據更新事件
    useEffect(() => {
        const handleGamificationUpdate = () => {
            setGamificationRefresh(prev => prev + 1);

            // Debug: 立即顯示最新數據
            if (user?.id) {
                const data = loadGamificationData(user.id);
                console.log(`🔄 [PlayerInfo 更新] 等級: ${data.level}, XP: ${data.xp}/${calculateRequiredXP(data.level)}`);
            }
        };

        window.addEventListener('gamificationUpdated', handleGamificationUpdate);

        return () => {
            window.removeEventListener('gamificationUpdated', handleGamificationUpdate);
        };
    }, [user?.id]);  // 依賴 user?.id，當用戶變更時重新綁定

    if (!user) return null;

    // 從 localStorage 載入動態等級與 XP 數據（gamificationRefresh 觸發重新計算）
    // 使用用戶 ID 來確保數據隢離
    const { level, xp } = loadGamificationData(user.id);
    const currentXP = xp + (gamificationRefresh * 0);  // 使用 gamificationRefresh 觸發重渲染
    const maxXP = calculateRequiredXP(level);
    const xpPercentage = maxXP > 0 ? (currentXP / maxXP) * 100 : 0;

    return (
        <>
            <style>{`
                /* PlayerInfo Mobile Responsive Styles */
                @media (max-width: 600px) {
                    /* Level and XP container - vertical stacking */
                    .player-level-xp-container {
                        flex-direction: column !important;
                        align-items: flex-start !important;
                        gap: 0.5rem;
                    }
                    
                    /* Level badge alignment */
                    .pixel-level-badge {
                        align-self: flex-start;
                        margin-bottom: 8px;
                    }
                    
                    /* XP text sizing */
                    .player-xp-text {
                        font-size: 0.85rem !important;
                        align-self: flex-start;
                    }
                    
                    /* XP progress bar full width */
                    .pixel-xp-container {
                        width: 100%;
                    }
                }
            `}</style>
            <div className="pixel-player-info">

                <div className="space-y-4">
                    {/* Welcome Header */}
                    <div className="text-center border-b-4 border-black pb-4">
                        <h2 className="text-2xl font-bold mb-2 pixel-text-shadow">歡迎回來！</h2>
                        <p className="text-xl font-bold break-all" style={{ overflowWrap: 'anywhere', wordBreak: 'break-all', maxWidth: '100%' }}>{user.nickname || user.name}</p>
                    </div>

                    {/* Level and XP */}
                    <div className="space-y-3">
                        <div className="flex justify-between items-center player-level-xp-container">
                            <span className="pixel-level-badge">等級 {level}</span>
                            <span className="text-sm font-bold player-xp-text" style={{ fontFamily: 'Press Start 2P', fontSize: '10px' }}>
                                {currentXP} / {maxXP} XP
                            </span>
                        </div>

                        {/* XP Progress Bar */}
                        <div className="pixel-xp-container">
                            <div
                                className="pixel-xp-bar"
                                style={{ width: `${xpPercentage}%` }}
                            >
                            </div>
                        </div>
                    </div>

                    {/* Quick Stats */}
                    <div className="grid grid-cols-3 gap-2">
                        <div className="pixel-stat-box">
                            <div className="pixel-stat-label">遊戲次數</div>
                            <div className="pixel-stat-number">{gameCount}</div>
                        </div>
                        <div className="pixel-stat-box">
                            <div className="pixel-stat-label">日記條目</div>
                            <div className="pixel-stat-number">{diaryCount}</div>
                        </div>
                        <div className="pixel-stat-box">
                            <div className="pixel-stat-label">今日登入</div>
                            <div className="pixel-stat-number">{user.daily_login_count || 1}</div>
                        </div>
                    </div>

                    {/* Logout Button */}
                    <button onClick={logout} className="pixel-button-danger pixel-button w-full">
                        登出
                    </button>
                </div>
            </div>
        </>
    );
};

