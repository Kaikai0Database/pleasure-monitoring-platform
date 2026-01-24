import React from 'react';

interface MenuCardProps {
    title: string;
    description: string;
    icon: string;
    onClick?: () => void;
    className?: string;
}

export const MenuCard: React.FC<MenuCardProps> = ({
    title,
    description,
    icon,
    onClick,
    className = '',
}) => {
    return (
        <div
            onClick={onClick}
            className={`
        relative bg-white border-4 border-black p-6 
        cursor-pointer
        transition-all duration-200
        hover:translate-y-[-4px] hover:shadow-[8px_8px_0_0_rgba(0,0,0,1)]
        active:translate-y-0 active:shadow-[4px_4px_0_0_rgba(0,0,0,1)]
        ${className}
      `}
        >
            <div className="flex flex-col items-center text-center space-y-3">
                <div className="text-4xl">{icon}</div>
                <h3 className="text-xl font-bold">{title}</h3>
                <p className="text-sm opacity-80">{description}</p>
            </div>

            {/* Pixel corner decorations */}
            <div className="absolute top-0 left-0 w-2 h-2 bg-gray-800"></div>
            <div className="absolute top-0 right-0 w-2 h-2 bg-gray-800"></div>
            <div className="absolute bottom-0 left-0 w-2 h-2 bg-gray-800"></div>
            <div className="absolute bottom-0 right-0 w-2 h-2 bg-gray-800"></div>
        </div>
    );
};
