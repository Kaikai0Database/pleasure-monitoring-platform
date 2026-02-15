import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { PixelCard } from '../components/ui/PixelCard';
import { PixelButton } from '../components/ui/PixelButton';

export const ConsentPage: React.FC = () => {
    const [hasAgreed, setHasAgreed] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const navigate = useNavigate();
    const { user, refreshUser } = useAuth();

    // Redirect if already consented
    React.useEffect(() => {
        if (user?.has_consented) {
            navigate('/profile-setup');
        }
    }, [user, navigate]);

    const handleSubmit = async () => {
        if (!hasAgreed) return;

        setIsSubmitting(true);
        try {
            // Call API to record consent
            const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';
            const response = await fetch(`${API_BASE_URL}/auth/consent`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'ngrok-skip-browser-warning': 'true'
                }
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.message || '提交失敗');
            }

            // Refresh user data to get updated consent status
            await refreshUser();

            // Navigate to profile setup
            navigate('/profile-setup');
        } catch (error) {
            console.error('提交同意失敗:', error);
            alert('提交失敗，請稍後再試');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-yellow-100 to-orange-100 py-10 px-4">
            <div className="max-w-3xl mx-auto">
                <PixelCard className="bg-white">
                    {/* Title */}
                    <h2 className="text-2xl font-bold mb-6 text-center">
                        失樂感數位監測平台使用同意書
                    </h2>

                    {/* Scrollable Content Area */}
                    <div
                        className="border-4 border-black p-6 mb-6 overflow-y-auto bg-gray-50"
                        style={{ maxHeight: '400px', minHeight: '300px' }}
                    >
                        <div className="space-y-4 text-sm leading-relaxed">
                            <p>
                                本數位監測平台為研究團隊依人體試驗委員會核准之研究計畫所建置，目的在於蒐集與分析個人情緒與失樂感相關之變化趨勢資料，並運用移動平均線等統計方法進行學術研究分析。
                            </p>

                            <p>
                                因研究執行與資料管理之需要，本平台採用註冊機制，以利研究期間之追蹤、資料完整性確認與必要之研究聯繫；惟所有蒐集之資料於分析過程中，將以研究編碼取代個人身分識別資訊，並以加密方式儲存與處理。
                            </p>

                            <p>
                                研究團隊僅於研究管理與必要之資料比對時，得依權限接觸可識別資訊；實際進行分析與結果呈現時，均以個人資料之趨勢變化為主，不涉及個別身分之揭露或辨識。所有資料僅限本研究之學術用途，不會提供予任何非研究相關之第三方或對外揭露。
                            </p>

                            <p>
                                本平台之使用不影響您於原受訪者同意書中所載之各項權益，相關資料之蒐集、處理與保存，均依該同意書及相關法規辦理。
                            </p>
                        </div>
                    </div>

                    {/* Checkbox */}
                    <div className="mb-6">
                        <label
                            className="flex items-start gap-3 cursor-pointer select-none p-4 border-2 border-gray-300 hover:border-black transition-colors"
                            onClick={() => setHasAgreed(!hasAgreed)}
                        >
                            <div
                                className={`w-6 h-6 border-4 border-black flex items-center justify-center flex-shrink-0 ${hasAgreed ? 'bg-black' : 'bg-white'
                                    }`}
                            >
                                {hasAgreed && (
                                    <span className="text-white text-xl leading-none">✓</span>
                                )}
                            </div>
                            <span className="text-base font-bold">
                                我已閱讀並同意上述說明
                            </span>
                        </label>
                    </div>

                    {/* Next Button */}
                    <PixelButton
                        onClick={handleSubmit}
                        disabled={!hasAgreed || isSubmitting}
                        className="w-full"
                    >
                        {isSubmitting ? '處理中...' : '下一步'}
                    </PixelButton>
                </PixelCard>
            </div>
        </div>
    );
};
