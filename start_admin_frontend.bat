@echo off
chcp 65001 > nul
echo ========================================
echo 啟動管理後台 (醫護人員界面)
echo ========================================
echo.
echo 端口: 5174
echo URL: http://localhost:5174
echo.
echo 按 Ctrl+C 可停止服務器
echo ========================================
echo.

cd /d "%~dp0admin-frontend"

npm run dev

pause
