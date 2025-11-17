# Start Backend Server with Environment Variables
# Load API key from .env file
if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "OPENAI_API_KEY=(.+)") {
        $env:OPENAI_API_KEY = $matches[1].Trim()
        Write-Host "Loaded OPENAI_API_KEY from .env file" -ForegroundColor Green
    } else {
        Write-Host "ERROR: OPENAI_API_KEY not found in .env file" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "ERROR: .env file not found" -ForegroundColor Red
    exit 1
}

Write-Host "Starting Backend Server..." -ForegroundColor Green
Write-Host ""

# Activate virtual environment
if (Test-Path "venv\Scripts\Activate.ps1") {
    . venv\Scripts\Activate.ps1
    Write-Host "Virtual environment activated" -ForegroundColor Cyan
}

# Start uvicorn
Write-Host "Starting uvicorn on http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host ""
uvicorn main:app --host 127.0.0.1 --port 8000 --reload

