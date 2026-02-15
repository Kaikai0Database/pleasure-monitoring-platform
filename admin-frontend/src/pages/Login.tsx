import { useState } from 'react';
import { Link } from 'react-router-dom';
import { authAPI } from '../services/api';
import './Login.css';

export default function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const response = await authAPI.login(email, password);
            if (response.data.success) {
                localStorage.setItem('admin_token', response.data.access_token);
                localStorage.setItem('admin_staff', JSON.stringify(response.data.staff));
                window.location.href = '/dashboard';
            } else {
                setError(response.data.message || '登入失敗');
            }
        } catch (err: any) {
            setError(err.response?.data?.message || '登入失敗，請稍後重試');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="login-box">
                <h1 className="login-title">失樂感監測系統</h1>
                <h2 className="login-subtitle">醫護人員後台</h2>

                <form onSubmit={handleSubmit} className="login-form">
                    {error && <div className="error-message">{error}</div>}

                    <div className="form-group">
                        <label htmlFor="email">電子郵件</label>
                        <input
                            id="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            placeholder="請輸入電子郵件"
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">密碼</label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            placeholder="請輸入密碼"
                            disabled={loading}
                        />
                    </div>

                    <button type="submit" className="login-button" disabled={loading}>
                        {loading ? '登入中...' : '登入'}
                    </button>
                </form>

                <div className="register-link-container">
                    <p className="register-link-text">
                        還沒有帳號？
                        <Link to="/register" className="register-link">
                            立即註冊
                        </Link>
                    </p>
                </div>

                <div className="login-footer">
                    <p>請使用醫護人員帳號登入</p>
                </div>
            </div>
        </div>
    );
}
