import React, { useState } from 'react';
import { PixelButton } from './ui/PixelButton';
import { PixelCard } from './ui/PixelCard';

interface DeleteReasonModalProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: (reason: string) => void;
    isPermanent?: boolean;
}

export const DeleteReasonModal: React.FC<DeleteReasonModalProps> = ({ isOpen, onClose, onConfirm, isPermanent = false }) => {
    const [selectedReason, setSelectedReason] = useState<string>('misclick');
    const [customReason, setCustomReason] = useState<string>('');

    if (!isOpen) return null;

    const handleConfirm = () => {
        let finalReason = '';
        if (selectedReason === 'misclick') {
            finalReason = '誤觸測驗';
        } else {
            finalReason = customReason || '其他原因';
        }
        onConfirm(finalReason);
        // Reset state
        setSelectedReason('misclick');
        setCustomReason('');
        onClose();
    };

    if (isPermanent) {
        return (
            <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
                <PixelCard className="bg-white w-full max-w-md">
                    <h3 className="text-xl font-bold mb-4 text-red-600">永久刪除警告</h3>
                    <p className="mb-6 leading-relaxed">
                        您確定要永久刪除這筆記錄嗎？<br />
                        此動作無法復原！
                    </p>
                    <div className="flex gap-4 justify-end">
                        <PixelButton onClick={onClose} variant="secondary">取消</PixelButton>
                        <PixelButton onClick={() => { onConfirm('permanent'); onClose(); }} variant="danger">確認永久刪除</PixelButton>
                    </div>
                </PixelCard>
            </div>
        );
    }

    return (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
            <PixelCard className="bg-white w-full max-w-md">
                <h3 className="text-xl font-bold mb-4">刪除記錄</h3>
                <p className="mb-4 text-gray-600">請選擇刪除原因：</p>

                <div className="space-y-4 mb-6">
                    <label className="flex items-center gap-3 cursor-pointer">
                        <input
                            type="radio"
                            name="delete-reason"
                            value="misclick"
                            checked={selectedReason === 'misclick'}
                            onChange={(e) => setSelectedReason(e.target.value)}
                            className="w-5 h-5 accent-black"
                        />
                        <span>誤觸測驗</span>
                    </label>

                    <div className="space-y-2">
                        <label className="flex items-center gap-3 cursor-pointer">
                            <input
                                type="radio"
                                name="delete-reason"
                                value="other"
                                checked={selectedReason === 'other'}
                                onChange={(e) => setSelectedReason(e.target.value)}
                                className="w-5 h-5 accent-black"
                            />
                            <span>其他</span>
                        </label>

                        {selectedReason === 'other' && (
                            <textarea
                                value={customReason}
                                onChange={(e) => setCustomReason(e.target.value)}
                                placeholder="請輸入原因..."
                                className="w-full h-24 p-2 border-2 border-black rounded font-pixel resize-none focus:outline-none focus:ring-2 focus:ring-yellow-400"
                                autoFocus
                            />
                        )}
                    </div>
                </div>

                <div className="flex gap-4 justify-end">
                    <PixelButton onClick={onClose} variant="secondary">取消</PixelButton>
                    <PixelButton onClick={handleConfirm} variant="danger">移至回收桶</PixelButton>
                </div>
            </PixelCard>
        </div>
    );
};
