import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';
import './Register.css';

export default function Register() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        jobTitle: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        // 驗證
        if (!formData.name || !formData.email || !formData.password || !formData.jobTitle) {
            setError('請填寫所有欄位');
            return;
        }

        if (formData.password.length < 6) {
            setError('密碼長度至少需要 6 個字元');
            return;
        }

        setLoading(true);

        try {
            const response = await authAPI.register(
                formData.email,
                formData.password,
                formData.name,
                formData.jobTitle
            );

            if (response.data.success) {
                alert('註冊成功！請使用您的帳號登入');
                navigate('/');
            } else {
                setError(response.data.message || '註冊失敗');
            }
        } catch (err: any) {
            setError(err.response?.data?.message || '註冊失敗，請稍後重試');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="register-container">
            <div className="register-box">
                <h1 className="register-title">失樂感監測系統</h1>
                <h2 className="register-subtitle">醫護人員註冊</h2>

                <form onSubmit={handleSubmit} className="register-form">
                    {error && <div className="error-message">{error}</div>}

                    <div className="form-group">
                        <label htmlFor="name">姓名</label>
                        <input
                            id="name"
                            name="name"
                            type="text"
                            value={formData.name}
                            onChange={handleChange}
                            required
                            placeholder="請輸入姓名"
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="email">電子郵件</label>
                        <input
                            id="email"
                            name="email"
                            type="email"
                            value={formData.email}
                            onChange={handleChange}
                            required
                            placeholder="請輸入電子郵件"
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">密碼</label>
                        <input
                            id="password"
                            name="password"
                            type="password"
                            value={formData.password}
                            onChange={handleChange}
                            required
                            placeholder="至少 6 個字元"
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="jobTitle">職稱</label>
                        <select
                            id="jobTitle"
                            name="jobTitle"
                            value={formData.jobTitle}
                            onChange={handleChange}
                            required
                            disabled={loading}
                        >
                            <option value="">請選擇職稱</option>
                            <option value="醫師">醫師</option>
                            <option value="護理師">護理師</option>
                            <option value="心理師">心理師</option>
                            <option value="個案管理師">個案管理師</option>
                            <option value="其他">其他</option>
                        </select>
                    </div>

                    <button type="submit" className="register-button" disabled={loading}>
                        {loading ? '註冊中...' : '註冊'}
                    </button>
                </form>

                <div className="register-footer">
                    <Link to="/" className="link-to-login">
                        已有帳號？返回登入
                    </Link>
                </div>
            </div>
        </div>
    );
}
