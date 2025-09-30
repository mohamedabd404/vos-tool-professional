# VOS Tool - Hidden Mode Operation Guide

## Overview

This guide explains how to run VOS Tool completely hidden in the background with automatic URL capture.

## Files Included

1. **`start_vos_tool_hidden.vbs`** - Main launcher (double-click to start)
2. **`start_cloudflared.ps1`** - PowerShell script that captures the URL
3. **`get_cloudflared_url.ps1`** - Retrieve the current URL anytime
4. **`stop_vos_tool.ps1`** - Stop all VOS Tool processes

---

## Quick Start

### Starting VOS Tool (Hidden Mode)

1. **Double-click**: `start_vos_tool_hidden.vbs`
2. **Wait 10 seconds** for everything to start
3. **A popup will show** with your public URL
4. **URL is automatically copied** to your clipboard
5. **Share the URL** with your users!

**No windows will appear** - everything runs hidden in the background.

---

## Getting the URL Later

If you need to retrieve the URL after starting:

### Method 1: Run the PowerShell Script
1. **Right-click** `get_cloudflared_url.ps1`
2. **Select** "Run with PowerShell"
3. **URL will be displayed** and copied to clipboard

### Method 2: Check the File
The URL is always saved to: `C:\temp\cloudflared_url.txt`

You can open this file anytime to see the current URL.

---

## Stopping VOS Tool

### Method 1: Run Stop Script
1. **Right-click** `stop_vos_tool.ps1`
2. **Select** "Run with PowerShell"
3. All processes will be stopped

### Method 2: Task Manager
1. Open Task Manager (`Ctrl+Shift+Esc`)
2. Find and end these processes:
   - `streamlit.exe`
   - `cloudflared.exe`
   - `python.exe` (if running Streamlit)

---

## How It Works

### The Process Flow:

```
1. start_vos_tool_hidden.vbs (VBS Launcher)
   ↓
2. Starts Streamlit (hidden)
   - Runs: streamlit run app.py
   - Port: 8501
   - Window: Hidden
   ↓
3. Starts start_cloudflared.ps1 (hidden)
   - Runs: cloudflared tunnel --url http://localhost:8501
   - Captures output to logs
   - Extracts URL using regex
   - Saves URL to: C:\temp\cloudflared_url.txt
   ↓
4. Shows popup with URL
   - Displays the public URL
   - Copies URL to clipboard
   - You can now share it!
```

### URL Capture Method:

The script monitors both stdout and stderr from cloudflared for up to 10 seconds, looking for the pattern:
```
https://[random-words].trycloudflare.com
```

Once found, it's saved to `C:\temp\cloudflared_url.txt`

---

## Log Files

All logs are saved to `C:\temp\`:

- **`cloudflared_url.txt`** - The current public URL
- **`cloudflared.log`** - Standard output from cloudflared
- **`cloudflared_error.log`** - Error output from cloudflared

### Checking Logs:

```powershell
# View the URL
Get-Content C:\temp\cloudflared_url.txt

# View cloudflared logs
Get-Content C:\temp\cloudflared.log

# View errors
Get-Content C:\temp\cloudflared_error.log
```

---

## Troubleshooting

### Issue: No URL popup appears

**Solution**:
1. Wait 15 seconds (sometimes takes longer)
2. Check `C:\temp\cloudflared_url.txt` manually
3. Run `get_cloudflared_url.ps1` to retrieve it

### Issue: "Execution Policy" error

**Solution**:
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: URL file not created

**Solution**:
1. Check if `C:\temp\` folder exists
2. Check `C:\temp\cloudflared_error.log` for errors
3. Make sure cloudflared.exe is in `C:\cloudflared\`

### Issue: Streamlit not starting

**Solution**:
1. Open PowerShell manually and run:
   ```powershell
   cd "C:\Users\almisria\Desktop\Final tools\VOS TOOL - final"
   streamlit run app.py
   ```
2. Check for error messages
3. Make sure all dependencies are installed

---

## Daily Usage

### Morning Routine:
1. **Double-click** `start_vos_tool_hidden.vbs`
2. **Copy the URL** from the popup
3. **Share with your team** via email/chat
4. **Leave it running** all day

### Evening Routine:
1. **Run** `stop_vos_tool.ps1`
2. Everything stops cleanly

---

## Advanced: Auto-Start with Windows

To make VOS Tool start automatically when Windows boots:

1. **Press** `Win + R`
2. **Type**: `shell:startup`
3. **Press** Enter
4. **Copy** `start_vos_tool_hidden.vbs` to this folder
5. **Restart** your PC to test

Now VOS Tool will start hidden every time Windows starts!

---

## Security Notes

- The URL changes each time you restart cloudflared
- Only people with the URL can access your VOS Tool
- The URL is random and hard to guess
- Your PC must stay on for users to access the tool

---

## Benefits of Hidden Mode

✅ **Clean Desktop** - No visible windows cluttering your screen
✅ **Professional** - Runs like a service in the background
✅ **Easy URL Sharing** - Automatic capture and clipboard copy
✅ **Reliable** - Consistent startup process
✅ **Convenient** - One double-click to start everything

---

## File Locations Reference

```
VOS Tool Project/
├── start_vos_tool_hidden.vbs    ← Double-click this to start
├── start_cloudflared.ps1         ← URL capture script
├── get_cloudflared_url.ps1       ← Retrieve URL anytime
├── stop_vos_tool.ps1             ← Stop everything
└── app.py                        ← Main Streamlit app

C:\temp/
├── cloudflared_url.txt           ← Current public URL
├── cloudflared.log               ← Cloudflared output
└── cloudflared_error.log         ← Error messages

C:\cloudflared/
└── cloudflared.exe               ← Cloudflared executable
```

---

## Support

If you encounter issues:
1. Check the log files in `C:\temp\`
2. Try running manually to see error messages
3. Make sure all paths are correct
4. Verify cloudflared.exe is in `C:\cloudflared\`

---

**Enjoy your fully automated, hidden VOS Tool setup!** 🚀
