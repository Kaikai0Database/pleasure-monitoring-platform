import React from 'react';

interface EmojiOptionProps {
    emoji: string;
    label: string;
    onClick: () => void;
}

export const EmojiOption: React.FC<EmojiOptionProps> = ({ emoji, label, onClick }) => {
    return (
        <button
            onClick={onClick}
            className="
        relative bg-white border-4 border-black p-6
        transition-all duration-200
        hover:translate-y-[-8px] hover:shadow-[8px_8px_0_0_rgba(0,0,0,1)]
        active:translate-y-0 active:shadow-[4px_4px_0_0_rgba(0,0,0,1)]
        flex flex-col items-center gap-2
        min-w-[120px]
      "
        >
            <div className="text-5xl">{emoji}</div>
            <div className="text-xs font-bold">{label}</div>

            {/* Pixel corner decorations */}
            <div className="absolute top-0 left-0 w-2 h-2 bg-gray-800"></div>
            <div className="absolute top-0 right-0 w-2 h-2 bg-gray-800"></div>
            <div className="absolute bottom-0 left-0 w-2 h-2 bg-gray-800"></div>
            <div className="absolute bottom-0 right-0 w-2 h-2 bg-gray-800"></div>
        </button>
    );
};
