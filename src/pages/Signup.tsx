import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { PixelCard } from '../components/ui/PixelCard';
import { PixelInput } from '../components/ui/PixelInput';
import { PixelButton } from '../components/ui/PixelButton';

export const Signup: React.FC = () => {
    const [email, setEmail] = useState('');
    const [name, setName] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const { signup } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (password !== confirmPassword) {
            setError('兩次輸入的密碼不一致');
            return;
        }

        setIsLoading(true);

        try {
            await signup(email, name, password);
            navigate('/consent');
        } catch (err) {
            setError('註冊失敗，此電子郵件可能已被使用');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex min-h-[calc(100vh-150px)] py-10 px-4">
            <PixelCard className="w-full max-w-md m-auto">
                <h2 className="text-2xl font-bold mb-6 text-center">建立新帳號</h2>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block mb-2 text-sm">玩家名稱</label>
                        <PixelInput
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="請輸入玩家名稱"
                            required
                        />
                    </div>
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
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="請輸入密碼"
                            required
                        />
                    </div>
                    <div>
                        <label className="block mb-2 text-sm">確認密碼</label>
                        <PixelInput
                            type="password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            placeholder="請再次輸入密碼"
                            required
                        />
                    </div>
                    {error && (
                        <div className="bg-red-100 border-2 border-red-500 text-red-700 px-4 py-2 text-sm">
                            {error}
                        </div>
                    )}
                    <PixelButton type="submit" className="w-full mt-4" disabled={isLoading}>
                        {isLoading ? '載入中...' : '建立帳號'}
                    </PixelButton>
                </form>
                <p className="mt-4 text-center text-sm">
                    已經有帳號了嗎？{' '}
                    <Link to="/login" className="text-blue-600 hover:underline">
                        登入
                    </Link>
                </p>
            </PixelCard>
        </div>
    );
};
