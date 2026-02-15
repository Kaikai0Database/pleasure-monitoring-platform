import html2canvas from 'html2canvas';

/**
 * Convert array of objects to CSV format
 */
export function convertToCSV(data: any[]): string {
    if (!data || data.length === 0) return '';
    
    // Get headers from first object
    const headers = Object.keys(data[0]);
    
    // Create CSV header row
    const csvHeaders = headers.join(',');
    
    // Create CSV data rows
    const csvRows = data.map(row => {
        return headers.map(header => {
            const value = row[header];
            // Handle null, undefined, and values with commas
            if (value === null || value === undefined) return '';
            const stringValue = String(value);
            // Escape values containing commas or quotes
            if (stringValue.includes(',') || stringValue.includes('"')) {
                return `"${stringValue.replace(/"/g, '""')}"`;
            }
            return stringValue;
        }).join(',');
    });
    
    return [csvHeaders, ...csvRows].join('\n');
}

/**
 * Download data as CSV file
 */
export function downloadCSV(data: any[], filename: string): void {
    const csvContent = convertToCSV(data);
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' }); // Add BOM for Excel compatibility
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${filename}_${new Date().toLocaleDateString('zh-TW').replace(/\//g, '-')}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

/**
 * Download chart as PNG image
 */
export async function downloadChartAsPNG(element: HTMLElement, filename: string): Promise<void> {
    try {
        const canvas = await html2canvas(element, {
            backgroundColor: '#ffffff',
            scale: 2, // Higher quality
            logging: false,
        });
        
        canvas.toBlob((blob) => {
            if (blob) {
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = `${filename}_${new Date().toLocaleDateString('zh-TW').replace(/\//g, '-')}.png`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                URL.revokeObjectURL(url);
            }
        });
    } catch (error) {
        console.error('Download chart as PNG failed:', error);
        alert('下載圖片失敗，請稍後再試');
    }
}
