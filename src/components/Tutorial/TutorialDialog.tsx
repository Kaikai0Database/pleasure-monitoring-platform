import React from 'react';
import type { TutorialStep } from './tutorialSteps';

interface TutorialDialogProps {
    step: TutorialStep;
    currentStep: number;
    totalSteps: number;
    onNext: () => void;
    onPrev: () => void;
    onClose: () => void;
}

/**
 * Tutorial 對話框
 * 像素風格對話框，顯示教學內容和導航按鈕
 * 優化版：使用 Flexbox 布局，內容區域獨立滾動
 */
export const TutorialDialog: React.FC<TutorialDialogProps> = ({
    step,
    currentStep,
    totalSteps,
    onNext,
    onPrev,
    onClose
}) => {
    // 智慧對話框定位：步驟3（核心功能按鈕，index 2）移到上方，避免遮擋底部按鈕
    const dialogStyle: React.CSSProperties = currentStep === 2  // 步驟3（index 2）
        ? {
            position: 'fixed',
            top: '15%',
            left: '50%',
            transform: 'translateX(-50%)',
            maxWidth: '600px',
            width: '90%'
        }
        : {
            position: 'fixed',
            bottom: '80px',
            left: '50%',
            transform: 'translateX(-50%)',
            maxWidth: '600px',
            width: '90%'
        };

    return (
        <div
            className="z-[10000] bg-white border-8 border-black shadow-[12px_12px_0px_rgba(0,0,0,1)]"
            style={{
                ...dialogStyle,
                maxHeight: '80vh',
                height: 'auto',
                display: 'flex',
                flexDirection: 'column',
                padding: '24px',
                paddingBottom: 'calc(24px + env(safe-area-inset-bottom))',
            }}
        >
            <style>{`
                /* Custom scrollbar styling for pixel art aesthetic */
                .tutorial-content-scroll::-webkit-scrollbar {
                    width: 6px;
                }
                .tutorial-content-scroll::-webkit-scrollbar-track {
                    background: transparent;
                }
                .tutorial-content-scroll::-webkit-scrollbar-thumb {
                    background: #9CA3AF;
                    border-radius: 3px;
                }
                .tutorial-content-scroll::-webkit-scrollbar-thumb:hover {
                    background: #6B7280;
                }
                /* Firefox scrollbar */
                .tutorial-content-scroll {
                    scrollbar-width: thin;
                    scrollbar-color: #9CA3AF transparent;
                }
            `}</style>

            {/* 小飛船助手 - 固定位置，不參與滾動 */}
            <div className="absolute -top-16 left-1/2 -translate-x-1/2 text-6xl animate-bounce">
                🚀
            </div>

            {/* 標題 - 固定位置，不滾動 */}
            <h3
                className="text-xl font-bold mb-4 text-purple-800 flex-shrink-0"
                style={{ fontFamily: '"Press Start 2P", monospace', fontSize: '16px', lineHeight: '1.6' }}
            >
                {step.title}
            </h3>

            {/* 內容區域 - 可滾動，flex-grow 佔據剩餘空間 */}
            <div
                className="tutorial-content-scroll flex-grow overflow-y-auto mb-4"
                style={{
                    minHeight: '0', // 重要：允許 flex item 縮小
                }}
            >
                <div
                    className="text-sm leading-relaxed whitespace-pre-line pr-2"
                    style={{ fontFamily: 'Arial, sans-serif' }}
                >
                    {step.content}
                </div>
            </div>

            {/* 進度指示器 - 固定位置，不滾動 */}
            <div className="flex gap-2 justify-center mb-4 flex-shrink-0">
                {Array.from({ length: totalSteps }).map((_, index) => (
                    <div
                        key={index}
                        className={`w-3 h-3 border-2 border-black transition-all ${index === currentStep ? 'bg-purple-600 scale-125' : 'bg-gray-300'
                            }`}
                    />
                ))}
            </div>

            {/* 按鈕區域 - 固定位置，不滾動 */}
            <div className="flex gap-4 flex-shrink-0">
                {currentStep > 0 && (
                    <button
                        onClick={onPrev}
                        className="flex-1 px-4 py-3 bg-gray-300 border-4 border-black font-bold hover:bg-gray-400 transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] active:shadow-none active:translate-x-[4px] active:translate-y-[4px]"
                        style={{ fontFamily: '"Press Start 2P", monospace', fontSize: '12px' }}
                    >
                        ← 上一步
                    </button>
                )}

                {currentStep < totalSteps - 1 ? (
                    <button
                        onClick={onNext}
                        className="flex-1 px-4 py-3 bg-yellow-400 border-4 border-black font-bold hover:bg-yellow-500 transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] active:shadow-none active:translate-x-[4px] active:translate-y-[4px]"
                        style={{ fontFamily: '"Press Start 2P", monospace', fontSize: '12px' }}
                    >
                        下一步 →
                    </button>
                ) : (
                    <button
                        onClick={onClose}
                        className="flex-1 px-4 py-3 bg-green-400 border-4 border-black font-bold hover:bg-green-500 transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] active:shadow-none active:translate-x-[4px] active:translate-y-[4px]"
                        style={{ fontFamily: '"Press Start 2P", monospace', fontSize: '12px' }}
                    >
                        開始冒險！
                    </button>
                )}
            </div>

            {/* 跳過按鈕 - 固定位置，不滾動 */}
            <button
                onClick={onClose}
                className="mt-3 w-full text-xs text-gray-500 hover:text-gray-700 transition-colors flex-shrink-0"
                style={{ fontFamily: 'Arial, sans-serif' }}
            >
                跳過教學
            </button>
        </div>
    );
};
