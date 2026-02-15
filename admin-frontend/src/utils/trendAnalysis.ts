/**
 * 趨勢分析工具 - MA 計算與警報偵測
 * 用於醫護端患者數據監控
 */

export interface DailyScore {
    date: string;
    score: number | null;
}

export interface TrendAlert {
    type: 'high' | 'low';  // high: 穿線警報, low: 接近線警報
    exceededLines: string[];  // 觸發的均線 ['7日', '14日', '30日']
    currentScore: number;
    timestamp: string;
}

export interface TrendAnalysisResult {
    ma7: number | null;
    ma14: number | null;
    ma30: number | null;
    alerts: TrendAlert[];
    hasSufficientData: boolean;
}

/**
 * 計算移動平均線
 * @param data 歷史分數數據（必須按日期排序）
 * @param period MA 週期（7, 14, 30）
 * @param minDataRatio 最小數據比例（預設 0.5，即至少需要 period/2 天的數據）
 */
export function calculateMA(
    data: DailyScore[],
    period: number,
    minDataRatio: number = 0.5
): number | null {
    if (data.length < Math.ceil(period * minDataRatio)) {
        return null;  // 數據不足
    }

    // 取最近 period 天的數據
    const recentData = data.slice(-period);
    const validScores = recentData
        .map(d => d.score)
        .filter((s): s is number => s !== null);

    // 檢查是否有足夠的有效數據
    if (validScores.length < Math.ceil(period * minDataRatio)) {
        return null;
    }

    const sum = validScores.reduce((acc, score) => acc + score, 0);
    return Number((sum / validScores.length).toFixed(1));
}

/**
 * 偵測穿線警報（High Alert）
 * 當日分數 > MA 線時觸發
 */
function detectCrossover(
    currentScore: number,
    previousScore: number | null,
    ma: number | null
): boolean {
    if (ma === null || previousScore === null) {
        return false;
    }

    // 穿越偵測：當日 > MA 且前一日 <= MA
    return currentScore > ma && previousScore <= ma;
}

/**
 * 偵測接近線警報（Low Alert）
 * 當 0 < (MA - 當日分數) <= 3 時觸發
 */
function detectApproaching(
    currentScore: number,
    ma: number | null,
    threshold: number = 3
): boolean {
    if (ma === null) {
        return false;
    }

    const diff = ma - currentScore;
    return diff > 0 && diff <= threshold;
}

/**
 * 分析趨勢並生成警報
 * @param history 完整歷史數據（按日期升序）
 * @param minAssessments 觸發警報所需的最小評估次數（當日）
 */
export function analyzeTrend(
    history: DailyScore[],
    minAssessments: number = 3
): TrendAnalysisResult {
    if (history.length === 0) {
        return {
            ma7: null,
            ma14: null,
            ma30: null,
            alerts: [],
            hasSufficientData: false,
        };
    }

    // 計算 MA
    const ma7 = calculateMA(history, 7);
    const ma14 = calculateMA(history, 14);
    const ma30 = calculateMA(history, 30);

    const currentData = history[history.length - 1];
    const previousData = history.length > 1 ? history[history.length - 2] : null;

    const alerts: TrendAlert[] = [];

    // 只有當日分數存在才進行警報檢查
    if (currentData.score !== null) {
        const currentScore = currentData.score;
        const previousScore = previousData?.score ?? null;

        // 穿線警報（優先級最高）
        const crossoverLines: string[] = [];
        if (detectCrossover(currentScore, previousScore, ma7)) {
            crossoverLines.push('7日');
        }
        if (detectCrossover(currentScore, previousScore, ma14)) {
            crossoverLines.push('14日');
        }
        if (detectCrossover(currentScore, previousScore, ma30)) {
            crossoverLines.push('30日');
        }

        if (crossoverLines.length > 0) {
            alerts.push({
                type: 'high',
                exceededLines: crossoverLines,
                currentScore,
                timestamp: currentData.date,
            });
        } else {
            // 只有沒有穿線時才檢查接近線
            const approachingLines: string[] = [];
            if (detectApproaching(currentScore, ma7)) {
                approachingLines.push('7日');
            }
            if (detectApproaching(currentScore, ma14)) {
                approachingLines.push('14日');
            }
            if (detectApproaching(currentScore, ma30)) {
                approachingLines.push('30日');
            }

            if (approachingLines.length > 0) {
                alerts.push({
                    type: 'low',
                    exceededLines: approachingLines,
                    currentScore,
                    timestamp: currentData.date,
                });
            }
        }
    }

    return {
        ma7,
        ma14,
        ma30,
        alerts,
        hasSufficientData: history.length >= 7,
    };
}

/**
 * 準備圖表數據（包含 MA 線）
 */
export function prepareChartData(history: DailyScore[]): Array<{
    date: string;
    當日分數: number | null;
    '7日平均': number | null;
    '14日平均': number | null;
    '30日平均': number | null;
}> {
    return history.map((item, index) => {
        const historySoFar = history.slice(0, index + 1);

        return {
            date: item.date,
            當日分數: item.score,
            '7日平均': calculateMA(historySoFar, 7),
            '14日平均': calculateMA(historySoFar, 14),
            '30日平均': calculateMA(historySoFar, 30),
        };
    });
}
