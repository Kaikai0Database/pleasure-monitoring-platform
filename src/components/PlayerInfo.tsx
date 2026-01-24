import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { PixelCard } from './ui/PixelCard';
import { PixelButton } from './ui/PixelButton';
import { historyApi } from '../services/api';
import { diaryService } from '../services/diaryService';

export const PlayerInfo: React.FC = () => {
    const { user, logout } = useAuth();
    const [gameCount, setGameCount] = useState(0);
    const [diaryCount, setDiaryCount] = useState(0);

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

    if (!user) return null;

    const level = 5;
    const currentXP = 350;
    const maxXP = 500;
    const xpPercentage = (currentXP / maxXP) * 100;

    return (
        <PixelCard className="bg-gradient-to-br from-blue-50 to-purple-50">
            <div className="space-y-4">
                {/* Welcome Header */}
                <div className="text-center border-b-4 border-black pb-4">
                    <h2 className="text-2xl font-bold mb-2">歡迎回來！</h2>
                    <p className="text-xl">{user.nickname || user.name}</p>
                </div>

                {/* Level and XP */}
                <div className="space-y-2">
                    <div className="flex justify-between items-center">
                        <span className="text-lg font-bold">等級 {level}</span>
                        <span className="text-sm opacity-80">
                            {currentXP} / {maxXP} XP
                        </span>
                    </div>

                    {/* XP Progress Bar */}
                    <div className="h-8 bg-gray-300 border-4 border-black relative overflow-hidden">
                        <div
                            className="h-full bg-gradient-to-r from-yellow-400 to-orange-500 transition-all duration-500"
                            style={{ width: `${xpPercentage}%` }}
                        >
                            <div className="h-full w-full bg-[repeating-linear-gradient(90deg,transparent,transparent_4px,rgba(0,0,0,0.1)_4px,rgba(0,0,0,0.1)_8px)]"></div>
                        </div>
                    </div>
                </div>

                {/* Quick Stats */}
                <div className="flex gap-1 text-center">
                    <div className="flex-1 bg-white border-2 border-black p-2 min-w-0">
                        <div className="text-2xl font-bold">{gameCount}</div>
                        <div className="text-xs opacity-80 whitespace-nowrap">遊戲次數</div>
                    </div>
                    <div className="flex-1 bg-white border-2 border-black p-2 min-w-0">
                        <div className="text-2xl font-bold">{diaryCount}</div>
                        <div className="text-xs opacity-80 whitespace-nowrap">日記條目</div>
                    </div>
                    <div className="flex-1 bg-white border-2 border-black p-2 min-w-0">
                        <div className="text-2xl font-bold">{user.daily_login_count || 1}</div>
                        <div className="text-xs opacity-80 whitespace-nowrap">今日登入</div>
                    </div>
                </div>

                {/* Logout Button */}
                <PixelButton onClick={logout} variant="danger" className="w-full">
                    登出
                </PixelButton>
            </div>
        </PixelCard>
    );
};
