import React from 'react';

interface MenuCardProps {
    title: string;
    description: string;
    icon: string;
    onClick?: () => void;
    className?: string;
    disabled?: boolean;
}

export const MenuCard: React.FC<MenuCardProps> = ({
    title,
    description,
    icon,
    onClick,
    className = '',
    disabled = false,
}) => {
    return (
        <div
            onClick={disabled ? undefined : onClick}
            className={`
        pixel-card
        ${disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}
        ${className}
      `}
            style={disabled ? { filter: 'grayscale(100%)' } : undefined}
        >
            <div className="flex flex-col items-center text-center space-y-3">
                <div className="text-4xl pixel-icon-bounce">{icon}</div>
                <h3 className="text-xl font-bold pixel-text-shadow" style={{ color: '#fff' }}>{title}</h3>
                <p className="text-sm opacity-90 pixel-text-readable" style={{ color: '#cbd5e0' }}>{description}</p>
            </div>

            {/* Pixel corner decorations */}
            <div className="absolute top-0 left-0 w-2 h-2 bg-gray-800"></div>
            <div className="absolute top-0 right-0 w-2 h-2 bg-gray-800"></div>
            <div className="absolute bottom-0 left-0 w-2 h-2 bg-gray-800"></div>
            <div className="absolute bottom-0 right-0 w-2 h-2 bg-gray-800"></div>
        </div>
    );
};
