import React, { createContext, useContext, useState, useEffect } from 'react';

export type FontSize = 'small' | 'medium' | 'large' | 'extra-large';

interface FontSizeContextType {
    fontSize: FontSize;
    setFontSize: (size: FontSize) => void;
    fontSizeLabel: string;
    fontSizePixels: number;
}

const FontSizeContext = createContext<FontSizeContextType | undefined>(undefined);

export const useFontSize = () => {
    const context = useContext(FontSizeContext);
    if (!context) {
        throw new Error('useFontSize must be used within FontSizeProvider');
    }
    return context;
};

const fontSizeMap: Record<FontSize, { label: string; pixels: number; scale: number }> = {
    'small': { label: '小', pixels: 18, scale: 0.818 },
    'medium': { label: '中', pixels: 22, scale: 1.0 },
    'large': { label: '大', pixels: 28, scale: 1.273 },
    'extra-large': { label: '特大', pixels: 32, scale: 1.455 },
};

export const FontSizeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [fontSize, setFontSizeState] = useState<FontSize>('medium');

    useEffect(() => {
        // Load saved font size from localStorage
        const savedFontSize = localStorage.getItem('font_size') as FontSize;
        if (savedFontSize && fontSizeMap[savedFontSize]) {
            setFontSizeState(savedFontSize);
            applyFontSize(savedFontSize);
        } else {
            // Apply default font size on first load
            applyFontSize('medium');
        }
    }, []);

    const applyFontSize = (size: FontSize) => {
        const { pixels, scale } = fontSizeMap[size];
        // Set CSS custom properties on the root element
        document.documentElement.style.setProperty('--base-font-size', `${pixels}px`);
        document.documentElement.style.setProperty('--font-scale', scale.toString());
    };

    const setFontSize = (size: FontSize) => {
        setFontSizeState(size);
        applyFontSize(size);
        localStorage.setItem('font_size', size);
    };

    const value: FontSizeContextType = {
        fontSize,
        setFontSize,
        fontSizeLabel: fontSizeMap[fontSize].label,
        fontSizePixels: fontSizeMap[fontSize].pixels,
    };

    return (
        <FontSizeContext.Provider value={value}>
            {children}
        </FontSizeContext.Provider>
    );
};
