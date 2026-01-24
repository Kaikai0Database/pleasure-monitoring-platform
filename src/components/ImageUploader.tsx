import React, { useRef, useState } from 'react';

interface ImageUploaderProps {
    images: string[]; // 已上傳的圖片 URLs
    onImagesChange: (images: string[]) => void;
    maxImages?: number;
}

export const ImageUploader: React.FC<ImageUploaderProps> = ({
    images,
    onImagesChange,
    maxImages = 6,
}) => {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const files = event.target.files;
        if (!files || files.length === 0) return;

        // 檢查是否超過最大數量
        if (images.length + files.length > maxImages) {
            setError(`最多只能上傳 ${maxImages} 張圖片`);
            return;
        }

        setUploading(true);
        setError(null);

        try {
            // 動態導入 diaryService
            const { diaryService } = await import('../services/diaryService');

            // 上傳圖片
            const filesArray = Array.from(files);
            const uploadedUrls = await diaryService.uploadImages(filesArray);

            // 更新圖片列表（將後端返回的相對路徑轉換為完整 URL）
            const fullUrls = uploadedUrls.map(url => `http://localhost:5000${url}`);
            onImagesChange([...images, ...fullUrls]);
        } catch (err) {
            setError(err instanceof Error ? err.message : '上傳失敗');
        } finally {
            setUploading(false);
            // 清空 input
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        }
    };

    const handleRemoveImage = (index: number) => {
        const newImages = images.filter((_, i) => i !== index);
        onImagesChange(newImages);
    };

    const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        const files = e.dataTransfer.files;
        if (files.length > 0 && fileInputRef.current) {
            fileInputRef.current.files = files;
            handleFileSelect({ target: { files } } as any);
        }
    };

    const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
    };

    return (
        <div className="space-y-4">
            <h3 className="text-xl font-bold">上傳照片（選填）</h3>

            {/* 上傳區域 */}
            {images.length < maxImages && (
                <div
                    onDrop={handleDrop}
                    onDragOver={handleDragOver}
                    onClick={() => fileInputRef.current?.click()}
                    className="border-4 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-yellow-400 hover:bg-yellow-50 transition-colors"
                >
                    <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/png,image/jpeg,image/jpg,image/gif,image/webp"
                        multiple
                        onChange={handleFileSelect}
                        className="hidden"
                    />

                    {uploading ? (
                        <div className="text-gray-600">
                            <div className="text-3xl mb-2">⏳</div>
                            <div>上傳中...</div>
                        </div>
                    ) : (
                        <div className="text-gray-600">
                            <div className="text-3xl mb-2">📷</div>
                            <div className="font-medium">點擊或拖放圖片到這裡</div>
                            <div className="text-sm mt-1">支援 PNG, JPG, GIF, WEBP</div>
                            <div className="text-sm text-gray-500 mt-1">
                                還可以上傳 {maxImages - images.length} 張
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* 錯誤訊息 */}
            {error && (
                <div className="p-3 bg-red-100 border-4 border-red-400 rounded-lg text-red-700">
                    {error}
                </div>
            )}

            {/* 圖片預覽 */}
            {images.length > 0 && (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {images.map((url, index) => (
                        <div key={index} className="relative group">
                            <img
                                src={url}
                                alt={`上傳的圖片 ${index + 1}`}
                                className="w-full h-32 object-cover border-4 border-gray-300 rounded-lg"
                            />
                            <button
                                onClick={() => handleRemoveImage(index)}
                                className="absolute top-2 right-2 w-8 h-8 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600 font-bold"
                            >
                                ×
                            </button>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};
