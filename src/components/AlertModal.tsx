import React from 'react';
import type { AlertInfo } from '../types/alert';

interface AlertModalProps {
    alertInfo: AlertInfo | null;
    alertType: 'high' | 'low';
    onClose: () => void;
}

export const AlertModal: React.FC<AlertModalProps> = ({ alertInfo, alertType, onClose }) => {
    // Show modal even if no alert, with a friendly message
    if (!alertInfo) {
        const isHighAlert = alertType === 'high';
        return (
            <div
                className="fixed inset-0 flex items-center justify-center p-4"
                style={{
                    backgroundColor: 'rgba(0, 0, 0, 0.5)',
                    zIndex: 9999,
                    top: 0,
                    left: 0,
                    width: '100vw',
                    height: '100vh'
                }}
            >
                <div
                    className="bg-white p-8 text-center"
                    style={{
                        minHeight: '300px',
                        maxHeight: '70vh',
                        width: '90%',
                        maxWidth: '400px',
                        boxShadow: '12px 12px 0px rgba(0,0,0,0.3), 0 0 0 4px #000',
                        border: '4px solid #000',
                        overflowY: 'auto'
                    }}
                >
                    <div className="text-8xl mb-6">{isHighAlert ? '✅' : '📊'}</div>
                    <h2 className="text-3xl font-bold text-gray-700 mb-6">
                        {isHighAlert ? '分數穩定' : '趨勢良好'}
                    </h2>
                    <p className="text-lg text-gray-600 mb-8">
                        目前數據穩定，無異常預警資訊
                    </p>
                    <button
                        onClick={onClose}
                        style={{
                            background: '#FCD34D',
                            border: '4px solid #000',
                            padding: '16px 48px',
                            fontSize: '24px',
                            fontWeight: 'bold',
                            cursor: 'pointer',
                            boxShadow: '6px 6px 0px #000',
                            marginTop: '20px'
                        }}
                    >
                        我知道了
                    </button>
                </div>
            </div>
        );
    }

    // Extract data from alertInfo
    const exceededLines = Object.entries(alertInfo.exceededLines);

    // Different UI based on alert type
    const isHighAlert = alertType === 'high';

    return (
        <div
            className="fixed inset-0 flex items-center justify-center p-4"
            style={{
                backgroundColor: 'rgba(0, 0, 0, 0.5)',
                zIndex: 9999,
                top: 0,
                left: 0,
                width: '100vw',
                height: '100vh'
            }}
        >
            <div
                className="bg-white p-8"
                style={{
                    minHeight: '400px',
                    maxHeight: '70vh',
                    width: '90%',
                    maxWidth: '400px',
                    boxShadow: '12px 12px 0px rgba(0,0,0,0.3), 0 0 0 4px #000',
                    border: '4px solid #000',
                    overflowY: 'auto'
                }}
            >
                {/* Alert Icon - Large */}
                <div className="text-center mb-6">
                    <div className="text-8xl mb-4">
                        {isHighAlert ? '⚠️' : '📉'}
                    </div>
                    <h2
                        className="text-4xl font-bold mb-6"
                        style={{ color: isHighAlert ? '#DC2626' : '#2563EB' }}
                    >
                        {isHighAlert ? '高分警示' : '穿線預警'}
                    </h2>
                </div>

                {/* Alert Message */}
                <div className="mb-6 space-y-4">
                    <p className="text-xl text-center leading-relaxed">
                        您在{' '}
                        <span className="font-bold" style={{ color: '#9333EA' }}>
                            {new Date(alertInfo.date).toLocaleDateString('zh-TW', {
                                year: 'numeric',
                                month: 'long',
                                day: 'numeric'
                            })}
                        </span>
                        {' '}的平均分數為
                    </p>

                    <p className="text-center mb-6">
                        <span
                            className="text-6xl font-bold"
                            style={{ color: isHighAlert ? '#DC2626' : '#2563EB' }}
                        >
                            {alertInfo.dailyAverage}
                        </span>
                        <span className="text-3xl text-gray-600"> 分</span>
                    </p>

                    {exceededLines.length > 0 && (
                        <div
                            className="rounded-2xl p-6 mb-6"
                            style={{
                                backgroundColor: isHighAlert ? '#FEE2E2' : '#DBEAFE',
                                border: `3px solid ${isHighAlert ? '#FCA5A5' : '#93C5FD'}`
                            }}
                        >
                            <p
                                className="font-bold text-lg mb-3"
                                style={{ color: isHighAlert ? '#DC2626' : '#2563EB' }}
                            >
                                {isHighAlert
                                    ? '高於以下移動平均線：'
                                    : '低於以下移動平均線 3 分以上：'}
                            </p>
                            <ul className="space-y-2">
                                {exceededLines.map(([period, avgScore]) => (
                                    <li
                                        key={period}
                                        className="flex justify-between items-center text-lg font-medium"
                                        style={{ color: isHighAlert ? '#DC2626' : '#2563EB' }}
                                    >
                                        <span>• {period}平均</span>
                                        <span className="font-bold text-xl">{avgScore} 分</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    <p className="text-center text-gray-700 text-lg leading-relaxed px-4">
                        {isHighAlert
                            ? '請注意調整心情，如有需要請尋求協助。'
                            : '您的分數即將接近移動平均線，請留意情緒變化。'}
                    </p>
                </div>

                {/* Close Button - Pixel Style Yellow */}
                <div className="flex justify-center mt-8">
                    <button
                        onClick={onClose}
                        style={{
                            background: '#FCD34D',
                            border: '4px solid #000',
                            padding: '16px 48px',
                            fontSize: '24px',
                            fontWeight: 'bold',
                            cursor: 'pointer',
                            boxShadow: '6px 6px 0px #000',
                            transition: 'transform 0.1s',
                            marginTop: '20px'
                        }}
                        onMouseDown={(e) => {
                            e.currentTarget.style.transform = 'translate(3px, 3px)';
                            e.currentTarget.style.boxShadow = '3px 3px 0px #000';
                        }}
                        onMouseUp={(e) => {
                            e.currentTarget.style.transform = 'translate(0, 0)';
                            e.currentTarget.style.boxShadow = '6px 6px 0px #000';
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.transform = 'translate(0, 0)';
                            e.currentTarget.style.boxShadow = '6px 6px 0px #000';
                        }}
                    >
                        我知道了
                    </button>
                </div>
            </div>
        </div>
    );
};
