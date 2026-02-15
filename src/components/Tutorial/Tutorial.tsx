import React from 'react';
import { TutorialOverlay } from './TutorialOverlay';
import { TutorialSpotlight } from './TutorialSpotlight';
import { TutorialDialog } from './TutorialDialog';
import { tutorialSteps } from './tutorialSteps';

interface TutorialProps {
    isActive: boolean;
    currentStep: number;
    onNext: () => void;
    onPrev: () => void;
    onClose: () => void;
}

/**
 * Tutorial 主組件
 * 整合遮罩、聚光燈和對話框
 */
export const Tutorial: React.FC<TutorialProps> = ({
    isActive,
    currentStep,
    onNext,
    onPrev,
    onClose
}) => {
    if (!isActive) return null;

    const step = tutorialSteps[currentStep];

    if (!step) {
        console.error(`❌ [Tutorial] 無效的步驟索引: ${currentStep}`);
        return null;
    }

    return (
        <>
            {/* 半透明遮罩 */}
            <TutorialOverlay />

            {/* 高亮聚光燈 */}
            <TutorialSpotlight targetSelector={step.target} />

            {/* 教學對話框 */}
            <TutorialDialog
                step={step}
                currentStep={currentStep}
                totalSteps={tutorialSteps.length}
                onNext={onNext}
                onPrev={onPrev}
                onClose={onClose}
            />
        </>
    );
};
