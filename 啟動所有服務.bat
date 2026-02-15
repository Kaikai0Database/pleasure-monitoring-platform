@echo off
chcp 65001 > nul
echo ========================================
echo    啟動所有服務（失樂症監測平台）
echo ========================================
echo.
echo 此腳本將啟動：
echo   1. 後端服務器 (端口 5000)
echo   2. 主前端 (端口 5173)  
echo   3. 管理後台 (端口 5174)
echo.
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 啟動後端服務器...
start "後端服務器 (Port 5000)" cmd /k "cd backend && python run.py"
timeout /t 3 /nobreak > nul

echo [2/3] 啟動主前端...
start "主前端 (Port 5173)" cmd /k "npm run dev"
timeout /t 3 /nobreak > nul

echo [3/3] 啟動管理後台...
start "管理後台 (Port 5174)" cmd /k "cd admin-frontend && npm run dev"
timeout /t 2 /nobreak > nul

echo.
echo ========================================
echo ✅ 所有服務已啟動！
echo ========================================
echo.
echo 訪問網址：
echo   - 主前端：http://localhost:5173
echo   - 管理後台：http://localhost:5174
echo.
echo 請等待 5-10 秒讓服務完全啟動
echo ========================================
echo.

pause
