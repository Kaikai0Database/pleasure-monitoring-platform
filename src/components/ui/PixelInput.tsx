import React from 'react';
import { cn } from '../../lib/utils';

interface PixelInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
    endIcon?: React.ReactNode;
}

export const PixelInput: React.FC<PixelInputProps> = ({ className, endIcon, ...props }) => {
    return (
        <div className="relative">
            <input
                className={cn(
                    'w-full px-4 py-2 font-pixel text-sm border-4 border-gray-800 focus:outline-none focus:border-blue-500',
                    'placeholder:text-gray-400',
                    endIcon && 'pr-10',
                    className
                )}
                {...props}
            />
            {endIcon && (
                <div className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500">
                    {endIcon}
                </div>
            )}
        </div>
    );
};
