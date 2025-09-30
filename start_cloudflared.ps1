# PowerShell script to start cloudflared and capture the URL
# This script runs cloudflared and saves the public URL to a file

$logFile = "C:\temp\cloudflared.log"
$urlFile = "C:\temp\cloudflared_url.txt"
$errorFile = "C:\temp\cloudflared_error.log"

# Ensure temp directory exists
if (!(Test-Path "C:\temp")) {
    New-Item -ItemType Directory -Path "C:\temp" -Force | Out-Null
}

# Clear previous URL file
if (Test-Path $urlFile) {
    Remove-Item $urlFile -Force
}

# Start cloudflared and capture both stdout and stderr
$process = Start-Process -FilePath "C:\cloudflared\cloudflared.exe" `
    -ArgumentList "tunnel --url http://localhost:8501" `
    -RedirectStandardOutput $logFile `
    -RedirectStandardError $errorFile `
    -WindowStyle Hidden `
    -PassThru `
    -NoNewWindow

# Wait a moment for cloudflared to start
Start-Sleep -Seconds 3

# Parse the log files to find the URL
$maxAttempts = 10
$attempt = 0
$urlFound = $false

while ($attempt -lt $maxAttempts -and !$urlFound) {
    Start-Sleep -Seconds 1
    
    # Check both stdout and stderr logs
    $logContent = ""
    if (Test-Path $logFile) {
        $logContent += Get-Content $logFile -Raw
    }
    if (Test-Path $errorFile) {
        $logContent += Get-Content $errorFile -Raw
    }
    
    # Look for the trycloudflare.com URL pattern
    if ($logContent -match "(https://[a-zA-Z0-9-]+\.trycloudflare\.com)") {
        $url = $matches[1]
        $url | Out-File -FilePath $urlFile -Encoding UTF8
        Write-Host "Cloudflared URL captured: $url"
        $urlFound = $true
    }
    
    $attempt++
}

if (!$urlFound) {
    Write-Host "Warning: Could not capture cloudflared URL after $maxAttempts attempts"
    Write-Host "Check logs at: $logFile and $errorFile"
}

# Keep the process running
Wait-Process -Id $process.Id
