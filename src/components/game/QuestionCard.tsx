import React from 'react';

interface QuestionCardProps {
    questionNumber: number;
    totalQuestions: number;
    questionText: string;
}

export const QuestionCard: React.FC<QuestionCardProps> = ({
    questionNumber,
    totalQuestions,
    questionText,
}) => {
    return (
        <div className="w-full max-w-3xl mx-auto">
            {/* Progress indicator */}
            <div className="mb-6 flex items-center gap-4">
                <div className="flex-1 h-6 bg-gray-300 border-4 border-black relative overflow-hidden">
                    <div
                        className="h-full bg-gradient-to-r from-blue-400 to-purple-500 transition-all duration-500"
                        style={{ width: `${(questionNumber / totalQuestions) * 100}%` }}
                    >
                        <div className="h-full w-full bg-[repeating-linear-gradient(90deg,transparent,transparent_4px,rgba(0,0,0,0.1)_4px,rgba(0,0,0,0.1)_8px)]"></div>
                    </div>
                </div>
                <div className="text-xl font-bold whitespace-nowrap">
                    {questionNumber}/{totalQuestions}
                </div>
            </div>

            {/* Question dialog box */}
            <div className="relative bg-white border-4 border-black p-8 shadow-[8px_8px_0_0_rgba(0,0,0,1)]">
                {/* Question text */}
                <p className="text-2xl leading-relaxed text-center font-bold">
                    {questionText}
                </p>

                {/* Pixel corner decorations */}
                <div className="absolute top-0 left-0 w-3 h-3 bg-gray-800"></div>
                <div className="absolute top-0 right-0 w-3 h-3 bg-gray-800"></div>
                <div className="absolute bottom-0 left-0 w-3 h-3 bg-gray-800"></div>
                <div className="absolute bottom-0 right-0 w-3 h-3 bg-gray-800"></div>
            </div>
        </div>
    );
};
