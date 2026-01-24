import React, { useEffect, useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { PlayerInfo } from '../components/PlayerInfo';
import { MenuCard } from '../components/ui/MenuCard';
import { AlertModal } from '../components/AlertModal';
import { alertsApi } from '../services/api';
import type { ScoreAlert } from '../types/api';

export const GameMenu: React.FC = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [highAlertCount, setHighAlertCount] = useState(0);
    const [lowAlertCount, setLowAlertCount] = useState(0);
    const [highAlerts, setHighAlerts] = useState<ScoreAlert[]>([]);
    const [lowAlerts, setLowAlerts] = useState<ScoreAlert[]>([]);
    const [showAlertModal, setShowAlertModal] = useState(false);
    const [activeAlertType, setActiveAlertType] = useState<'high' | 'low'>('high');
    const [hasShownOnLogin, setHasShownOnLogin] = useState(false);

    // Load unread alerts
    useEffect(() => {
        if (!user) return; // Skip if not logged in
        loadAlerts();
    }, [user]);

    // Auto-show alerts on first visit after login (prioritize high alerts)
    useEffect(() => {
        if (!hasShownOnLogin && (highAlerts.length > 0 || lowAlerts.length > 0)) {
            // Show high alerts first if available, otherwise low alerts
            setActiveAlertType(highAlerts.length > 0 ? 'high' : 'low');
            setShowAlertModal(true);
            setHasShownOnLogin(true);
        }
    }, [highAlerts, lowAlerts, hasShownOnLogin]);

    // Early return after all hooks
    if (!user) {
        return <Navigate to="/login" replace />;
    }

    const loadAlerts = async () => {
        try {
            const alertsRes = await alertsApi.getAlerts();

            if (alertsRes.success && alertsRes.alerts) {
                const unread = alertsRes.alerts.filter(a => !a.is_read);

                // Separate high and low alerts
                const high = unread.filter(a => a.alert_type === 'high');
                const low = unread.filter(a => a.alert_type === 'low');

                setHighAlerts(high);
                setLowAlerts(low);
                setHighAlertCount(high.length);
                setLowAlertCount(low.length);
            }
        } catch (error) {
            console.error('Failed to load alerts:', error);
        }
    };

    const handleCloseAlert = () => {
        // Simply close the modal without marking alerts as read
        // Alerts will persist until the next assessment shows improved scores
        // The backend will automatically delete alerts when conditions are no longer met
        setShowAlertModal(false);
    };

    const handleHighAlertClick = () => {
        setActiveAlertType('high');
        setShowAlertModal(true);
    };

    const handleLowAlertClick = () => {
        setActiveAlertType('low');
        setShowAlertModal(true);
    };

    const menuItems = [
        {
            title: '開始遊戲',
            description: '進行失樂感評估測驗',
            icon: '🎮',
            onClick: () => {
                navigate('/game/assessment');
            },
        },
        {
            title: '寫日記',
            description: '記錄今天的心情',
            icon: '📝',
            onClick: () => {
                navigate('/diary');
            },
        },
        {
            title: '分數歷史',
            description: '查看過往測驗結果',
            icon: '📊',
            onClick: () => {
                navigate('/history');
            },
        },
        {
            title: '設定',
            description: '個人資料與偏好設定',
            icon: '⚙️',
            onClick: () => {
                navigate('/settings');
            },
        },
    ];

    return (
        <div className="min-h-[calc(100vh-100px)] py-8">
            <div className="max-w-7xl mx-auto space-y-8">
                {/* Page Title with Alert Bell */}
                <div className="text-center relative">
                    <h1 className="text-4xl font-bold mb-2 inline-block">主選單</h1>

                    {/* Alert Icons Container */}
                    <div className="absolute top-0 right-8 flex gap-3">
                        {/* High Score Alert Bell - Only show when there are unread high alerts */}
                        {highAlertCount > 0 && (
                            <button
                                onClick={handleHighAlertClick}
                                className="bg-white border-4 border-red-600 rounded-lg p-3 hover:bg-red-50 transition-all transform hover:scale-110 relative"
                                title={`${highAlertCount} 個高分警告 (超越移動平均線)`}
                            >
                                <span className="text-3xl">🔔</span>
                                <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center border-2 border-white">
                                    {highAlertCount}
                                </span>
                            </button>
                        )}

                        {/* Low Score Alert Icon - Only show when there are unread low alerts */}
                        {lowAlertCount > 0 && (
                            <button
                                onClick={handleLowAlertClick}
                                className="bg-white border-4 border-blue-600 rounded-lg p-3 hover:bg-blue-50 transition-all transform hover:scale-110 relative"
                                title={`${lowAlertCount} 個低分警告 (接近移動平均線)`}
                            >
                                <span className="text-3xl">📉</span>
                                <span className="absolute -top-2 -right-2 bg-blue-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center border-2 border-white">
                                    {lowAlertCount}
                                </span>
                            </button>
                        )}
                    </div>

                    <p className="text-lg opacity-80">選擇您想要進行的活動</p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
                    {/* Left Column - Player Info (2 columns width) */}
                    <div className="lg:col-span-2">
                        <PlayerInfo />
                    </div>

                    {/* Right Column - Menu Grid (3 columns width) */}
                    <div className="lg:col-span-3">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {menuItems.map((item, index) => (
                                <MenuCard
                                    key={index}
                                    title={item.title}
                                    description={item.description}
                                    icon={item.icon}
                                    onClick={item.onClick}
                                />
                            ))}
                        </div>
                    </div>
                </div>

                {/* Additional Info Section */}
                <div className="mt-8 p-6 bg-yellow-100 border-4 border-yellow-600">
                    <div className="flex items-start space-x-4">
                        <div className="text-3xl">💡</div>
                        <div>
                            <h3 className="font-bold text-lg mb-1">每日提醒</h3>
                            <p className="text-sm opacity-90">
                                記得每天花幾分鐘記錄心情，持續追蹤能幫助您更了解自己的情緒變化！
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Alert Modal */}
            {showAlertModal && (
                <AlertModal
                    alerts={activeAlertType === 'high' ? highAlerts : lowAlerts}
                    alertType={activeAlertType}
                    onClose={handleCloseAlert}
                />
            )}
        </div>
    );
};

