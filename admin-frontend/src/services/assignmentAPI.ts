import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api/admin';

// Create axios instance with auth token
const apiClient = axios.create({
    baseURL: API_BASE_URL,
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
