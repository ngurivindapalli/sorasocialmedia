# VideoHook - Start Both Servers
# This script starts both the backend (FastAPI) and frontend (Vite) servers

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VideoHook - Starting Servers" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$rootPath = $PSScriptRoot
if (-not $rootPath) {
    $rootPath = Get-Location
}

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

Write-Host "Root: $rootPath" -ForegroundColor Gray
Write-Host ""

# Start Backend Server
Write-Host "Starting Backend Server (FastAPI)..." -ForegroundColor Green
$backendCommand = "cd '$backendPath'; if (Test-Path 'venv\Scripts\Activate.ps1') { .\venv\Scripts\Activate.ps1; Write-Host '[Backend] Virtual environment activated' -ForegroundColor Green } else { Write-Host '[Backend] No venv found, using system Python' -ForegroundColor Yellow }; Write-Host ''; Write-Host '========================================' -ForegroundColor Cyan; Write-Host '  BACKEND SERVER (FastAPI)' -ForegroundColor Cyan; Write-Host '========================================' -ForegroundColor Cyan; Write-Host 'URL: http://localhost:8000' -ForegroundColor Green; Write-Host 'API Docs: http://localhost:8000/docs' -ForegroundColor Yellow; Write-Host ''; Write-Host 'Starting server...' -ForegroundColor Cyan; Write-Host ''; python main.py"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCommand -WindowStyle Normal

# Wait a moment before starting frontend
Start-Sleep -Seconds 2

# Start Frontend Server
Write-Host "Starting Frontend Server (Vite/React)..." -ForegroundColor Green
$frontendCommand = "cd '$frontendPath'; Write-Host ''; Write-Host '========================================' -ForegroundColor Cyan; Write-Host '  FRONTEND SERVER (Vite/React)' -ForegroundColor Cyan; Write-Host '========================================' -ForegroundColor Cyan; Write-Host 'URL: http://localhost:3001' -ForegroundColor Green; Write-Host ''; Write-Host 'Starting server...' -ForegroundColor Cyan; Write-Host ''; npm run dev"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCommand -WindowStyle Normal

# Wait a moment
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "SUCCESS: Both servers are starting!" -ForegroundColor Green
Write-Host ""
Write-Host "Server URLs:" -ForegroundColor Cyan
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "   Frontend: http://localhost:3001" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Two PowerShell windows have opened:" -ForegroundColor Yellow
Write-Host "   1. Backend (FastAPI) - Port 8000" -ForegroundColor Gray
Write-Host "   2. Frontend (Vite) - Port 3001" -ForegroundColor Gray
Write-Host ""
Write-Host "Wait a few seconds for servers to fully start..." -ForegroundColor Yellow
Write-Host "Then open http://localhost:3001 in your browser" -ForegroundColor Yellow
Write-Host ""
Write-Host "To stop servers, close the PowerShell windows" -ForegroundColor Gray
Write-Host ""
