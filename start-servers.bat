@echo off
REM VideoHook - Start Both Servers (Batch version)
REM Double-click this file or run: start-servers.bat

echo.
echo ========================================
echo   VideoHook - Starting Servers
echo ========================================
echo.

cd /d "%~dp0"

REM Start Backend Server
echo Starting Backend Server (FastAPI)...
start "VideoHook Backend" powershell -NoExit -Command "cd '%CD%\backend'; if (Test-Path 'venv\Scripts\Activate.ps1') { .\venv\Scripts\Activate.ps1 }; Write-Host '=== BACKEND SERVER ===' -ForegroundColor Cyan; Write-Host 'URL: http://localhost:8000' -ForegroundColor Green; python main.py"

timeout /t 2 /nobreak >nul

REM Start Frontend Server
echo Starting Frontend Server (Vite/React)...
start "VideoHook Frontend" powershell -NoExit -Command "cd '%CD%\frontend'; Write-Host '=== FRONTEND SERVER ===' -ForegroundColor Cyan; Write-Host 'URL: http://localhost:3001' -ForegroundColor Green; npm run dev"

timeout /t 2 /nobreak >nul

echo.
echo Both servers are starting!
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3001
echo API Docs: http://localhost:8000/docs
echo.
echo Two windows have opened - check them for startup messages
echo.
pause


