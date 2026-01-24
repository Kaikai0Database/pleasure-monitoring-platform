import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { PixelCard } from '../components/ui/PixelCard';
import { PixelButton } from '../components/ui/PixelButton';
import { type Answer, calculateScore, getScoreInterpretation } from '../data/questions';
import { historyApi } from '../services/api';
import { Footer } from '../components/Footer';

export const GameResult: React.FC = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const answers = location.state?.answers as Answer[] | undefined;
    const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');

    const { user } = useAuth(); // Get user to check group

    if (!answers || answers.length === 0) {
        return <Navigate to="/" replace />;
    }

    const totalScore = calculateScore(answers);
    const maxScore = answers.length * 4; // Maximum possible score

    // Determine level locally based on user group for immediate display
    let localLevel = '良好';
    if (user?.group === 'student') {
        localLevel = totalScore >= 24 ? '需要關注' : '良好';
    } else {
        // Clinical or default
        localLevel = totalScore >= 29 ? '需要關注' : '良好';
    }

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
