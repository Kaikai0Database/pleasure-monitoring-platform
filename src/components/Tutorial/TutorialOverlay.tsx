import React from 'react';

/**
 * Tutorial 遮罩層
 * 半透明黑色背景，保持底層RPG動畫可見
 */
export const TutorialOverlay: React.FC = () => {
    return (
        <div
            className="fixed inset-0 z-[9998]"
            style={{
                backgroundColor: 'rgba(0, 0, 0, 0.6)',
                pointerEvents: 'none'
            }}
        />
    );
};
