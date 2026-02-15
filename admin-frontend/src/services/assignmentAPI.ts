import axios from 'axios';

// Use environment variable or fallback to /api/admin for proxy
const API_BASE_URL = (import.meta.env.VITE_API_URL || '') + '/api/admin';

// Create axios instance with auth token
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': '69420',  // Bypass ngrok warning page
    },
});

// Add auth token to requests
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('admin_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Assignment API endpoints
export const assignmentAPI = {
    // Get all assignments
    getAll: () => apiClient.get('/assignments'),

    // Assign patient to nurse
    assign: (patientId: number, staffId: number, notes?: string) =>
        apiClient.post('/assignments', {
            patient_id: patientId,
            staff_id: staffId,
            notes: notes || ''
        }),

    // Remove assignment
    unassign: (assignmentId: number) =>
        apiClient.delete(`/assignments/${assignmentId}`),

    // Get staff list (for dropdown)
    getStaffList: () => apiClient.get('/assignments/staff'),
};
