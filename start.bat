@echo off
REM VideoHook - Start Both Servers (Windows Batch)
REM Double-click this file or run: start.bat

echo ========================================
echo   VideoHook - Starting Servers
echo ========================================
echo.

REM Start Backend
echo Starting Backend Server...
start "VideoHook Backend" powershell -NoExit -Command "cd backend; if (Test-Path 'venv\Scripts\Activate.ps1') { .\venv\Scripts\Activate.ps1 }; Write-Host '=== BACKEND SERVER ===' -ForegroundColor Cyan; Write-Host 'http://localhost:8000' -ForegroundColor Green; python main.py"

timeout /t 2 /nobreak >nul

REM Start Frontend
echo Starting Frontend Server...
start "VideoHook Frontend" powershell -NoExit -Command "cd frontend; Write-Host '=== FRONTEND SERVER ===' -ForegroundColor Cyan; Write-Host 'http://localhost:3001' -ForegroundColor Green; npm run dev"

echo.
echo ✅ Both servers are starting!
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3001
echo.
echo Two windows have opened - check them for startup logs.
echo.
pause

