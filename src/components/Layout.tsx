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
            // If profile is NOT completed AND we are NOT on the setup page
            if (user.is_profile_completed === false && location.pathname !== '/profile-setup') {
                navigate('/profile-setup');
            }
        }
    }, [user, isLoading, location.pathname, navigate]);

    return (
        <div className="min-h-screen bg-gray-100 font-pixel text-gray-900 flex flex-col">
            <header className="bg-white border-b-4 border-gray-800 p-4">
                <div className="container mx-auto flex justify-center items-center">
                    <h1 className="text-4xl font-bold">失樂感監測平台</h1>
                </div>
            </header>
            <main className="container mx-auto p-4 flex-grow">
                <Outlet />
            </main>
            <Footer />
        </div>
    );
};
