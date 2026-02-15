/**
 * 自定義 Tooltip 組件
 * 顯示當日分數和三條 MA 線的數值
 */

import React from 'react';

export const CustomMATooltip: React.FC<any> = ({
    active,
    payload,
    label,
}) => {
    if (!active || !payload || payload.length === 0) {
        return null;
    }

    return (
        <div
            style={{
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                border: '1px solid #ddd',
                borderRadius: '6px',
                padding: '12px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
            }}
        >
            <p style={{ margin: '0 0 8px 0', fontWeight: '600', fontSize: '14px' }}>
                {label}
            </p>

            {payload.map((entry: any, index: number) => {
                let color = '#999';
                const label = entry.name;

                // 根據數據系列設置顏色
                if (entry.dataKey === '當日分數') {
                    color = '#f59e0b';  // 橘色
                } else if (entry.dataKey === '7日平均') {
                    color = '#667eea';  // 藍色
                } else if (entry.dataKey === '14日平均') {
                    color = '#48bb78';  // 綠色
                } else if (entry.dataKey === '30日平均') {
                    color = '#9f7aea';  // 紫色
                }

                return (
                    <p
                        key={index}
                        style={{
                            margin: '4px 0',
                            fontSize: '13px',
                            color,
                            fontWeight: '500',
                        }}
                    >
                        {label}: {entry.value !== null && entry.value !== undefined ? Number(entry.value).toFixed(1) : '-'}
                    </p>
                );
            })}
        </div>
    );
};
