import type {
    RegisterRequest,
    LoginRequest,
    AuthResponse,
    SaveHistoryRequest,
    HistoryResponse,
    ApiResponse,
} from '../types/api';

// Use environment variable or fallback to /api for proxy
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

// Helper function to get auth token
const getAuthToken = (): string | null => {
    return localStorage.getItem('access_token');
};

// Helper function to create headers
const createHeaders = (includeAuth: boolean = false): HeadersInit => {
    const headers: HeadersInit = {
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'true', // Bypass ngrok warning
    };

    if (includeAuth) {
        const token = getAuthToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
    }

    return headers;
};

// Generic API request handler
async function apiRequest<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.message || 'API request failed');
    }

    return data;
}

// Authentication API
export const authApi = {
    register: async (data: RegisterRequest): Promise<AuthResponse> => {
        return apiRequest<AuthResponse>('/auth/register', {
            method: 'POST',
            headers: createHeaders(),
            body: JSON.stringify(data),
        });
    },

    login: async (data: LoginRequest): Promise<AuthResponse> => {
        const response = await apiRequest<AuthResponse>('/auth/login', {
            method: 'POST',
            headers: createHeaders(),
            body: JSON.stringify(data),
        });

        // Store token in localStorage
        if (response.access_token) {
            localStorage.setItem('access_token', response.access_token);
            if (response.user) {
                localStorage.setItem('user', JSON.stringify(response.user));
            }
        }

        return response;
    },

    getCurrentUser: async (): Promise<AuthResponse> => {
        return apiRequest<AuthResponse>('/auth/me', {
            method: 'GET',
            headers: createHeaders(true),
        });
    },

    logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
    },
};

// History API
export const historyApi = {
    getHistory: async (): Promise<HistoryResponse> => {
        return apiRequest<HistoryResponse>('/history', {
            method: 'GET',
            headers: createHeaders(true),
        });
    },

    saveHistory: async (data: SaveHistoryRequest): Promise<HistoryResponse> => {
        return apiRequest<HistoryResponse>('/history', {
            method: 'POST',
            headers: createHeaders(true),
            body: JSON.stringify(data),
        });
    },

    deleteHistory: async (id: number, reason?: string, permanent: boolean = false): Promise<ApiResponse> => {
        return apiRequest<ApiResponse>(`/history/${id}`, {
            method: 'DELETE',
            headers: createHeaders(true),
            body: JSON.stringify({ reason, permanent }),
        });
    },

    getTrash: async (): Promise<HistoryResponse> => {
        return apiRequest<HistoryResponse>('/history/trash', {
            method: 'GET',
            headers: createHeaders(true),
        });
    },

    restoreHistory: async (id: number): Promise<ApiResponse> => {
        return apiRequest<ApiResponse>(`/history/${id}/restore`, {
            method: 'POST',
            headers: createHeaders(true),
        });
    },
};

// Alerts API
export const alertsApi = {
    getAlerts: async (): Promise<import('../types/api').AlertsResponse> => {
        return apiRequest<import('../types/api').AlertsResponse>('/alerts', {
            method: 'GET',
            headers: createHeaders(true),
        });
    },

    getUnreadCount: async (): Promise<import('../types/api').UnreadCountResponse> => {
        return apiRequest<import('../types/api').UnreadCountResponse>('/alerts/unread-count', {
            method: 'GET',
            headers: createHeaders(true),
        });
    },

    markAsRead: async (alertId: number): Promise<ApiResponse> => {
        return apiRequest<ApiResponse>(`/alerts/${alertId}/read`, {
            method: 'PUT',
            headers: createHeaders(true),
        });
    },

    markAllAsRead: async (): Promise<ApiResponse> => {
        return apiRequest<ApiResponse>('/alerts/mark-all-read', {
            method: 'PUT',
            headers: createHeaders(true),
        });
    },
};

