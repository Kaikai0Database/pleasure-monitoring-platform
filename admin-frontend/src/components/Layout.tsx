import { type ReactNode } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './Layout.css';


interface LayoutProps {
    children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
    const navigate = useNavigate();
    const location = useLocation();
    const staff = JSON.parse(localStorage.getItem('admin_staff') || '{}');

    const handleLogout = () => {
        localStorage.removeItem('admin_token');
        localStorage.removeItem('admin_staff');
        navigate('/');
    };

    const menuItems = [
        { path: '/dashboard', label: '總覽', icon: '📊' },
        { path: '/watchlist', label: '特別關注病人', icon: '⭐' },
        { path: '/assignments', label: '病人分配', icon: '👥' },
    ];

    return (
        <div className="layout-container">
            <header className="layout-header">
                <h1 className="header-title">失樂感監測系統</h1>
                <div className="header-user">
                    <span className="user-name">{staff.name}</span>
                    <button onClick={handleLogout} className="logout-button">
                        登出
                    </button>
                </div>
            </header>

            <div className="layout-content">
                <aside className="sidebar">
                    <nav className="sidebar-nav">
                        {menuItems.map((item) => (
                            <button
                                key={item.path}
                                onClick={() => navigate(item.path)}
                                className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
                            >
                                <span className="menu-icon">{item.icon}</span>
                                <span className="menu-text">{item.label}</span>
                            </button>
                        ))}
                    </nav>
                </aside>

                <main className="main-content">{children}</main>
            </div>
        </div>
    );
}
