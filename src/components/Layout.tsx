import React, { useEffect } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Footer } from './Footer';

export const Layout: React.FC = () => {
    const { user, isLoading } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        // If loading, do nothing
        if (isLoading) return;

        // If user is logged in
        if (user) {
            // First check: if not consented AND not on consent page, redirect to consent
            if (user.has_consented === false && location.pathname !== '/consent') {
                navigate('/consent');
            }
            // Second check: if consented but profile not completed AND not on profile-setup page
            else if (user.has_consented === true && user.is_profile_completed === false && location.pathname !== '/profile-setup') {
                navigate('/profile-setup');
            }
        }
    }, [user, isLoading, location.pathname, navigate]);

    return (
        <div className="min-h-screen font-pixel text-gray-900 flex flex-col">
            <header className="p-4">
                <div className="container mx-auto flex justify-center items-center">
                    <h1 className="text-xl sm:text-4xl font-bold" style={{ color: '#000000', textShadow: '1px 1px 0px #ffffff' }}>失樂感監測平台</h1>
                </div>
            </header>
            <main className="container mx-auto p-4 flex-grow">
                <Outlet />
            </main>
            <Footer />
        </div>
    );
};
