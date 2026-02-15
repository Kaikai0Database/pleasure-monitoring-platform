/**
 * Alert Calculator Utility
 * Frontend implementation of MA calculation and alert detection
 * Shared logic between user frontend and admin dashboard
 */

import type {
    AssessmentHistory,
    DailyAverageResult,
    AlertInfo,
    AlertDetectionResult
} from '../types/alert';

/**
 * Calculate daily average score for a specific date
 */
export function calculateDailyAverage(
    assessments: AssessmentHistory[],
    targetDate: Date
): DailyAverageResult | null {
    // Filter assessments for target date
    const targetDateStr = targetDate.toISOString().split('T')[0];

    const dailyAssessments = assessments.filter(a => {
        const assessDate = new Date(a.completed_at).toISOString().split('T')[0];
        return assessDate === targetDateStr;
    });

    if (dailyAssessments.length === 0) {
        return null;
    }

    const total = dailyAssessments.reduce((sum, a) => sum + a.total_score, 0);
    const average = total / dailyAssessments.length;

    return {
        average: Math.round(average * 10) / 10,  // Round to 1 decimal
        count: dailyAssessments.length
    };
}

/**
 * Calculate Moving Average for n days
 * Matches backend logic: 按日分組，需要 >= n/2 天的數據
 */
export function calculateMovingAverage(
    assessments: AssessmentHistory[],
    days: number,
    endDate: Date
): number | null {
    // Get start date (n days before end date)
    const startDate = new Date(endDate);
    startDate.setDate(startDate.getDate() - days);

    // Group assessments by date and calculate daily averages
    const dailyAverages: Record<string, number[]> = {};

    assessments.forEach(a => {
        const assessDate = new Date(a.completed_at);

        // Skip if outside date range
        if (assessDate < startDate || assessDate > endDate) {
            return;
        }

        const dateKey = assessDate.toISOString().split('T')[0];

        if (!dailyAverages[dateKey]) {
            dailyAverages[dateKey] = [];
        }
        dailyAverages[dateKey].push(a.total_score);
    });

    // Calculate average for each day
    const dayAverages = Object.values(dailyAverages).map(scores => {
        const sum = scores.reduce((a, b) => a + b, 0);
        return sum / scores.length;
    });

    // Check if we have enough data (at least n/2 days)
    const requiredDays = Math.ceil(days / 2);
    if (dayAverages.length < requiredDays) {
        return null;
    }

    // Calculate MA
    const maSum = dayAverages.reduce((a, b) => a + b, 0);
    const ma = maSum / dayAverages.length;

    return Math.round(ma * 10) / 10;  // Round to 1 decimal
}

/**
 * Detect alerts based on assessment history
 */
export function detectAlerts(
    assessments: AssessmentHistory[],
    targetDate: Date = new Date()
): AlertDetectionResult {
    // Calculate daily average
    const dailyResult = calculateDailyAverage(assessments, targetDate);

    // Return no alerts if less than 3 assessments today
    if (!dailyResult || dailyResult.count < 3) {
        return {
            highAlert: null,
            lowAlert: null
        };
    }

    const dailyAvg = dailyResult.average;

    // Calculate MAs
    const ma7 = calculateMovingAverage(assessments, 7, targetDate);
    const ma14 = calculateMovingAverage(assessments, 14, targetDate);
    const ma30 = calculateMovingAverage(assessments, 30, targetDate);

    // Detect High Alert (daily_avg > MA)
    const highExceeded: Record<string, number> = {};
    if (ma7 !== null && dailyAvg > ma7) {
        highExceeded['7日'] = ma7;
    }
    if (ma14 !== null && dailyAvg > ma14) {
        highExceeded['14日'] = ma14;
    }
    if (ma30 !== null && dailyAvg > ma30) {
        highExceeded['30日'] = ma30;
    }

    // Detect Low Alert (0 < MA - daily_avg <= 3)
    const lowApproached: Record<string, number> = {};
    if (ma7 !== null) {
        const diff = ma7 - dailyAvg;
        if (diff > 0 && diff <= 3) {
            lowApproached['7日'] = ma7;
        }
    }
    if (ma14 !== null) {
        const diff = ma14 - dailyAvg;
        if (diff > 0 && diff <= 3) {
            lowApproached['14日'] = ma14;
        }
    }
    if (ma30 !== null) {
        const diff = ma30 - dailyAvg;
        if (diff > 0 && diff <= 3) {
            lowApproached['30日'] = ma30;
        }
    }

    // Create alert info
    const dateStr = targetDate.toISOString().split('T')[0];

    const highAlert: AlertInfo | null = Object.keys(highExceeded).length > 0
        ? {
            date: dateStr,
            dailyAverage: dailyAvg,
            exceededLines: highExceeded,
            assessmentCount: dailyResult.count
        }
        : null;

    // High alert has priority - only show low if no high
    const lowAlert: AlertInfo | null = !highAlert && Object.keys(lowApproached).length > 0
        ? {
            date: dateStr,
            dailyAverage: dailyAvg,
            exceededLines: lowApproached,
            assessmentCount: dailyResult.count
        }
        : null;

    return {
        highAlert,
        lowAlert
    };
}
