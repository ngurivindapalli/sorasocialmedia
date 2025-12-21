# Simple backend startup script
# Run this in PowerShell to see all logs

Write-Host "Starting backend server..." -ForegroundColor Green
Write-Host "Logs will appear below:" -ForegroundColor Yellow
Write-Host ""

cd $PSScriptRoot
python main.py
