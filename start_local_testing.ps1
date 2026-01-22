# PowerShell script to start backend and frontend for local LinkedIn testing

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Local LinkedIn Testing Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if backend .env has LinkedIn credentials
Write-Host "Checking backend configuration..." -ForegroundColor Yellow
$backendEnv = "backend\.env"
if (Test-Path $backendEnv) {
    $envContent = Get-Content $backendEnv -Raw
    if ($envContent -match "LINKEDIN_CLIENT_ID" -and $envContent -match "LINKEDIN_CLIENT_SECRET") {
        Write-Host "  OK: LinkedIn credentials found" -ForegroundColor Green
    } else {
        Write-Host "  WARNING: LinkedIn credentials not found in .env" -ForegroundColor Red
        Write-Host "  Add LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET to backend/.env" -ForegroundColor Yellow
    }
    
    if ($envContent -match "BASE_URL=http://localhost:8000") {
        Write-Host "  OK: BASE_URL set for local testing" -ForegroundColor Green
    } else {
        Write-Host "  WARNING: BASE_URL should be http://localhost:8000 for local testing" -ForegroundColor Yellow
    }
    
    if ($envContent -match "FRONTEND_URL=http://localhost:3000") {
        Write-Host "  OK: FRONTEND_URL set for local testing" -ForegroundColor Green
    } else {
        Write-Host "  WARNING: FRONTEND_URL should be http://localhost:3000 for local testing" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ERROR: backend/.env file not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "Starting services..." -ForegroundColor Yellow
Write-Host ""

# Start backend in new window
Write-Host "Starting backend server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; Write-Host 'Starting backend server for LinkedIn testing...' -ForegroundColor Green; python main.py"

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start frontend in new window
Write-Host "Starting frontend server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; Write-Host 'Starting frontend server...' -ForegroundColor Green; npm run dev"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Services Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Open http://localhost:3000 in your browser" -ForegroundColor White
Write-Host "2. Go to Settings tab" -ForegroundColor White
Write-Host "3. Click 'Connect LinkedIn' button" -ForegroundColor White
Write-Host "4. Complete OAuth flow" -ForegroundColor White
Write-Host ""
Write-Host "IMPORTANT: Make sure you added this redirect URL to LinkedIn:" -ForegroundColor Yellow
Write-Host "  http://localhost:8000/api/oauth/linkedin/callback" -ForegroundColor White
Write-Host ""
