import React from 'react';
import { cn } from '../../lib/utils';
import { motion, type HTMLMotionProps } from 'framer-motion';

interface PixelCardProps extends HTMLMotionProps<"div"> { }

export const PixelCard: React.FC<PixelCardProps> = ({ className, children, ...props }) => {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className={cn(
                'bg-white p-6 border-4 border-gray-800 shadow-[8px_8px_0_0_rgba(0,0,0,1)]',
                className
            )}
            {...props}
        >
            {children}
        </motion.div>
    );
};
