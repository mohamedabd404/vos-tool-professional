# PowerShell script to retrieve the current Cloudflared URL
# Run this anytime to get the current public URL

$urlFile = "C:\temp\cloudflared_url.txt"

if (Test-Path $urlFile) {
    $url = Get-Content $urlFile -Raw
    $url = $url.Trim()
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  VOS Tool Public URL" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  $url" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "URL copied to clipboard!" -ForegroundColor Green
    
    # Copy to clipboard
    $url | Set-Clipboard
    
} else {
    Write-Host ""
    Write-Host "Error: Cloudflared URL file not found!" -ForegroundColor Red
    Write-Host "Make sure Cloudflared is running." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Expected file: $urlFile" -ForegroundColor Gray
    Write-Host ""
}

# Keep window open
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
