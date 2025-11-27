# Exchange Instagram Short-Lived Token for Long-Lived Token
# Run this script to get a long-lived token (expires in ~60 days)

param(
    [Parameter(Mandatory=$true)]
    [string]$AppId,
    
    [Parameter(Mandatory=$true)]
    [string]$AppSecret,
    
    [Parameter(Mandatory=$true)]
    [string]$ShortLivedToken
)

Write-Host "🔄 Exchanging Instagram Token..." -ForegroundColor Cyan
Write-Host ""

$url = "https://graph.facebook.com/v21.0/oauth/access_token"
$params = @{
    grant_type = "fb_exchange_token"
    client_id = $AppId
    client_secret = $AppSecret
    fb_exchange_token = $ShortLivedToken
}

try {
    Write-Host "Sending request to Facebook Graph API..." -ForegroundColor Yellow
    $response = Invoke-RestMethod -Uri $url -Method Get -Body $params
    
    if ($response.access_token) {
        Write-Host ""
        Write-Host "✅ SUCCESS! Long-lived token obtained:" -ForegroundColor Green
        Write-Host ""
        Write-Host "Access Token:" -ForegroundColor Cyan
        Write-Host $response.access_token -ForegroundColor White
        Write-Host ""
        Write-Host "Expires In: $($response.expires_in) seconds (~$([math]::Round($response.expires_in / 86400)) days)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "📝 Next steps:" -ForegroundColor Cyan
        Write-Host "1. Copy the access token above" -ForegroundColor White
        Write-Host "2. Update backend/.env with:" -ForegroundColor White
        Write-Host "   INSTAGRAM_ACCESS_TOKEN=$($response.access_token)" -ForegroundColor Gray
        Write-Host ""
        
        # Ask if user wants to update .env automatically
        $update = Read-Host "Would you like to update backend/.env automatically? (y/n)"
        if ($update -eq 'y' -or $update -eq 'Y') {
            $envPath = "backend\.env"
            if (Test-Path $envPath) {
                $content = Get-Content $envPath -Raw
                if ($content -match "INSTAGRAM_ACCESS_TOKEN=") {
                    $content = $content -replace "INSTAGRAM_ACCESS_TOKEN=.*", "INSTAGRAM_ACCESS_TOKEN=$($response.access_token)"
                    Set-Content $envPath -Value $content -NoNewline
                    Write-Host "✅ Updated INSTAGRAM_ACCESS_TOKEN in .env" -ForegroundColor Green
                } else {
                    Add-Content $envPath -Value "`nINSTAGRAM_ACCESS_TOKEN=$($response.access_token)"
                    Write-Host "✅ Added INSTAGRAM_ACCESS_TOKEN to .env" -ForegroundColor Green
                }
            } else {
                "INSTAGRAM_ACCESS_TOKEN=$($response.access_token)" | Out-File $envPath -Encoding utf8
                Write-Host "✅ Created .env file with INSTAGRAM_ACCESS_TOKEN" -ForegroundColor Green
            }
        }
    } else {
        Write-Host "❌ Error: No access token in response" -ForegroundColor Red
        Write-Host "Response: $($response | ConvertTo-Json)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Error exchanging token:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Yellow
    if ($_.ErrorDetails.Message) {
        Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

