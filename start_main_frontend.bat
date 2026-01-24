@echo off
chcp 65001 > nul
echo ========================================
echo 啟動主前端 (用戶界面)
echo ========================================
echo.
echo 端口: 5173
echo URL: http://localhost:5173
echo.
echo 按 Ctrl+C 可停止服務器
echo ========================================
echo.

cd /d "%~dp0"

npm run dev

pause
