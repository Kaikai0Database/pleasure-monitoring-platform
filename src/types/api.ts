// API Response Types
export interface ApiResponse<T = any> {
    success: boolean;
    message?: string;
    [key: string]: any;
}

// User Types
export interface User {
    id: number;
    email: string;
    name: string;
    created_at?: string;
    daily_login_count?: number;
    is_profile_completed?: boolean;
    has_consented?: boolean;
    // Profile Fields
    nickname?: string;
    dob?: string;
    gender?: string;
    height?: number;
    weight?: number;
    education?: string;
    marital_status?: string;
    marriage_other?: string;
    has_children?: boolean;
    children_count?: number;
    economic_status?: string;
    family_structure?: string;
    family_other?: string;
    has_job?: boolean;
    salary_range?: string;
    location_city?: string;
    location_district?: string;
    living_situation?: string;
    cohabitant_count?: number;
    religion?: boolean;
    religion_other?: string;
    consecutive_days?: number;
    group?: string;
}

export interface RegisterRequest {
    email: string;
    name: string;
    password: string;
}

export interface LoginRequest {
    email: string;
    password: string;
}

export interface AuthResponse extends ApiResponse {
    access_token?: string;
    user?: User;
}

// Assessment History Types
export interface AssessmentAnswer {
    questionId: number;
    emoji: string;
    score: number;
}

export interface AssessmentHistory {
    id: number;
    total_score: number;
    max_score: number;
    level: string;
    percentage: number;
    answers: AssessmentAnswer[];
    completed_at: string;
    // Soft delete fields
    is_deleted?: boolean;
    deleted_at?: string | null;
    delete_reason?: string | null;
}

export interface SaveHistoryRequest {
    total_score: number;
    max_score: number;
    level: string;
    answers: AssessmentAnswer[];
}

export interface HistoryResponse extends ApiResponse {
    history?: AssessmentHistory[];
    history_id?: number;
}

// Score Alert Types
export interface ScoreAlert {
    id: number;
    user_id: number;
    alert_date: string;
    daily_average: number;
    exceeded_lines: { [key: string]: number };  // {"7日": 38, "14日": 35}
    alert_type: 'high' | 'low';  // 'high' = above MA, 'low' = 3+ points below MA
    is_read: boolean;
    created_at: string;
}

export interface AlertsResponse extends ApiResponse {
    alerts?: ScoreAlert[];
}

export interface UnreadCountResponse extends ApiResponse {
    count?: number;
}

