import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api/admin';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add token to all requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('admin_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Handle auth errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('admin_token');
            localStorage.removeItem('admin_staff');
            window.location.href = '/';
        }
        return Promise.reject(error);
    }
);

export const authAPI = {
    login: (email: string, password: string) =>
        api.post('/auth/login', { email, password }),
    register: (email: string, password: string, name: string, role?: string) =>
        api.post('/auth/register', { email, password, name, role }),
    getMe: () => api.get('/auth/me'),
};

export const patientsAPI = {
    getAll: () => api.get('/patients'),
    getDetail: (id: number) => api.get(`/patients/${id}`),
    getHistory: (id: number) => api.get(`/patients/${id}/history`),
    getStatistics: (id: number) => api.get(`/patients/${id}/statistics`),
    getAlerts: (id: number) => api.get(`/patients/${id}/alerts`),
    getAlertCounts: () => api.get('/patients/alert-counts'),
};

export const watchlistAPI = {
    getAll: () => api.get('/watchlist'),
    add: (patient_id: number, notes?: string) =>
        api.post('/watchlist', { patient_id, notes }),
    remove: (patient_id: number) => api.delete(`/watchlist/${patient_id}`),
    updateNotes: (patient_id: number, notes: string) =>
        api.put(`/watchlist/${patient_id}/notes`, { notes }),
    reorder: (order: Array<{ patient_id: number; display_order: number }>) =>
        api.post('/watchlist/reorder', { order }),
};

export const dashboardAPI = {
    getStats: () => api.get('/dashboard/stats'),
};

export const diaryAPI = {
    getPatientDiaries: (patient_id: number) => api.get(`/diary/${patient_id}`),
};

export default api;
