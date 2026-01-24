import React from 'react';
import { motion, type HTMLMotionProps } from 'framer-motion';
import { cn } from '../../lib/utils';

interface PixelButtonProps extends HTMLMotionProps<"button"> {
    variant?: 'primary' | 'secondary' | 'danger';
    isLoading?: boolean;
    size?: 'sm' | 'md' | 'lg';
}

export const PixelButton: React.FC<PixelButtonProps> = ({
    className,
    variant = 'primary',
    children,
    isLoading = false,
    size = 'md',
    disabled,
    ...props
}) => {
    const baseStyles = "relative font-bold font-pixel transition-all disabled:opacity-50 disabled:cursor-not-allowed";

    // Pixel border styles
    const borderStyles = "border-b-4 border-r-4 border-t-2 border-l-2";

    const sizeStyles = {
        sm: "px-4 py-2 text-sm",
        md: "px-8 py-4 text-xl",
        lg: "px-10 py-5 text-2xl",
    };

    const variants = {
        primary: "bg-yellow-400 hover:bg-yellow-300 text-black border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] active:shadow-none",
        secondary: "bg-white hover:bg-gray-50 text-black border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] active:shadow-none",
        danger: "bg-red-500 hover:bg-red-400 text-white border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] active:shadow-none",
    };

    return (
        <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className={cn(
                baseStyles,
                borderStyles,
                variants[variant],
                sizeStyles[size],
                className
            )}
            disabled={disabled || isLoading}
            {...props}
        >
            {children}
        </motion.button>
    );
};
