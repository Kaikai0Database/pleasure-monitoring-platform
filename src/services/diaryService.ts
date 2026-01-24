import type { Diary, DiaryFormData } from '../types/diary';

const API_BASE_URL = 'http://localhost:5000/api';

// 獲取 token
function getAuthToken(): string | null {
    return localStorage.getItem('access_token');
}

// 建立認證 headers
function getAuthHeaders(): HeadersInit {
    const token = getAuthToken();
    return {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
    };
}

export const diaryService = {
    // 獲取所有日記
    async getAllDiaries(year?: number, month?: number): Promise<Diary[]> {
        const params = new URLSearchParams();
        if (year) params.append('year', year.toString());
        if (month) params.append('month', month.toString());

        const url = `${API_BASE_URL}/diary${params.toString() ? '?' + params.toString() : ''}`;

        const response = await fetch(url, {
            method: 'GET',
            headers: getAuthHeaders(),
        });

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.message || '獲取日記失敗');
        }

        return data.diaries;
    },

    // 根據日期獲取日記
    async getDiaryByDate(date: string): Promise<Diary> {
        const response = await fetch(`${API_BASE_URL}/diary/${date}`, {
            method: 'GET',
            headers: getAuthHeaders(),
        });

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.message || '獲取日記失敗');
        }

        return data.diary;
    },

    // 根據 ID 獲取日記
    async getDiaryById(diaryId: number): Promise<Diary> {
        const response = await fetch(`${API_BASE_URL}/diary/id/${diaryId}`, {
            method: 'GET',
            headers: getAuthHeaders(),
        });

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.message || '獲取日記失敗');
        }

        return data.diary;
    },

    // 創建日記
    async createDiary(diaryData: DiaryFormData): Promise<Diary> {
        const response = await fetch(`${API_BASE_URL}/diary`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(diaryData),
        });

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.message || '創建日記失敗');
        }

        return data.diary;
    },

    // 更新日記
    async updateDiary(diaryId: number, diaryData: Partial<DiaryFormData>): Promise<Diary> {
        const response = await fetch(`${API_BASE_URL}/diary/${diaryId}`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify(diaryData),
        });

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.message || '更新日記失敗');
        }

        return data.diary;
    },

    // 刪除日記
    async deleteDiary(diaryId: number): Promise<void> {
        const response = await fetch(`${API_BASE_URL}/diary/${diaryId}`, {
            method: 'DELETE',
            headers: getAuthHeaders(),
        });

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.message || '刪除日記失敗');
        }
    },

    // 上傳圖片
    async uploadImages(files: File[]): Promise<string[]> {
        const formData = new FormData();
        files.forEach(file => {
            formData.append('images', file);
        });

        const token = getAuthToken();
        const response = await fetch(`${API_BASE_URL}/diary/upload-image`, {
            method: 'POST',
            headers: {
                ...(token && { 'Authorization': `Bearer ${token}` }),
            },
            body: formData,
        });

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.message || '上傳圖片失敗');
        }

        return data.images;
    },
};
