import { type ReactNode, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './Layout.css';


interface LayoutProps {
    children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
    const navigate = useNavigate();
    const location = useLocation();
    const staff = JSON.parse(localStorage.getItem('admin_staff') || '{}');
    const [sidebarOpen, setSidebarOpen] = useState(false);

    const handleLogout = () => {
        localStorage.removeItem('admin_token');
        localStorage.removeItem('admin_staff');
        navigate('/');
    };

    const menuItems = [
        { path: '/dashboard', label: '總覽', icon: '📊' },
        { path: '/watchlist', label: '特別關注個案', icon: '⭐' },
        { path: '/assignments', label: '個案分配', icon: '👥' },
    ];

    const handleNavClick = (path: string) => {
        navigate(path);
        setSidebarOpen(false); // close sidebar on mobile after navigation
    };

    return (
        <div className="layout-container">
            <header className="layout-header">
                {/* Hamburger – only visible on mobile via CSS */}
                <button
                    className="hamburger-button"
                    onClick={() => setSidebarOpen(true)}
                    aria-label="開啟選單"
                >
                    ☰
                </button>

                <h1 className="header-title">失樂感監測系統</h1>

                <div className="header-user">
                    <span className="user-name">{staff.name}</span>
                    <button onClick={handleLogout} className="logout-button">
                        登出
                    </button>
                </div>
            </header>

            <div className="layout-content">
                {/* Backdrop – tapping it closes the sidebar on mobile */}
                {sidebarOpen && (
                    <div
                        className="sidebar-backdrop"
                        onClick={() => setSidebarOpen(false)}
                    />
                )}

                <aside className={`sidebar${sidebarOpen ? ' sidebar-open' : ''}`}>
                    <nav className="sidebar-nav">
                        {menuItems.map((item) => (
                            <button
                                key={item.path}
                                onClick={() => handleNavClick(item.path)}
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
