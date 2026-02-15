/**
 * Tutorial localStorage 管理工具
 * 用於追蹤用戶是否已完成引導教學
 */

const TUTORIAL_STORAGE_KEY = 'tutorial_completed';

/**
 * 檢查用戶是否已完成教學
 * @param userId - 用戶 ID
 * @returns 是否已完成教學
 */
export function hasTutorialCompleted(userId: number | string): boolean {
    if (!userId) return true; // 無用戶ID視為已完成（不顯示）

    const key = `${TUTORIAL_STORAGE_KEY}_${userId}`;
    return localStorage.getItem(key) === 'true';
}

/**
 * 標記教學為已完成
 * @param userId - 用戶 ID
 */
export function markTutorialCompleted(userId: number | string): void {
    if (!userId) return;

    const key = `${TUTORIAL_STORAGE_KEY}_${userId}`;
    localStorage.setItem(key, 'true');
    console.log(`✅ [Tutorial] 用戶 ${userId} 已完成教學`);
}

/**
 * 重置教學狀態（用於測試或重新查看）
 * @param userId - 用戶 ID
 */
export function resetTutorial(userId: number | string): void {
    if (!userId) return;

    const key = `${TUTORIAL_STORAGE_KEY}_${userId}`;
    localStorage.removeItem(key);
    console.log(`🔄 [Tutorial] 用戶 ${userId} 教學狀態已重置`);
}
