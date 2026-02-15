import React from 'react';

export const Footer: React.FC = () => {
    return (
        <>
            <style>{`
                /* Footer Mobile Optimization */
                @media (max-width: 600px) {
                    .footer-copyright {
                        font-size: 0.75rem !important;
                    }
                    
                    .footer-version {
                        font-size: 0.7rem !important;
                    }
                }
            `}</style>
            <footer
                className="w-full bg-transparent text-center"
                style={{
                    padding: '20px 0',
                    width: '90%',
                    margin: '0 auto'
                }}
            >
                <p className="text-gray-500 text-sm font-pixel footer-copyright">
                    © 2025 智慧醫療轉譯及創新實驗室擁有版權與 CN Lab 共同並協助開發
                </p>
                <p className="text-gray-400 text-xs mt-1 font-pixel footer-version">
                    版本 0.2（測試版）
                </p>
            </footer>
        </>
    );
};
