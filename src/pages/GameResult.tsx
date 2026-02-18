import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { PixelCard } from '../components/ui/PixelCard';
import { PixelButton } from '../components/ui/PixelButton';
import { type Answer, calculateScore, getScoreInterpretation } from '../data/questions';
import { historyApi } from '../services/api';
import { Footer } from '../components/Footer';
import { incrementDailyActivity, calculateCompoundXP, addXP, setAssessmentCooldown } from '../utils/gamification';

export const GameResult: React.FC = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const answers = location.state?.answers as Answer[] | undefined;
    const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
    const [xpBonusInfo, setXpBonusInfo] = useState<{
        xp: number;
        bonusText: string[];
        totalMultiplier: number;
    } | null>(null);

    const { user } = useAuth(); // Get user to check group

    if (!answers || answers.length === 0) {
        return <Navigate to="/" replace />;
    }

    const totalScore = calculateScore(answers);
    const maxScore = answers.length * 4; // Maximum possible score

    // Determine level locally based on user group for immediate display
    let localLevel = '良好';
    if (user?.group === 'student') {
        // 學生組：分數 >= 24 為需要關注
        localLevel = totalScore >= 24 ? '需要關注' : '良好';
        console.log(`📊 [學生組] 分數: ${totalScore}, 切截點: 24, 判定: ${localLevel}`);
    } else {
        // 臨床組（Clinical）或預設：分數 >= 30 為需要關注
        localLevel = totalScore >= 30 ? '需要關注' : '良好';
        console.log(`📊 [臨床組] 分數: ${totalScore}, 切截點: 30, 判定: ${localLevel}`);
    }
    console.log(`👤 用戶組別: ${user?.group || 'undefined'}, 用戶名稱: ${user?.name}`);

    const interpretation = getScoreInterpretation(totalScore, localLevel);
    const percentage = Math.round((totalScore / maxScore) * 100);

    const hasSaved = React.useRef(false);

    // Auto-save assessment result
    useEffect(() => {
        if (hasSaved.current) return;
        hasSaved.current = true;

        const saveAssessment = async () => {
            setSaveStatus('saving');
            try {
                await historyApi.saveHistory({
                    total_score: totalScore,
                    max_score: maxScore,
                    level: interpretation.level,
                    answers: answers.map((a, index) => ({
                        questionId: index + 1,
                        emoji: a.emoji,
                        score: a.score,
                    })),
                });
                setSaveStatus('saved');

                // ===== 遊戲化邏輯：XP 獎勵與冷卻 =====
                try {
                    // 確保有用戶 ID 才執行遊戲化邏輯
                    if (user?.id) {
                        // 1. 遞增每日活動次數（用戶專屬）
                        const activityCount = incrementDailyActivity(user.id);

                        // 2. 獲取連續天數（從user物件，由後端API提供）
                        const streak = user.consecutive_days || 0;

                        // 3. 計算複方XP獎勵（基礎50 × 當日加成 × 連續加成）
                        const xpReward = calculateCompoundXP(activityCount, streak);

                        // 存儲XP獎勵信息用於UI顯示
                        setXpBonusInfo({
                            xp: xpReward.xp,
                            bonusText: xpReward.bonusText,
                            totalMultiplier: xpReward.totalMultiplier
                        });

                        // 4. 增加 XP 並處理升級（用戶專屬）
                        const result = addXP(xpReward.xp, user.id);

                        // 5. 設定 5 小時冷卻（用戶專屬）
                        console.assert(!!user?.id, "CRITICAL: No UserID found during cooldown save!");
                        setAssessmentCooldown(user.id);

                        // 6. 觸發 PlayerInfo 即時更新
                        window.dispatchEvent(new Event('gamificationUpdated'));

                        // Console 輸出（開發用）
                        console.log(`✨ 測驗完成獎勵：+${xpReward.xp} XP (基礎${xpReward.baseXP} × ${xpReward.totalMultiplier})`);
                        console.log(`   當日第${activityCount}次 (${xpReward.dailyMultiplier}x) × 連續${streak}天 (${xpReward.streakMultiplier}x)`);
                        console.log(`   當前等級：${result.level} | XP：${result.xp}`);

                        if (xpReward.bonusText.length > 0) {
                            console.log(`🎊 獲得加成: ${xpReward.bonusText.join(' + ')}`);
                        }

                        if (result.leveledUp) {
                            console.log('🎉 恭喜升級！');
                        }
                    } else {
                        console.warn('無法獲取用戶 ID，跳過遊戲化邏輯');
                    }
                } catch (gamificationError) {
                    console.error('Gamification logic error:', gamificationError);
                    // 不阻斷測驗保存流程，僅記錄錯誤
                }
            } catch (error) {
                console.error('Failed to save assessment:', error);
                setSaveStatus('error');
                // Reset hasSaved on error to allow retry if component re-mounts or logic changes
                hasSaved.current = false;
            }
        };

        saveAssessment();
    }, []); // Run once on mount

    return (
        <div className="fixed inset-0 bg-gradient-to-br from-purple-100 to-blue-100 p-8 flex items-center justify-center overflow-y-auto">
            <div className="max-w-3xl w-full space-y-6 my-auto">
                {/* Title */}
                <h1 className="text-4xl font-bold text-center mb-8">評估結果</h1>

                {/* Save Status */}
                {saveStatus === 'saving' && (
                    <div className="bg-blue-100 border-2 border-blue-500 text-blue-700 px-4 py-2 text-sm text-center mb-4">
                        正在保存結果...
                    </div>
                )}
                {saveStatus === 'saved' && (
                    <div className="bg-green-100 border-2 border-green-500 text-green-700 px-4 py-2 text-sm text-center mb-4">
                        ✓ 結果已保存到您的歷史記錄
                    </div>
                )}
                {saveStatus === 'error' && (
                    <div className="bg-red-100 border-2 border-red-500 text-red-700 px-4 py-2 text-sm text-center mb-4">
                        保存失敗，請稍後再試
                    </div>
                )}

                {/* Score Card */}
                <PixelCard className="bg-white">
                    <div className="text-center space-y-6">
                        {/* Score Display */}
                        <div className="space-y-2">
                            <div className="text-6xl font-bold text-purple-600">
                                {totalScore}
                            </div>
                            <div className="text-xl opacity-80">
                                總分 / {maxScore}
                            </div>
                        </div>

                        {/* Percentage Bar */}
                        <div className="w-full h-12 bg-gray-300 border-4 border-black relative overflow-hidden">
                            <div
                                className={`h-full ${interpretation.color} transition-all duration-1000`}
                                style={{ width: `${percentage}%` }}
                            >
                                <div className="h-full w-full bg-[repeating-linear-gradient(90deg,transparent,transparent_4px,rgba(0,0,0,0.1)_4px,rgba(0,0,0,0.1)_8px)]"></div>
                            </div>
                            <div className="absolute inset-0 flex items-center justify-center text-2xl font-bold">
                                {percentage}%
                            </div>
                        </div>

                        {/* Level Badge */}
                        <div className={`inline-block px-8 py-4 ${interpretation.color} border-4 border-black text-white text-2xl font-bold`}>
                            {interpretation.level}
                        </div>
                    </div>
                </PixelCard>

                {/* Interpretation Message */}
                <PixelCard className="bg-gradient-to-br from-yellow-50 to-orange-50">
                    <div className="flex items-start gap-4">
                        <div className="text-4xl">💡</div>
                        <div>
                            <h3 className="text-xl font-bold mb-3">評估說明</h3>
                            <p className="text-lg leading-relaxed opacity-90">
                                {interpretation.message}
                            </p>
                        </div>
                    </div>
                </PixelCard>

                {/* Answer Summary */}
                <PixelCard className="bg-white">
                    <h3 className="text-xl font-bold mb-4">您的回答</h3>
                    <div className="grid grid-cols-7 gap-2">
                        {answers.map((answer, index) => (
                            <div
                                key={index}
                                className="text-center p-2 bg-gray-100 border-2 border-black"
                                title={`問題 ${index + 1}`}
                            >
                                <div className="text-2xl">{answer.emoji}</div>
                                <div className="text-xs mt-1">{answer.score}分</div>
                            </div>
                        ))}
                    </div>
                </PixelCard>

                {/* XP Bonus Display */}
                {xpBonusInfo && xpBonusInfo.bonusText.length > 0 && (
                    <PixelCard className="bg-gradient-to-br from-yellow-100 to-orange-100">
                        <div className="text-center space-y-3">
                            <div className="text-xl font-bold text-purple-800">
                                🎊 獲得經驗值加成！
                            </div>
                            <div className="text-3xl font-bold text-orange-600">
                                +{xpBonusInfo.xp} XP
                            </div>
                            <div className="flex flex-wrap gap-2 justify-center">
                                {xpBonusInfo.bonusText.map((text: string, index: number) => (
                                    <div
                                        key={index}
                                        className="px-4 py-2 bg-gradient-to-r from-yellow-400 to-orange-400 border-4 border-black text-black font-bold text-sm shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all"
                                        style={{
                                            textShadow: '1px 1px 0px rgba(255,255,255,0.5)',
                                            fontFamily: '"Press Start 2P", monospace'
                                        }}
                                    >
                                        {text}
                                    </div>
                                ))}
                            </div>
                            {xpBonusInfo.totalMultiplier > 1 && (
                                <div className="text-sm text-purple-700 font-semibold">
                                    基礎 50 XP × {xpBonusInfo.totalMultiplier} 倍加成
                                </div>
                            )}
                        </div>
                    </PixelCard>
                )}

                {/* Action Buttons */}
                <div className="flex gap-4 justify-center">
                    <PixelButton onClick={() => navigate('/game/assessment')}>
                        重新測驗
                    </PixelButton>
                    <PixelButton onClick={() => navigate('/')} variant="secondary">
                        返回主選單
                    </PixelButton>
                </div>

                <div className="mt-8">
                    <Footer />
                </div>
            </div>
        </div>
    );
};
