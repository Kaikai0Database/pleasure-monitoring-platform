import React, { useEffect, useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { PlayerInfo } from '../components/PlayerInfo';
import { MenuCard } from '../components/ui/MenuCard';
import { AlertModal } from '../components/AlertModal';
import { historyApi } from '../services/api';
import { detectAlerts } from '../utils/alertCalculator';
import type { AlertInfo } from '../types/alert';
import '../styles/game-theme.css';
import '../styles/tutorial.css';
import { getCooldownRemaining } from '../utils/gamification';
import { Tutorial } from '../components/Tutorial/Tutorial';
import { hasTutorialCompleted, markTutorialCompleted } from '../utils/tutorialStorage';

export const GameMenu: React.FC = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [highAlertCount, setHighAlertCount] = useState(0);
    const [lowAlertCount, setLowAlertCount] = useState(0);
    const [highAlert, setHighAlert] = useState<AlertInfo | null>(null);
    const [lowAlert, setLowAlert] = useState<AlertInfo | null>(null);
    const [showAlertModal, setShowAlertModal] = useState(false);
    const [activeAlertType, setActiveAlertType] = useState<'high' | 'low'>('high');
    const [hasShownOnLogin, setHasShownOnLogin] = useState(false);
    const [cooldownRemaining, setCooldownRemaining] = useState(0);

    // Tutorial state
    const [showTutorial, setShowTutorial] = useState(false);
    const [tutorialStep, setTutorialStep] = useState(0);

    // Load and calculate alerts from assessment history
    useEffect(() => {
        if (!user) return;
        loadAndCalculateAlerts();
    }, [user]);

    // Auto-show alerts on first visit after login
    useEffect(() => {
        if (!hasShownOnLogin && (highAlert || lowAlert)) {
            setActiveAlertType(highAlert ? 'high' : 'low');
            setShowAlertModal(true);
            setHasShownOnLogin(true);
        }
    }, [highAlert, lowAlert, hasShownOnLogin]);


    // 監聽冷卻時間，每秒更新（用戶專屬）
    useEffect(() => {
        // 🔒 GATE: 若無 userId，不執行任何冷卻檢查
        if (!user?.id) {
            setCooldownRemaining(0);
            return;
        }

        const updateCooldown = () => {
            // CRITICAL: 傳入 user?.id 確保讀取正確的用戶冷卻數據
            const remaining = getCooldownRemaining(user.id);
            setCooldownRemaining(remaining);
        };

        updateCooldown();  // 初始更新
        const interval = setInterval(updateCooldown, 1000);  // 每秒更新

        return () => clearInterval(interval);
    }, [user?.id]);  // 依賴 user?.id，當用戶變更時重新計算

    // Tutorial: 首次進入檢測
    useEffect(() => {
        if (user?.id && !hasTutorialCompleted(user.id)) {
            // 延遲顯示，確保頁面渲染完成
            const timer = setTimeout(() => {
                setShowTutorial(true);
            }, 500);
            return () => clearTimeout(timer);
        }
    }, [user?.id]);

    // Early return after all hooks
    if (!user) {
        return <Navigate to="/login" replace />;
    }

    const loadAndCalculateAlerts = async () => {
        try {
            // Get assessment history
            const historyRes = await historyApi.getHistory();

            if (historyRes.success && historyRes.history) {
                // Calculate alerts using frontend logic
                const result = detectAlerts(historyRes.history);

                // Update state - only show alerts if assessment count >= 3
                setHighAlert(result.highAlert);
                setLowAlert(result.lowAlert);
                setHighAlertCount(result.highAlert ? 1 : 0);
                setLowAlertCount(result.lowAlert ? 1 : 0);

                console.log('🔔 [GameMenu] Frontend alert calculation:');
                console.log('  High Alert:', result.highAlert ? `${result.highAlert.dailyAverage} (${result.highAlert.assessmentCount} assessments)` : 'None');
                console.log('  Low Alert:', result.lowAlert ? `${result.lowAlert.dailyAverage} (${result.lowAlert.assessmentCount} assessments)` : 'None');
            }
        } catch (error) {
            console.error('❌ [GameMenu] Failed to calculate alerts:', error);
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

    // Tutorial handlers
    const handleTutorialNext = () => {
        setTutorialStep(prev => prev + 1);
    };

    const handleTutorialPrev = () => {
        setTutorialStep(prev => Math.max(0, prev - 1));
    };

    const handleTutorialClose = () => {
        setShowTutorial(false);
        if (user?.id) {
            markTutorialCompleted(user.id);
        }
    };

    // 手動觸發教學（說明按鈕）
    const handleShowHelp = () => {
        setTutorialStep(0);
        setShowTutorial(true);
    };

    // 格式化時間顯示（HH:MM:SS）
    const formatTime = (seconds: number): string => {
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = seconds % 60;
        return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    };

    const menuItems = [
        {
            title: cooldownRemaining > 0 ? `恢復中 (${formatTime(cooldownRemaining)})` : '開啟冒險',
            description: '進行失樂感評估測驗',
            icon: '⚔️',
            onClick: () => {
                if (cooldownRemaining === 0) {
                    navigate('/game/assessment');
                }
            },
            disabled: cooldownRemaining > 0,
        },
        {
            title: '英雄日誌',
            description: '記錄今天的心情',
            icon: '📜',
            onClick: () => {
                navigate('/diary');
            },
        },
        {
            title: '冒險成就',
            description: '查看過往測驗結果',
            icon: '🏆',
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
        <div className="pixel-theme min-h-screen py-8">
            <style>{`
                /* Mobile Responsive Styles */
                @media (max-width: 768px) {
                    /* Title font size reduction */
                    .pixel-title {
                        font-size: 2rem !important; /* 80% of 2.5rem */
                    }
                    
                    .pixel-title + p {
                        font-size: 0.875rem !important; /* Subtitle */
                    }
                    
                    /* Alert icons positioning */
                    .mobile-alert-container {
                        position: relative !important;
                        top: auto !important;
                        right: auto !important;
                        margin-top: 1rem;
                        justify-content: center;
                    }
                    
                    /* Layout stacking */
                    .mobile-stack-layout {
                        display: flex;
                        flex-direction: column;
                        gap: 2rem;
                    }
                    
                    /* Player info card width */
                    .mobile-player-card {
                        width: 100%;
                        max-width: 100%;
                    }
                    
                    /* Menu grid - single column on mobile */
                    .mobile-menu-grid {
                        grid-template-columns: 1fr !important;
                    }
                    
                    /* Reduce padding/margins */
                    .mobile-reduce-spacing {
                        padding-left: 1rem;
                        padding-right: 1rem;
                    }
                }
                
                @media (max-width: 480px) {
                    /* Extra small screens */
                    .pixel-title {
                        font-size: 1.5rem !important;
                    }
                }
            `}</style>

            {/* Tutorial System */}
            <Tutorial
                isActive={showTutorial}
                currentStep={tutorialStep}
                onNext={handleTutorialNext}
                onPrev={handleTutorialPrev}
                onClose={handleTutorialClose}
            />

            {/* Help Button */}
            <button
                onClick={handleShowHelp}
                className="tutorial-help-button"
                title="查看教學"
                aria-label="查看教學"
            >
                ❓
            </button>

            <div className="max-w-7xl mx-auto space-y-8 px-4 mobile-reduce-spacing">
                {/* Page Title with Alert Bell */}
                <div className="text-center relative">
                    <h1 className="pixel-title text-4xl mb-2 inline-block">主選單</h1>

                    {/* Alert Icons Container - Responsive positioning */}
                    <div
                        data-tutorial="alerts"
                        className="absolute top-0 right-8 flex gap-3 mobile-alert-container"
                        style={{ zIndex: 100 }}
                    >
                        {/* High Score Alert Bell - Always vivid and clear */}
                        <button
                            onClick={handleHighAlertClick}
                            className="pixel-alert-bell"
                            style={{
                                animation: highAlertCount > 0 ? 'bounce 2s ease-in-out infinite' : 'none'
                            }}
                            title={highAlertCount > 0 ? `${highAlertCount} 個高分警告 (超越移動平均線)` : '目前無高分警告'}
                        >
                            <span className="text-3xl">🔔</span>
                            {highAlertCount > 0 && (
                                <span className="pixel-alert-badge">
                                    {highAlertCount}
                                </span>
                            )}
                        </button>

                        {/* Low Score Alert - Always vivid and clear */}
                        <button
                            onClick={handleLowAlertClick}
                            className="pixel-alert-bell"
                            style={{
                                boxShadow: '0 0 0 4px #000, 0 0 0 6px #a78bfa, 0 0 0 8px #000, 4px 4px 0 8px rgba(0,0,0,0.3)',
                                animation: lowAlertCount > 0 ? 'bounce 2s ease-in-out infinite' : 'none'
                            }}
                            title={lowAlertCount > 0 ? `${lowAlertCount} 個低分警告 (接近移動平均線)` : '目前無穿線預警'}
                        >
                            <span className="text-3xl">📉</span>
                            {lowAlertCount > 0 && (
                                <span className="pixel-alert-badge" style={{ background: '#3b82f6' }}>
                                    {lowAlertCount}
                                </span>
                            )}
                        </button>
                    </div>

                    <p className="text-lg opacity-90 pixel-text-readable" style={{ color: '#cbd5e0' }}>選擇您想要進行的活動</p>
                </div>

                {/* Responsive Layout Container */}
                <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 mobile-stack-layout">
                    {/* Left Column - Player Info (2 columns width on desktop, full width on mobile) */}
                    <div data-tutorial="player-info" className="lg:col-span-2 mobile-player-card">
                        <PlayerInfo />
                    </div>

                    {/* Right Column - Menu Grid (3 columns width on desktop, full width on mobile) */}
                    <div className="lg:col-span-3">
                        <div data-tutorial="menu-buttons" className="grid grid-cols-1 md:grid-cols-2 gap-6 mobile-menu-grid">
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

                {/* Additional Info Section - Pixel Scroll */}
                <div data-tutorial="daily-mission" className="pixel-scroll mt-8">
                    <div className="flex items-start space-x-4">
                        <div className="text-3xl">💡</div>
                        <div>
                            <h3 className="font-bold text-lg mb-2" style={{ fontFamily: 'Press Start 2P', fontSize: '14px', lineHeight: '1.6' }}>今日任務</h3>
                            <p className="text-sm opacity-90 pixel-text-readable" style={{ fontFamily: 'Arial, sans-serif' }}>
                                記得每天花幾分鐘記錄心情，持續追蹤能幫助您更了解自己的情緒變化！
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Alert Modal */}
            {showAlertModal && (
                <AlertModal
                    alertInfo={activeAlertType === 'high' ? highAlert : lowAlert}
                    alertType={activeAlertType}
                    onClose={handleCloseAlert}
                />
            )}
        </div>
    );
};
