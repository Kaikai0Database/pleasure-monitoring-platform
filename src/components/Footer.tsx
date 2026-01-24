import React from 'react';

export const Footer: React.FC = () => {
    return (
        <footer className="w-full py-4 bg-transparent text-center">
            <p className="text-gray-500 text-sm font-pixel">
                © 2025 智慧醫療轉譯及創新實驗室擁有版權與 CN Lab 共同並協助開發
            </p>
            <p className="text-gray-400 text-xs mt-1 font-pixel">
                版本 0.2（測試版）
            </p>
        </footer>
    );
};
