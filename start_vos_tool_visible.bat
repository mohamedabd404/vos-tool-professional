@echo off
REM Simple batch script to start VOS Tool with visible windows
REM This is easier to debug than the hidden VBS version

echo ========================================
echo Starting VOS Tool (Visible Mode)
echo ========================================
echo.

REM Start Streamlit in a new window
echo [1/3] Starting Streamlit...
start "VOS Tool - Streamlit" cmd /k "cd /d "%~dp0" && streamlit run app.py"

REM Wait for Streamlit to start
echo [2/3] Waiting for Streamlit to start (5 seconds)...
timeout /t 5 /nobreak >nul

REM Start Cloudflared in a new window
echo [3/3] Starting Cloudflared tunnel...
start "VOS Tool - Cloudflared" cmd /k "cd /d C:\cloudflared && cloudflared tunnel --url http://localhost:8501"

echo.
echo ========================================
echo VOS Tool Started!
echo ========================================
echo.
echo Two windows have opened:
echo 1. Streamlit (running your app)
echo 2. Cloudflared (creating the tunnel)
echo.
echo Wait 10 seconds, then check the Cloudflared window
echo for your public URL (https://...trycloudflare.com)
echo.
echo To stop: Close both windows
echo.
pause
