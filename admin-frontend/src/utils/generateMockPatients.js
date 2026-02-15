/**
 * Mock Patient Data Generator
 * 生成測試用病人數據
 * 
 * 執行方式：node src/utils/generateMockPatients.js
 * 或在瀏覽器 console 中直接執行 generateMockPatients() 函數
 */

// 隨機中文姓氏
const lastNames = [
    '王', '李', '張', '劉', '陳', '楊', '黃', '趙', '吳', '周',
    '徐', '孫', '馬', '朱', '胡', '郭', '何', '高', '林', '羅',
    '鄭', '梁', '謝', '宋', '唐', '許', '韓', '馮', '鄧', '曹'
];

// 隨機中文名字
const firstNames = [
    '明', '華', '強', '偉', '芳', '娟', '敏', '靜', '麗', '軍',
    '杰', '勇', '磊', '濤', '超', '婷', '雪', '梅', '玲', '紅',
    '宇', '浩', '欣', '怡', '雅', '詩', '曉', '雨', '晨', '陽'
];

// 病人狀態
const statuses = ['正常', '需追蹤', '高風險', '穩定', '待評估'];

/**
 * 生成 UUID v4
 */
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

/**
 * 生成隨機中文姓名
 */
function generateChineseName() {
    const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
    const firstName1 = firstNames[Math.floor(Math.random() * firstNames.length)];
    const firstName2 = Math.random() > 0.5 ? firstNames[Math.floor(Math.random() * firstNames.length)] : '';
    return lastName + firstName1 + firstName2;
}

/**
 * 生成隨機日期（過去一年內）
 */
function generateAdmissionDate() {
    const now = new Date();
    const oneYearAgo = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate());
    const randomTime = oneYearAgo.getTime() + Math.random() * (now.getTime() - oneYearAgo.getTime());
    return new Date(randomTime).toISOString().split('T')[0]; // YYYY-MM-DD 格式
}

/**
 * 根據分數決定狀態
 */
function determineStatus(score) {
    if (score >= 80) return '正常';
    if (score >= 60) return '需追蹤';
    if (score >= 40) return '穩定';
    if (score >= 20) return '待評估';
    return '高風險';
}

/**
 * 生成單筆病人數據
 */
function generateMockPatient(index) {
    const score = Math.floor(Math.random() * 101); // 0-100
    const age = 18 + Math.floor(Math.random() * 62); // 18-80
    const gender = Math.random() > 0.5 ? '男' : '女';

    return {
        id: generateUUID(),
        name: generateChineseName(),
        age: age,
        gender: gender,
        last_assessment_score: score,
        status: determineStatus(score),
        admission_date: generateAdmissionDate(),
        // 額外資訊
        patient_number: `P${String(index + 1).padStart(4, '0')}`, // P0001, P0002...
        email: `patient${index + 1}@test.com`,
        phone: `09${Math.floor(Math.random() * 100000000).toString().padStart(8, '0')}`
    };
}

/**
 * 生成多筆病人數據
 * @param {number} count - 要生成的病人數量（默認 20）
 */
function generateMockPatients(count = 20) {
    const patients = [];
    for (let i = 0; i < count; i++) {
        patients.push(generateMockPatient(i));
    }
    return patients;
}

/**
 * 主函數 - 生成並輸出 JSON
 */
function main() {
    const patientCount = 30; // 生成 30 筆測試數據
    const mockPatients = generateMockPatients(patientCount);

    console.log('='.repeat(60));
    console.log(`生成了 ${patientCount} 筆測試病人數據`);
    console.log('='.repeat(60));
    console.log(JSON.stringify(mockPatients, null, 2));
    console.log('='.repeat(60));

    return mockPatients;
}

// 如果在 Node.js 環境執行
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        generateMockPatients,
        generateMockPatient,
        generateChineseName,
        generateUUID
    };

    // 直接執行腳本時生成數據
    if (require.main === module) {
        main();
    }
}

// 如果在瀏覽器環境
if (typeof window !== 'undefined') {
    window.generateMockPatients = generateMockPatients;
    console.log('✅ Mock data generator loaded! Use: generateMockPatients(20)');
}
