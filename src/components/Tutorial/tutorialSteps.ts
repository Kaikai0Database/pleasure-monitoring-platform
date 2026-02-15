/**
 * Tutorial 步驟定義
 * 定義引導教學的每個步驟內容和目標元素
 */

export interface TutorialStep {
    id: number;
    target: string;           // CSS選擇器（data-tutorial屬性）
    title: string;            // 標題
    content: string;          // 說明內容
    position: 'top' | 'bottom' | 'left' | 'right';  // 對話框相對目標的位置
}

export const tutorialSteps: TutorialStep[] = [
    {
        id: 1,
        target: '[data-tutorial="player-info"]',
        title: '歡迎回來，冒險者！',
        content: '這裡顯示你的等級、經驗值（XP）、遊戲次數、日記條目和連續登入狀態。完成測驗可獲得 XP，等級越高，代表你對自我情緒的掌控力越強！\n\n⭐ 特別提醒：連續 7 天或當日第 3 次測驗，XP 會翻倍疊加！',
        position: 'right'
    },
    {
        id: 2,
        target: '[data-tutorial="alerts"]',
        title: '⚠️ 最重要的警示燈！',
        content: '🔔 鈴鐺：代表「高分警示」，提醒你分數已超越均線\n\n📉 趨勢圖：「穿線預警」，讓你在心情大幅波動前先做好準備',
        position: 'bottom'
    },
    {
        id: 3,
        target: '[data-tutorial="menu-buttons"]',
        title: '核心功能',
        content: '🚀 開啟冒險：進行失樂感評估，每次冒險需間隔 5 小時（獲得XP獎勵）\n\n📖 英雄日誌：記錄心情點滴，幫助研究團隊與你自己更了解情緒趨勢\n\n📊 冒險成就：查看過往戰績與趨勢圖表\n\n⚙️ 設定：調整你的冒險資料',
        position: 'left'
    },
    {
        id: 4,
        target: '[data-tutorial="daily-mission"]',
        title: '今日任務',
        content: '別忘了查看今日任務，完成它能幫助你更了解情緒變化！',
        position: 'top'
    }
];

/**
 * 獲取總步驟數
 */
export function getTotalSteps(): number {
    return tutorialSteps.length;
}

/**
 * 根據ID獲取步驟
 */
export function getStepById(id: number): TutorialStep | undefined {
    return tutorialSteps.find(step => step.id === id);
}
