import React from 'react';

interface EmojiOptionProps {
    emoji: string;
    label: string;
    onClick: () => void;
}

export const EmojiOption: React.FC<EmojiOptionProps> = ({ emoji, label, onClick }) => {
    return (
        <>
            <style>{`
                /* Emoji Option Mobile Optimization */
                @media (max-width: 600px) {
                    .emoji-option-label {
                        font-size: 0.9rem !important;
                    }
                    
                    .emoji-option-emoji {
                        font-size: 3rem !important;
                    }
                }
                
                @media (max-width: 400px) {
                    .emoji-option-label {
                        font-size: 0.8rem !important;
                    }
                    
                    .emoji-option-emoji {
                        font-size: 2.5rem !important;
                    }
                }
            `}</style>
            <button
                onClick={onClick}
                className="
            relative bg-white border-4 border-black p-6
            transition-all duration-200
            hover:translate-y-[-8px] hover:shadow-[8px_8px_0_0_rgba(0,0,0,1)]
            active:translate-y-0 active:shadow-[4px_4px_0_0_rgba(0,0,0,1)]
          "
                style={{
                    width: '100%',
                    aspectRatio: '1 / 1.1',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center',
                    alignItems: 'center',
                    gap: '0.5rem'
                }}
            >
                <div className="text-5xl emoji-option-emoji">{emoji}</div>
                <div className="text-xs font-bold emoji-option-label">{label}</div>

                {/* Pixel corner decorations */}
                <div className="absolute top-0 left-0 w-2 h-2 bg-gray-800"></div>
                <div className="absolute top-0 right-0 w-2 h-2 bg-gray-800"></div>
                <div className="absolute bottom-0 left-0 w-2 h-2 bg-gray-800"></div>
                <div className="absolute bottom-0 right-0 w-2 h-2 bg-gray-800"></div>
            </button>
        </>
    );
};
