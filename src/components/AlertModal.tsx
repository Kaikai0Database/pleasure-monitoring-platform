import React from 'react';
import { PixelCard } from './ui/PixelCard';
import { PixelButton } from './ui/PixelButton';
import type { ScoreAlert } from '../types/api';

interface AlertModalProps {
    alerts: ScoreAlert[];
    alertType: 'high' | 'low';
    onClose: () => void;
}

export const AlertModal: React.FC<AlertModalProps> = ({ alerts, alertType, onClose }) => {
    if (alerts.length === 0) return null;

    // Get the latest unread alert
    const latestAlert = alerts[0];
    const exceededLines = Object.entries(latestAlert.exceeded_lines);

    // Different UI based on alert type
    const isHighAlert = alertType === 'high';
    const iconEmoji = isHighAlert ? '⚠️' : '📉';
    const titleColor = isHighAlert ? 'text-red-600' : 'text-blue-600';
    const bgColor = isHighAlert ? 'bg-red-50' : 'bg-blue-50';
    const borderColor = isHighAlert ? 'border-red-200' : 'border-blue-200';
    const textColor = isHighAlert ? 'text-red-800' : 'text-blue-800';
    const valueColor = isHighAlert ? 'text-red-600' : 'text-blue-600';
    const lineTextColor = isHighAlert ? 'text-red-700' : 'text-blue-700';

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <PixelCard className="bg-white max-w-md w-full">
                <div className="p-6">
                    {/* Alert Icon */}
                    <div className="text-center mb-4">
                        <div className="text-6xl mb-2">{iconEmoji}</div>
                        <h2 className={`text-2xl font-bold ${titleColor}`}>
                            {isHighAlert ? '高分警示' : '穿線預警'}
                        </h2>
                    </div>

                    {/* Alert Message */}
                    <div className="mb-6 space-y-3">
                        <p className="text-lg text-center">
                            您在 <span className="font-bold text-purple-600">
                                {new Date(latestAlert.alert_date).toLocaleDateString('zh-TW', {
                                    year: 'numeric',
                                    month: 'long',
                                    day: 'numeric'
                                })}
                            </span> 的平均分數為
                        </p>

                        <p className="text-center">
                            <span className={`text-4xl font-bold ${valueColor}`}>
                                {latestAlert.daily_average}
                            </span>
                            <span className="text-xl text-gray-600"> 分</span>
                        </p>

                        {exceededLines.length > 0 && (
                            <div className={`${bgColor} border-2 ${borderColor} rounded-lg p-4`}>
                                <p className={`font-semibold ${textColor} mb-2`}>
                                    {isHighAlert
                                        ? '高於以下移動平均線：'
                                        : '低於以下移動平均線 3 分以上：'}
                                </p>
                                <ul className="space-y-1">
                                    {exceededLines.map(([period, avgScore]) => (
                                        <li key={period} className={`flex justify-between items-center ${lineTextColor}`}>
                                            <span>• {period}平均</span>
                                            <span className="font-bold">{avgScore} 分</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        <p className="text-center text-gray-600 text-sm mt-4">
                            {isHighAlert
                                ? '請注意調整心情，如有需要請尋求協助。'
                                : '您的分數即將接近移動平均線，請留意情緒變化。'}
                        </p>
                    </div>

                    {/* Close Button */}
                    <div className="flex justify-center">
                        <PixelButton onClick={onClose} variant="primary" className="px-8">
                            我知道了
                        </PixelButton>
                    </div>
                </div>
            </PixelCard>
        </div>
    );
};
