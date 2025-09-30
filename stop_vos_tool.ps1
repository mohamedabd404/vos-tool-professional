# PowerShell script to stop VOS Tool and Cloudflared

Write-Host ""
Write-Host "Stopping VOS Tool and Cloudflared..." -ForegroundColor Yellow
Write-Host ""

# Stop Streamlit processes
$streamlitProcesses = Get-Process -Name "streamlit" -ErrorAction SilentlyContinue
if ($streamlitProcesses) {
    $streamlitProcesses | Stop-Process -Force
    Write-Host "✓ Stopped Streamlit" -ForegroundColor Green
} else {
    Write-Host "- Streamlit not running" -ForegroundColor Gray
}

# Stop Cloudflared processes
$cloudflaredProcesses = Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue
if ($cloudflaredProcesses) {
    $cloudflaredProcesses | Stop-Process -Force
    Write-Host "✓ Stopped Cloudflared" -ForegroundColor Green
} else {
    Write-Host "- Cloudflared not running" -ForegroundColor Gray
}

# Stop Python processes running Streamlit
$pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*streamlit*"
}
if ($pythonProcesses) {
    $pythonProcesses | Stop-Process -Force
    Write-Host "✓ Stopped Python/Streamlit processes" -ForegroundColor Green
}

Write-Host ""
Write-Host "All processes stopped!" -ForegroundColor Green
Write-Host ""

# Keep window open
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
