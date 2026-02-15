/**
 * 趨勢指標組件 - 顯示警報 Icon
 * 用於列表頁面的視覺化回饋
 */

import React from 'react';
import './TrendIndicator.css';

export interface TrendIndicatorProps {
    hasHighAlert?: boolean;  // 穿線警報
    hasLowAlert?: boolean;   // 接近線警報
    alertLines?: string[];   // 觸發的均線
}

export const TrendIndicator: React.FC<TrendIndicatorProps> = ({
    hasHighAlert,
    hasLowAlert,
    alertLines = [],
}) => {
    if (!hasHighAlert && !hasLowAlert) {
        return null;
    }

    return (
        <div className="trend-indicators">
            {hasHighAlert && (
                <span
                    className="trend-icon trend-high-alert"
                    title={`穿越警報: ${alertLines.join('、')}`}
                >
                    📈
                </span>
            )}

            {hasLowAlert && (
                <span
                    className="trend-icon trend-low-alert"
                    title={`接近警報: ${alertLines.join('、')}`}
                >
                    ⚠️
                </span>
            )}
        </div>
    );
};

/**
 * 簡化版 - 僅用於快速判斷是否有警報
 */
export const hasAnyAlert = (highAlert: boolean, lowAlert: boolean): boolean => {
    return highAlert || lowAlert;
};
