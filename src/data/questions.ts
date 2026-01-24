export interface Question {
    id: number;
    text: string;
    background: string; // CSS background value (gradient or url())
}

export interface Answer {
    questionId: number;
    emoji: string;
    score: number;
}

export const EMOJI_OPTIONS = [
    { emoji: '😄', label: '非常同意', score: 1 },
    { emoji: '😐', label: '同意', score: 2 },
    { emoji: '😟', label: '不同意', score: 3 },
    { emoji: '😭', label: '非常不同意', score: 4 },
];

export const questions: Question[] = [
    {
        id: 1,
        text: '欣賞我喜愛的電視或廣播節目，我會很愉快。',
        background: 'url(/backgrounds/Q1.png)',
    },
    {
        id: 2,
        text: '我會很欣賞精心打扮後看起來很漂亮的我。',
        background: 'url(/backgrounds/Q2.png)',
    },
    {
        id: 3,
        text: '受到他人稱讚時，我會感到快樂。',
        background: 'url(/backgrounds/Q3.png)',
    },
    {
        id: 4,
        text: '我會從幫助他人中得到快樂。',
        background: 'url(/backgrounds/Q4.png)',
    },
    {
        id: 5,
        text: '我會很享受美麗的風景或景色。',
        background: 'url(/backgrounds/Q5.png)',
    },
    {
        id: 6,
        text: '我會從一些小事中找到樂趣，比如陽光明媚的日子或者一個朋友的電話。',
        background: 'url(/backgrounds/Q6.png)',
    },
    {
        id: 7,
        text: '我會很享受喝一杯茶，咖啡，或者我喜歡的飲料。',
        background: 'url(/backgrounds/Q7.png)',
    },
    {
        id: 8,
        text: '我很享受閱讀書籍、雜誌或者報紙的樂趣。',
        background: 'url(/backgrounds/Q8.png)',
    },
    {
        id: 9,
        text: '我喜歡看到別人的笑臉。',
        background: 'url(/backgrounds/Q9.png)',
    },
    {
        id: 10,
        text: '花的香味、清新的海風氣息或者新鮮的烤麵包味會讓我感到很快樂。',
        background: 'url(/backgrounds/Q10.png)',
    },
    {
        id: 11,
        text: '泡個熱水澡或來個使人清爽的淋浴，我會很愉快。',
        background: 'url(/backgrounds/Q11.png)',
    },
    {
        id: 12,
        text: '我能津津有味地享受我喜歡的菜餚。',
        background: 'url(/backgrounds/Q12.png)',
    },
    {
        id: 13,
        text: '我會從我的愛好和娛樂活動中找到快樂。',
        background: 'url(/backgrounds/Q13.png)',
    },
    {
        id: 14,
        text: '我很享受與家人或親密朋友在一起的快樂時時光。',
        background: 'url(/backgrounds/Q14.png)',
    },
];

export const calculateScore = (answers: Answer[]): number => {
    return answers.reduce((total, answer) => total + answer.score, 0);
};

export const getScoreInterpretation = (score: number, backendLevel?: string): {
    level: string;
    message: string;
    color: string;
} => {
    // 如果後端有提供等級，直接使用後端的判定結果
    if (backendLevel) {
        if (backendLevel === '良好') {
            return {
                level: '良好',
                message: '您目前的心理狀態良好，能夠從日常生活中獲得快樂和滿足感。繼續保持積極的生活態度！',
                color: 'bg-green-500',
            };
        } else {
            return {
                level: '需要關注',
                message: '您可能正經歷較低的快樂感受。建議尋求專業心理諮詢，與親友交流，或培養新的興趣愛好。',
                color: 'bg-red-500',
            };
        }
    }

    // 後備邏輯（以前端預設值為準，預設為學校標準 23）
    // 注意：這僅在無法獲取後端等級時使用
    if (score < 23) {
        return {
            level: '良好',
            message: '您目前的心理狀態良好，能夠從日常生活中獲得快樂和滿足感。繼續保持積極的生活態度！',
            color: 'bg-green-500',
        };
    } else {
        return {
            level: '需要關注',
            message: '您可能正經歷較低的快樂感受。建議尋求專業心理諮詢，與親友交流，或培養新的興趣愛好。',
            color: 'bg-red-500',
        };
    }
};
