export interface HealthcareStaff {
    id: number;
    email: string;
    name: string;
    role?: string;
    created_at: string;
}

export interface Patient {
    id: number;
    email: string;
    name: string;
    nickname?: string;
    dob?: string;
    gender?: string;
    created_at: string;
    is_profile_completed: boolean;
    group?: 'student' | 'clinical';  // Patient group classification
    latest_assessment?: Assessment;
    total_assessments?: number;
    average_score?: number;
    inactive_warning?: boolean;  // True if patient hasn't logged in for 5+ days
    is_in_watchlist?: boolean;   // True if patient is in current staff's watchlist
    // Additional profile fields
    height?: number;
    weight?: number;
    education?: string;
    marital_status?: string;
    has_children?: boolean;
    economic_status?: string;
    has_job?: boolean;
    salary_range?: string;
    location_city?: string;
    location_district?: string;
    living_situation?: string;
}

export interface Assessment {
    id: number;
    total_score: number;
    max_score: number;
    level: string;
    percentage: number;
    completed_at: string;
    answers: any[];
}

export interface Diary {
    id: number;
    user_id: number;
    date: string;
    mood?: string;
    content?: string;
    images: string[];
    period_marker: boolean;
    created_at: string;
    updated_at: string;
}

export interface WatchlistItem {
    id: number;
    staff_id: number;
    patient_id: number;
    notes?: string;
    created_at: string;
    updated_at: string;
    patient?: Patient;
    latest_assessment?: Assessment;
    average_score?: number;
}

export interface DashboardStats {
    total_patients: number;
    active_today: number;
    total_assessments: number;
    average_score: number;
    watchlist_count: number;
    recent_activity: { date: string; count: number }[];
    recent_patients: Patient[];
}

export interface Statistics {
    total_count: number;
    average_score: number | null;
    highest_score: number | null;
    lowest_score: number | null;
    trend: {
        date: string;
        score: number;
        max_score: number;
        percentage: number;
    }[];
}
