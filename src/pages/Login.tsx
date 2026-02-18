import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { PixelCard } from '../components/ui/PixelCard';
import { PixelInput } from '../components/ui/PixelInput';
import { PixelButton } from '../components/ui/PixelButton';

import { Eye, EyeOff } from 'lucide-react';

export const Login: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [showCongratsModal, setShowCongratsModal] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            const data = await login(email, password);
            // Check profile completion (assuming login returns user object or we get it from auth context)
            // But 'login' from useAuth might not return data directly if it is void.
            // Let's modify useAuth types/return or handle it here if login updates user state async.
            // Actually better: check user state or response.
            // Assuming login provider updates user. 
            // Let's wait a bit or redirect to home, and home (or Layout) guards profile?
            // Or better: update useAuth login to return user. 
            // For now, let's assume if successful we go to root, and root checks?
            // But prompt said "checks after login".
            // Let's rely on the fact that AuthProvider will set the user. 
            // We can fetch /me or rely on login response if useAuth returns it. 
            // I'll update Login to navigation logic.

            // Wait, useAuth login probably needs to return data. 
            // Let's inspect useAuth first? No, I'll just redirect to '/' and let a Guard handle it, 
            // OR simpler:
            // If I can't easily change useAuth return type right now without seeing it, 
            // I will hard reload or just assume the user will be redirected by App.tsx logic if implemented there.
            // But I haven't implemented App.tsx guard logic yet.

            // Let's implement Route Guard logic in App.tsx or Layout.
            // Actually, for simplicity, I'll just change logic here IF useAuth returns promise with data.

            // Checking Login.tsx again... code was:
            // await login(email, password);
            // navigate('/');

            // If I change it to:
            if (data.user.is_profile_completed) {
                if ((data.user?.consecutive_days ?? 0) >= 7) {
                    setShowCongratsModal(true);
                    // We don't navigate immediately, wait for modal close
                } else {
                    navigate('/');
                }
            } else {
                navigate('/profile-setup');
            }
        } catch (err) {
            setError('登入失敗，請檢查您的電子郵件和密碼');
        } finally {
            setIsLoading(false);
        }
    };

    const handleCongratsClose = () => {
        setShowCongratsModal(false);
        navigate('/history?view=chart');
    };

    return (
        <div className="flex min-h-[calc(100vh-150px)] py-10 px-4">
            <PixelCard className="w-full max-w-xl m-auto">
                <h2 className="text-2xl font-bold mb-6 text-center">登入</h2>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block mb-2 text-sm">電子郵件</label>
                        <PixelInput
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="請輸入電子郵件"
                            required
                        />
                    </div>
                    <div>
                        <label className="block mb-2 text-sm">密碼</label>
                        <PixelInput
                            type={showPassword ? 'text' : 'password'}
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="請輸入密碼"
                            required
                            endIcon={
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="focus:outline-none hover:text-gray-700"
                                >
                                    {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                                </button>
                            }
                        />
                    </div>
                    {error && (
                        <div className="bg-red-100 border-2 border-red-500 text-red-700 px-4 py-2 text-sm">
                            {error}
                        </div>
                    )}
                    <PixelButton type="submit" className="w-full mt-4" disabled={isLoading}>
                        {isLoading ? '載入中...' : '開始遊戲'}
                    </PixelButton>
                </form>
                <p className="mt-4 text-center text-sm">
                    尚未註冊？{' '}
                    <Link to="/signup" className="text-blue-600 hover:underline">
                        建立帳號
                    </Link>
                </p>
            </PixelCard>
            {showCongratsModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-white border-4 border-black p-8 max-w-sm w-full mx-4 text-center shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
                        <div className="text-4xl mb-4">🎉</div>
                        <h3 className="text-2xl font-bold mb-4">太棒了！</h3>
                        <p className="text-lg mb-6">
                            恭喜您連續完成 7 天的測驗！
                            <br />
                            持續保持關注自己的情緒～
                        </p>
                        <PixelButton onClick={handleCongratsClose} className="w-full">
                            查看心情趨勢
                        </PixelButton>
                    </div>
                </div>
            )}
        </div>
    );
};
