import React from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useMusicPlayer } from '../components/BackgroundMusic';
import { useFontSize } from '../context/FontSizeContext';
import { PixelCard } from '../components/ui/PixelCard';
import { PixelButton } from '../components/ui/PixelButton';

export const Settings: React.FC = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const { isPlaying, volume, isMuted, toggle, setVolume, toggleMute } = useMusicPlayer();
    const { fontSize, setFontSize, fontSizeLabel, fontSizePixels } = useFontSize();

    if (!user) {
        return <Navigate to="/login" replace />;
    }

    return (
        <div className="min-h-[calc(100vh-100px)] py-8">
            <div className="max-w-4xl mx-auto space-y-8">
                {/* Page Title */}
                <div className="text-center">
                    <h1 className="text-4xl font-bold mb-2">設定</h1>
                    <p className="text-lg opacity-80">個人資料與偏好設定</p>
                </div>

                {/* User Profile Section */}
                {/* User Profile Section */}
                <PixelCard className="bg-gradient-to-br from-blue-50 to-purple-50">
                    <div className="flex justify-between items-center mb-4 border-b-4 border-black pb-2">
                        <h2 className="text-2xl font-bold">個人資料</h2>
                        {!user.is_profile_completed && (<PixelButton onClick={() => navigate('/profile-setup')} size="sm" variant="secondary">
                            編輯資料
                        </PixelButton>)}
                    </div>

                    <div className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <h3 className="font-bold text-gray-500 mb-2">基本資訊</h3>
                                <div className="space-y-1">
                                    <div className="flex justify-between border-b border-gray-200 pb-1">
                                        <span>姓名</span>
                                        <span className="font-bold">{user.name}</span>
                                    </div>
                                    <div className="flex justify-between border-b border-gray-200 pb-1">
                                        <span>您來自哪裡</span>
                                        <span className="font-bold">
                                            {user.group === 'student' ? '學校' : user.group === 'clinical' ? '醫院' : '未填寫'}
                                        </span>
                                    </div>
                                    <div className="flex justify-between border-b border-gray-200 pb-1">
                                        <span>暱稱</span>
                                        <span className="font-bold">{user.nickname || '-'}</span>
                                    </div>
                                    <div className="flex justify-between border-b border-gray-200 pb-1">
                                        <span>Email</span>
                                        <span className="font-bold">{user.email}</span>
                                    </div>
                                    <div className="flex justify-between border-b border-gray-200 pb-1">
                                        <span>生日</span>
                                        <span className="font-bold">{user.dob || '-'}</span>
                                    </div>
                                    <div className="flex justify-between border-b border-gray-200 pb-1">
                                        <span>性別</span>
                                        <span className="font-bold">{user.gender || '-'}</span>
                                    </div>
                                </div>
                            </div>

                            <div>
                                <h3 className="font-bold text-gray-500 mb-2">身體數值</h3>
                                <div className="space-y-1">
                                    <div className="flex justify-between border-b border-gray-200 pb-1">
                                        <span>身高</span>
                                        <span className="font-bold">{user.height ? `${user.height} cm` : '-'}</span>
                                    </div>
                                    <div className="flex justify-between border-b border-gray-200 pb-1">
                                        <span>體重</span>
                                        <span className="font-bold">{user.weight ? `${user.weight} kg` : '-'}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                            <div>
                                <h3 className="font-bold text-gray-500 mb-2">社會經濟</h3>
                                <div className="space-y-1">
                                    <div className="flex justify-between border-b border-gray-200 pb-1">
                                        <span>學歷</span>
                                        <span className="font-bold">{user.education || '-'}</span>
                                    </div>
                                    <div className="flex justify-between border-b border-gray-200 pb-1">
                                        <span>婚姻</span>
                                        <span className="font-bold">{user.marital_status === '其他' ? user.marriage_other : (user.marital_status || '-')}</span>
                                    </div>
                                    <div className="flex justify-between border-b border-gray-200 pb-1">
                                        <span>子女</span>
                                        <span className="font-bold">{user.has_children ? `${user.children_count} 人` : '無'}</span>
                                    </div>
                                    <div className="flex justify-between border-b border-gray-200 pb-1">
                                        <span>經濟狀況</span>
                                        <span className="font-bold">{user.economic_status || '-'}</span>
                                    </div>
                                </div>
                            </div>

                            <div>
                                <h3 className="font-bold text-gray-500 mb-2">生活與其他</h3>
                                <div className="space-y-1">
                                    <div className="flex justify-between border-b border-gray-200 pb-1">
                                        <span>工作</span>
                                        <span className="font-bold">{user.has_job ? (user.salary_range || '有') : '無'}</span>
                                    </div>
                                    <div className="flex justify-between border-b border-gray-200 pb-1">
                                        <span>居住地</span>
                                        <span className="font-bold">{user.location_city ? `${user.location_city}${user.location_district}` : '-'}</span>
                                    </div>
                                    <div className="flex justify-between border-b border-gray-200 pb-1">
                                        <span>家庭結構</span>
                                        <span className="font-bold">{user.family_structure === '其他' ? user.family_other : (user.family_structure || '-')}</span>
                                    </div>
                                    <div className="flex justify-between border-b border-gray-200 pb-1">
                                        <span>居住狀況</span>
                                        <span className="font-bold">{user.living_situation || '-'}</span>
                                    </div>
                                    <div className="flex justify-between border-b border-gray-200 pb-1">
                                        <span>宗教信仰</span>
                                        <span className="font-bold">{user.religion ? (user.religion_other || '有') : '無'}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </PixelCard>

                {/* Background Music Settings */}
                <PixelCard className="bg-gradient-to-br from-yellow-50 to-orange-50">
                    <h2 className="text-2xl font-bold mb-4 border-b-4 border-black pb-2">
                        🎵 背景音樂設定
                    </h2>
                    <div className="space-y-6">
                        {/* Play/Pause Control */}
                        <div className="flex justify-between items-center">
                            <div>
                                <div className="font-bold text-lg">播放狀態</div>
                                <div className="text-sm opacity-80">
                                    {isPlaying ? '正在播放' : '已暫停'}
                                </div>
                            </div>
                            <PixelButton
                                onClick={toggle}
                                variant={isPlaying ? 'danger' : 'primary'}
                                className="min-w-[120px]"
                            >
                                {isPlaying ? '⏸ 暫停' : '▶ 播放'}
                            </PixelButton>
                        </div>

                        {/* Volume Control */}
                        <div className="space-y-2">
                            <div className="flex justify-between items-center">
                                <div className="font-bold text-lg">音量</div>
                                <div className="text-sm opacity-80">
                                    {Math.round(volume * 100)}%
                                </div>
                            </div>
                            <div className="relative">
                                <input
                                    type="range"
                                    min="0"
                                    max="100"
                                    value={volume * 100}
                                    onChange={(e) => setVolume(Number(e.target.value) / 100)}
                                    className="w-full h-4 bg-gray-300 border-4 border-black appearance-none cursor-pointer"
                                    style={{
                                        background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${volume * 100}%, #d1d5db ${volume * 100}%, #d1d5db 100%)`
                                    }}
                                />
                            </div>
                        </div>

                        {/* Mute Toggle */}
                        <div className="flex justify-between items-center">
                            <div>
                                <div className="font-bold text-lg">靜音</div>
                                <div className="text-sm opacity-80">
                                    {isMuted ? '已開啟靜音' : '已關閉靜音'}
                                </div>
                            </div>
                            <PixelButton
                                onClick={toggleMute}
                                variant={isMuted ? 'danger' : 'secondary'}
                                className="min-w-[120px]"
                            >
                                {isMuted ? '🔇 取消靜音' : '🔊 靜音'}
                            </PixelButton>
                        </div>
                    </div>
                </PixelCard>

                {/* Font Size Settings */}
                <PixelCard className="bg-gradient-to-br from-green-50 to-teal-50">
                    <h2 className="text-2xl font-bold mb-4 border-b-4 border-black pb-2">
                        📝 字體大小設定
                    </h2>
                    <div className="space-y-6">
                        {/* Current Font Size Display */}
                        <div className="flex justify-between items-center">
                            <div>
                                <div className="font-bold text-lg">當前字體大小</div>
                                <div className="text-sm opacity-80">
                                    {fontSizeLabel} ({fontSizePixels}px)
                                </div>
                            </div>
                        </div>

                        {/* Font Size Buttons */}
                        <div className="space-y-2">
                            <div className="font-bold text-lg mb-3">選擇字體大小</div>
                            <div className="grid grid-cols-2 gap-3">
                                <PixelButton
                                    onClick={() => setFontSize('small')}
                                    variant={fontSize === 'small' ? 'primary' : 'secondary'}
                                >
                                    小 (18px)
                                </PixelButton>
                                <PixelButton
                                    onClick={() => setFontSize('medium')}
                                    variant={fontSize === 'medium' ? 'primary' : 'secondary'}
                                >
                                    中 (22px)
                                </PixelButton>
                                <PixelButton
                                    onClick={() => setFontSize('large')}
                                    variant={fontSize === 'large' ? 'primary' : 'secondary'}
                                >
                                    大 (28px)
                                </PixelButton>
                                <PixelButton
                                    onClick={() => setFontSize('extra-large')}
                                    variant={fontSize === 'extra-large' ? 'primary' : 'secondary'}
                                >
                                    特大 (32px)
                                </PixelButton>
                            </div>
                        </div>

                        {/* Preview Text */}
                        <div className="space-y-2">
                            <div className="font-bold text-lg">預覽</div>
                            <div className="p-4 bg-white border-4 border-black">
                                <p className="mb-2">這是預覽文字，您可以看到字體大小的變化。</p>
                                <p className="text-sm opacity-80">This is a preview text to show font size changes.</p>
                            </div>
                        </div>
                    </div>
                </PixelCard>

                {/* Administrator Info */}
                <PixelCard className="bg-gradient-to-br from-gray-50 to-slate-50">
                    <h2 className="text-2xl font-bold mb-4 border-b-4 border-black pb-2">
                        🛡️ 管理者資訊
                    </h2>
                    <div className="space-y-3">
                        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                            <span className="font-bold">聯絡信箱：</span>
                            <a
                                href="mailto:yuki88720@gmail.com"
                                className="text-blue-600 hover:text-blue-800 underline break-all"
                            >
                                yuki88720@gmail.com
                            </a>
                        </div>
                    </div>
                </PixelCard>

                {/* Info Box */}
                <div className="p-6 bg-blue-100 border-4 border-blue-600">
                    <div className="flex items-start space-x-4">
                        <div className="text-3xl">💡</div>
                        <div>
                            <h3 className="font-bold text-lg mb-1">提示</h3>
                            <p className="text-sm opacity-90">
                                您的偏好設定（音樂與字體大小）會自動保存。下次開啟應用時會記住您的設定。
                            </p>
                        </div>
                    </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-4 justify-center">
                    <PixelButton onClick={() => navigate('/')} variant="secondary">
                        返回主選單
                    </PixelButton>
                </div>
            </div>
        </div>
    );
};
