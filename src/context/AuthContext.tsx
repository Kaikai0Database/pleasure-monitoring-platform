import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { authApi } from '../services/api';
import type { User } from '../types/api';

interface AuthContextType {
    user: User | null;
    login: (email: string, password: string) => Promise<{ success: boolean; user: User }>;
    signup: (email: string, name: string, password: string) => Promise<void>;
    logout: () => void;
    updateProfile: (data: Partial<User>) => Promise<void>;
    isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    // Auto-login on mount if token exists
    useEffect(() => {
        const initAuth = async () => {
            const token = localStorage.getItem('access_token');
            const savedUser = localStorage.getItem('user');

            if (token && savedUser) {
                try {
                    // Use saved user data directly
                    const parsedUser = JSON.parse(savedUser);
                    setUser(parsedUser);

                    // Optionally verify token in background (don't block UI)
                    authApi.getCurrentUser().catch((error) => {
                        console.warn('Token verification failed:', error);
                        // If verification fails, clear storage and logout
                        authApi.logout();
                        setUser(null);
                    });
                } catch (error) {
                    // Failed to parse user data, clear storage
                    console.error('Failed to restore user session:', error);
                    authApi.logout();
                }
            }
            setIsLoading(false);
        };

        initAuth();
    }, []);

    const login = async (email: string, password: string) => {
        try {
            const response = await authApi.login({ email, password });
            if (response.user) {
                setUser(response.user);
                return { success: true, user: response.user };
            }
            throw new Error('No user data returned');
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    };

    const updateProfile = async (data: Partial<User>) => {
        try {
            // Need to implement updateProfile in api.ts first? 
            // Or just fetch here. 
            // Re-use logic or call API.
            // Wait, I haven't added updateProfile to api.ts yet.
            // I'll do it via fetch for now or add to api.ts properly.
            // Let's assume api.ts has it or I add it now.
            // I'll add it to api.ts in a sec.
            // For now, simple fetch or better: update local state.
            const token = localStorage.getItem('access_token');
            // ... actually better to use api service. 
            // I'll leave this empty or throw for now, relying on ProfileSetup's direct fetch?
            // No, ProfileSetup calls updateProfile from context?
            // Previous ProfileSetup implementation used: `const { user, updateProfile } = useAuth();`
            // So I MUST provide it.

            // Let's implement it here properly.
            const response = await fetch('http://localhost:5000/api/auth/profile', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                body: JSON.stringify(data)
            });
            const resData = await response.json();
            if (resData.success && resData.user) {
                setUser(resData.user);
                // Update local storage too
                localStorage.setItem('user', JSON.stringify(resData.user));
            } else {
                throw new Error(resData.message || 'Update failed');
            }
        } catch (error) {
            console.error('Update profile failed:', error);
            throw error;
        }
    };

    const signup = async (email: string, name: string, password: string) => {
        try {
            const registerResponse = await authApi.register({ email, name, password });
            // Auto-login after successful registration
            if (registerResponse.success) {
                await login(email, password);
            }
        } catch (error) {
            console.error('Signup failed:', error);
            throw error;
        }
    };

    const logout = () => {
        authApi.logout();
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, signup, logout, updateProfile, isLoading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
