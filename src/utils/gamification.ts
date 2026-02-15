/**
 * 遊戲化邏輯核心工具函數
 * 
 * 功能：
 * - 等級與經驗值計算（初始 level=0, XP=0）
 * - 每日活動獎勵（50/30/10 遞減）
 * - 測驗冷卻機制（5小時）
 * - localStorage 持久化
 */

// ===== 介面定義 =====
export interface GamificationData {
    level: number;
    xp: number;
    lastActivityDate: string;  // yyyy-MM-DD 格式
    dailyActivityCount: number;
    lastAssessmentTimestamp: number | null;  // Unix timestamp (ms)
}

// ===== 常數定義 =====
const STORAGE_KEY_PREFIX = 'gamification_v2';  // v2: 升級版本，完全隔離舊數據
const COOLDOWN_DURATION = 5 * 60 * 60 * 1000;  // 5 小時（毫秒）

/**
 * 生成用戶專屬的 localStorage key（v2 版本）
 * 格式：gamification_v2_${userId}
 */
function getUserStorageKey(userId: number | string): string {
    return `${STORAGE_KEY_PREFIX}_${userId}`;
}

// ===== XP 與等級計算 =====

/**
 * 計算升到下一級所需的總經驗值
 * 公式：XP_next = 100 × (L + 1)²
 */
export function calculateRequiredXP(level: number): number {
    return 100 * Math.pow(level + 1, 2);
}

/**
 * 自動升級邏輯
 * 當 XP 足夠時自動升級，並返回新的 level 和剩餘 XP
 */
export function processLevelUp(currentLevel: number, currentXP: number): { level: number; xp: number } {
    let level = currentLevel;
    let xp = currentXP;

    while (xp >= calculateRequiredXP(level)) {
        xp -= calculateRequiredXP(level);
        level++;
    }

    return { level, xp };
}

// ===== 每日活動獎勵 =====

/**
 * 計算複方XP獎勵（基於當日次數 + 連續天數）
 * 
 * 獎勵規則：
 * - 基礎 XP：50 XP（固定）
 * - 當日次數加成：第1-2次 1x，第3次起 2x
 * - 連續天數加成：< 7天 1x，≥ 7天 2x
 * - 疊加邏輯：兩個加成相乘（最高 4x）
 * 
 * @param dailyCount - 當日完成次數（1, 2, 3...）
 * @param streak - 連續天數（從後端API獲取）
 * @returns XP數值、倍數和加成說明文字
 */
export function calculateCompoundXP(
    dailyCount: number,
    streak: number = 0
): {
    xp: number;
    baseXP: number;
    dailyMultiplier: number;
    streakMultiplier: number;
    totalMultiplier: number;
    bonusText: string[];
} {
    const BASE_XP = 50;

    // 當日次數加成：第3次起2x
    const dailyMultiplier = dailyCount >= 3 ? 2 : 1;

    // 連續天數加成：第7天起2x
    const streakMultiplier = streak >= 7 ? 2 : 1;

    // 疊加計算
    const totalMultiplier = dailyMultiplier * streakMultiplier;
    const finalXP = BASE_XP * totalMultiplier;

    // 生成獎勵文字
    const bonusText: string[] = [];
    if (dailyMultiplier === 2) {
        bonusText.push(`今日第${dailyCount}次挑戰 x2`);
    }
    if (streakMultiplier === 2) {
        bonusText.push(`連續${streak}天 x2`);
    }
    if (totalMultiplier === 4) {
        bonusText.push('🔥 雙重加成 x4！');
    }

    return {
        xp: finalXP,
        baseXP: BASE_XP,
        dailyMultiplier,
        streakMultiplier,
        totalMultiplier,
        bonusText
    };
}

/**
 * 【已棄用】根據當日活動次數計算 XP 獎勵（舊版遞減邏輯）
 * 第1次：50 XP
 * 第2次：30 XP
 * 第3次及之後：10 XP
 * 
 * @deprecated 請使用 calculateCompoundXP 以支援連續天數加成
 */
export function getDailyXPReward(activityCount: number): number {
    if (activityCount === 1) return 50;
    if (activityCount === 2) return 30;
    return 10;
}

/**
 * 獲取當前日期字串（台北時區 GMT+8）
 * 格式：yyyy-MM-DD
 */
function getCurrentDate(): string {
    // 使用 toLocaleDateString 並格式化為 yyyy-MM-DD
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// ===== localStorage 管理 =====

/**
 * 載入遊戲化數據（用戶專屬 - 嚴格版）
 * @param userId - 用戶 ID（必須有效）
 * 若 userId 無效，返回預設初始值（不進行任何 localStorage 操作）
 */
export function loadGamificationData(userId?: number | string): GamificationData {
    // 🔒 GATE: 若無 userId，返回預設值（完全不讀取 localStorage）
    if (!userId) {
        console.warn('⚠️ [載入數據] userId 為空，返回預設初始值（無 localStorage 操作）');
        return {
            level: 0,
            xp: 0,
            lastActivityDate: '',
            dailyActivityCount: 0,
            lastAssessmentTimestamp: null,
        };
    }

    try {
        const storageKey = getUserStorageKey(userId);
        const stored = localStorage.getItem(storageKey);

        if (!stored) {
            return {
                level: 0,
                xp: 0,
                lastActivityDate: '',
                dailyActivityCount: 0,
                lastAssessmentTimestamp: null,
            };
        }

        const data = JSON.parse(stored) as GamificationData;

        // 檢查跨日重置
        const currentDate = getCurrentDate();
        if (data.lastActivityDate !== currentDate) {
            data.dailyActivityCount = 0;
            data.lastActivityDate = currentDate;
            saveGamificationData(data, userId);
        }

        return data;
    } catch (error) {
        console.error('Failed to load gamification data:', error);
        return {
            level: 0,
            xp: 0,
            lastActivityDate: '',
            dailyActivityCount: 0,
            lastAssessmentTimestamp: null,
        };
    }
}

/**
 * 保存遊戲化數據到 localStorage（用戶專屬 - 嚴格版）
 * @param data - 遊戲化數據
 * @param userId - 用戶 ID（必須有效）
 */
export function saveGamificationData(data: GamificationData, userId?: number | string): void {
    // 🔒 GATE: 若無 userId，完全不執行寫入操作
    if (!userId) {
        console.error('❌ [保存數據] userId 為空，拒絕寫入 localStorage');
        return;
    }

    try {
        const storageKey = getUserStorageKey(userId);
        localStorage.setItem(storageKey, JSON.stringify(data));
        console.log(`💾 [保存數據] 用戶 ${userId} 數據已保存至 ${storageKey}`);
    } catch (error) {
        console.error('Failed to save gamification data:', error);
    }
}

// ===== XP 獎勵與升級 =====

/**
 * 增加 XP 並自動處理升級（用戶專屬）
 * @param amount - 要增加的 XP 數量
 * @param userId - 用戶 ID
 * 返回新的 level、xp 以及是否升級
 */
export function addXP(amount: number, userId?: number | string): { level: number; xp: number; leveledUp: boolean } {
    const data = loadGamificationData(userId);

    const newXP = data.xp + amount;
    const result = processLevelUp(data.level, newXP);

    const leveledUp = result.level > data.level;

    data.level = result.level;
    data.xp = result.xp;
    saveGamificationData(data, userId);

    return {
        level: result.level,
        xp: result.xp,
        leveledUp,
    };
}

/**
 * 遞增每日活動次數並返回新的次數（用戶專屬）
 * @param userId - 用戶 ID
 */
export function incrementDailyActivity(userId?: number | string): number {
    const data = loadGamificationData(userId);
    data.dailyActivityCount++;
    saveGamificationData(data, userId);
    return data.dailyActivityCount;
}

// ===== 測驗冷卻機制 =====

/**
 * 設定測驗冷卻時間戳記（用戶專屬）
 * @param userId - 用戶 ID
 */
export function setAssessmentCooldown(userId?: number | string): void {
    const data = loadGamificationData(userId);
    data.lastAssessmentTimestamp = Date.now();
    saveGamificationData(data, userId);

    // Debug log
    console.log(`⏰ [冷卻設定] 用戶 ${userId} 已進入冷卻，時間戳: ${data.lastAssessmentTimestamp}`);
}

/**
 * 獲取剩餘冷卻時間（秒）（用戶專屬）
 * @param userId - 用戶 ID
 * 返回 0 表示無冷卻
 */
export function getCooldownRemaining(userId?: number | string): number {
    // 安全檢查：若無 userId，直接返回 0（避免讀取錯誤的 key）
    if (!userId) {
        console.warn('⚠️ [冷卻檢查] userId 為空，返回 0');
        return 0;
    }

    const data = loadGamificationData(userId);

    if (!data.lastAssessmentTimestamp) {
        return 0;
    }

    const elapsed = Date.now() - data.lastAssessmentTimestamp;
    const remaining = COOLDOWN_DURATION - elapsed;

    const remainingSeconds = remaining > 0 ? Math.ceil(remaining / 1000) : 0;

    // Debug log (only when there's cooldown)
    if (remainingSeconds > 0) {
        console.log(`⏱️ [冷卻檢查] 用戶 ${userId} 剩餘: ${remainingSeconds}秒 (${Math.floor(remainingSeconds / 60)}分)`);
    }

    return remainingSeconds;
}
