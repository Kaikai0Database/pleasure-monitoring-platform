import React, { useEffect, useState } from 'react';

interface TutorialSpotlightProps {
    targetSelector: string;
}

/**
 * Tutorial 聚光燈
 * 白色脈衝邊框，高亮目標元素
 */
export const TutorialSpotlight: React.FC<TutorialSpotlightProps> = ({
    targetSelector
}) => {
    const [position, setPosition] = useState({
        top: 0,
        left: 0,
        width: 0,
        height: 0
    });
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        // 等待DOM渲染完成
        const timer = setTimeout(() => {
            const target = document.querySelector(targetSelector);
            if (target) {
                const rect = target.getBoundingClientRect();
                setPosition({
                    top: rect.top - 8,
                    left: rect.left - 8,
                    width: rect.width + 16,
                    height: rect.height + 16
                });
                setIsVisible(true);
            } else {
                console.warn(`⚠️ [Tutorial] 找不到目標元素: ${targetSelector}`);
            }
        }, 100);

        return () => clearTimeout(timer);
    }, [targetSelector]);

    if (!isVisible) return null;

    return (
        <div
            className="fixed z-[9999] border-4 border-white rounded-lg transition-all duration-500 ease-in-out"
            style={{
                top: `${position.top}px`,
                left: `${position.left}px`,
                width: `${position.width}px`,
                height: `${position.height}px`,
                boxShadow: '0 0 30px rgba(255,255,255,1), 0 0 60px rgba(255,255,255,0.8), inset 0 0 20px rgba(255,255,255,0.3)',
                animation: 'pulse-border 2s ease-in-out infinite',
                pointerEvents: 'none',  // 不阻擋點擊
                backgroundColor: 'transparent'  // 確保高亮區域完全透明
            }}
        />
    );
};
