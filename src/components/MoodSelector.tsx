import React from 'react';
import { MOODS, PERIOD_MARKER } from '../types/diary';

interface MoodSelectorProps {
    selectedMood: string;
    onMoodSelect: (moodKey: string) => void;
    periodMarker: boolean;
    onPeriodToggle: (marked: boolean) => void;
}

export const MoodSelector: React.FC<MoodSelectorProps> = ({
    selectedMood,
    onMoodSelect,
    periodMarker,
    onPeriodToggle,
}) => {
    return (
        <>
            <style>{`
                /* MoodSelector Mobile Responsive Styles */
                @media (max-width: 600px) {
                    /* Prevent mood icon squishing */
                    .mood-icon {
                        flex-shrink: 0;
                        min-width: 48px;
                        width: 48px !important;
                        height: 48px !important;
                        aspect-ratio: 1 / 1;
                    }
                    
                    /* Mood button container */
                    .mood-button {
                        padding: 0.75rem !important;
                    }
                    
                    /* Mood grid responsive */
                    .mood-grid {
                        gap: 0.75rem !important;
                    }
                    
                    /* Period marker icon */
                    .period-icon {
                        flex-shrink: 0;
                        min-width: 40px;
                        width: 40px !important;
                        height: 40px !important;
                        aspect-ratio: 1 / 1;
                    }
                }
                
                @media (max-width: 480px) {
                    .mood-icon {
                        width: 40px !important;
                        height: 40px !important;
                    }
                    
                    .mood-grid {
                        gap: 0.5rem !important;
                    }
                    
                    .period-icon {
                        width: 36px !important;
                        height: 36px !important;
                    }
                }
            `}</style>
            <div className="space-y-6">
                <div>
                    <h3 className="text-xl font-bold mb-4">今天的心情是？</h3>
                    <div className="grid grid-cols-3 gap-4 mood-grid">
                        {MOODS.map((mood) => (
                            <button
                                key={mood.key}
                                onClick={() => onMoodSelect(mood.key)}
                                className={`
                p-4 border-4 rounded-lg transition-all hover:scale-105
                flex flex-col items-center justify-center gap-2 mood-button
                ${selectedMood === mood.key
                                        ? 'border-yellow-500 bg-yellow-50'
                                        : 'border-gray-300 bg-white hover:border-yellow-300'
                                    }
              `}
                            >
                                <img
                                    src={mood.icon}
                                    alt={mood.name}
                                    className="w-16 h-16 pixelated mood-icon"
                                />
                                <span className="font-medium text-sm">{mood.name}</span>
                            </button>
                        ))}
                    </div>
                </div>

                {/* 生理期標記 */}
                <div className="border-t-4 border-gray-200 pt-4">
                    <button
                        onClick={() => onPeriodToggle(!periodMarker)}
                        className={`
            w-full p-4 border-4 rounded-lg transition-all hover:scale-102
            flex items-center justify-center gap-3
            ${periodMarker
                                ? 'border-pink-500 bg-pink-50'
                                : 'border-gray-300 bg-white hover:border-pink-300'
                            }
          `}
                    >
                        <img
                            src={PERIOD_MARKER.icon}
                            alt={PERIOD_MARKER.name}
                            className="w-12 h-12 pixelated period-icon"
                        />
                        <span className="font-medium">{PERIOD_MARKER.name}</span>
                        {periodMarker && (
                            <span className="ml-2 text-pink-600">✓</span>
                        )}
                    </button>
                </div>
            </div>
        </>
    );
};
