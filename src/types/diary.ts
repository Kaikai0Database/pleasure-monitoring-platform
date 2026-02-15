// 日記相關類型定義

export interface Diary {
    id: number;
    user_id: number;
    date: string; // ISO date string (YYYY-MM-DD)
    mood?: string; // 情緒 key，可選
    content?: string;
    images?: string[];
    period_marker: boolean;
    created_at: string;
    updated_at: string;
}

// 日記表單資料結構
export interface DiaryFormData {
    date: string;  // YYYY-MM-DD 格式
    mood?: string;  // 情緒 key（可選，允許只標記生理期）
    content?: string;
    images?: string[];
    period_marker?: boolean;
}

export interface MoodOption {
    key: string;
    name: string;
    icon: string; // 圖片路徑
}

// 情緒選項配置
export const MOODS: MoodOption[] = [
    { key: 'happy', name: '開心', icon: '/dairy/pexal_face_happy.png' },
    { key: 'sad', name: '難過', icon: '/dairy/pexal_face_sad.png' },
    { key: 'angry', name: '生氣', icon: '/dairy/pexal_face_angry.png' },
    { key: 'fear', name: '害怕', icon: '/dairy/pexal_face_Fear.png' },
    { key: 'exhausted', name: '疲憊', icon: '/dairy/pexal_face_exhausted.png' },
    { key: 'awkward', name: '尷尬', icon: '/dairy/pexal_face_Awkward.png' },
    { key: 'confuse', name: '困惑', icon: '/dairy/pexal_face_Confuse.png' },
    { key: 'shy', name: '害羞', icon: '/dairy/pexal_face_shy.png' },
    { key: 'uncomfortable', name: '不適', icon: '/dairy/pexal_face_uncomfortable.png' },
];

export const PERIOD_MARKER: MoodOption = {
    key: 'period',
    name: '生理期',
    icon: '/dairy/calendar.png'
};

// 根據 key 獲取情緒名稱
export function getMoodName(moodKey: string): string {
    const mood = MOODS.find(m => m.key === moodKey);
    return mood ? mood.name : moodKey;
}

// 根據 key 獲取情緒圖標
export function getMoodIcon(moodKey: string): string {
    const mood = MOODS.find(m => m.key === moodKey);
    return mood ? mood.icon : '';
}
