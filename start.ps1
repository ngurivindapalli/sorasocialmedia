# VideoHook - Start Both Servers
# This script starts both the backend and frontend servers

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VideoHook - Starting Servers" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$rootPath = $PSScriptRoot
$backendPath = Join-Path $rootPath "backend"
$frontendPath = Join-Path $rootPath "frontend"

# Check if directories exist
if (-not (Test-Path $backendPath)) {
    Write-Host "ERROR: Backend directory not found: $backendPath" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $frontendPath)) {
    Write-Host "ERROR: Frontend directory not found: $frontendPath" -ForegroundColor Red
    exit 1
}

Write-Host "Starting Backend Server..." -ForegroundColor Yellow
Write-Host "   Location: $backendPath" -ForegroundColor Gray
Write-Host "   URL: http://localhost:8000" -ForegroundColor Gray
Write-Host ""

# Start Backend in a new window (auto-restart DISABLED)
$backendCommand = "cd '$backendPath'; if (Test-Path 'venv\Scripts\Activate.ps1') { .\venv\Scripts\Activate.ps1; Write-Host '[Backend] Virtual environment activated' -ForegroundColor Green } else { Write-Host '[Backend] No venv found, using system Python' -ForegroundColor Yellow }; Write-Host ''; Write-Host '========================================' -ForegroundColor Cyan; Write-Host '  BACKEND SERVER (FastAPI)' -ForegroundColor Cyan; Write-Host '  Auto-restart: DISABLED' -ForegroundColor Yellow; Write-Host '========================================' -ForegroundColor Cyan; Write-Host 'Starting on http://localhost:8000' -ForegroundColor Green; Write-Host 'API Docs: http://localhost:8000/docs' -ForegroundColor Yellow; Write-Host ''; python main.py"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCommand -WindowStyle Normal

# Wait a moment for backend to start
Start-Sleep -Seconds 2

Write-Host "Starting Frontend Server..." -ForegroundColor Yellow
Write-Host "   Location: $frontendPath" -ForegroundColor Gray
Write-Host "   URL: http://localhost:3001" -ForegroundColor Gray
Write-Host ""

# Start Frontend in a new window
$frontendCommand = "cd '$frontendPath'; Write-Host ''; Write-Host '========================================' -ForegroundColor Cyan; Write-Host '  FRONTEND SERVER (Vite/React)' -ForegroundColor Cyan; Write-Host '========================================' -ForegroundColor Cyan; Write-Host 'Starting on http://localhost:3001' -ForegroundColor Green; Write-Host ''; npm run dev"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCommand -WindowStyle Normal

Write-Host ""
Write-Host "SUCCESS: Both servers are starting!" -ForegroundColor Green
Write-Host ""
Write-Host "Server Information:" -ForegroundColor Cyan
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "   Frontend: http://localhost:3001" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Two PowerShell windows have opened:" -ForegroundColor Yellow
Write-Host "   1. Backend server (FastAPI)" -ForegroundColor Gray
Write-Host "   2. Frontend server (Vite/React)" -ForegroundColor Gray
Write-Host ""
Write-Host "Wait a few seconds for servers to fully start," -ForegroundColor Yellow
Write-Host "then open http://localhost:3001 in your browser" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to exit this window (servers will keep running)..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
