/**
 * Alert Type Definitions
 * Types for frontend alert calculation system
 */

export interface AlertInfo {
    date: string;              // Alert date (YYYY-MM-DD)
    dailyAverage: number;      // Daily average score
    exceededLines: Record<string, number>;  // MA lines exceeded/approached
    assessmentCount: number;   // Number of assessments today
}

export interface AlertDetectionResult {
    highAlert: AlertInfo | null;
    lowAlert: AlertInfo | null;
}

export interface DailyAverageResult {
    average: number;
    count: number;
}

export interface AssessmentHistory {
    id: number;
    total_score: number;
    completed_at: string;
    // ... other fields
}
