' VBS Script to start VOS Tool and Cloudflared completely hidden
' This script starts both Streamlit and Cloudflared in the background
' The Cloudflared URL will be saved to C:\temp\cloudflared_url.txt

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
scriptDir = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Start Streamlit (hidden)
objShell.Run "powershell.exe -WindowStyle Hidden -Command ""cd '" & scriptDir & "'; streamlit run app.py""", 0, False

' Wait 5 seconds for Streamlit to start
WScript.Sleep 5000

' Start Cloudflared using the PowerShell script (hidden)
objShell.Run "powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File """ & scriptDir & "\start_cloudflared.ps1""", 0, False

' Wait for URL to be captured
WScript.Sleep 5000

' Read and display the URL
urlFile = "C:\temp\cloudflared_url.txt"
If objFSO.FileExists(urlFile) Then
    Set file = objFSO.OpenTextFile(urlFile, 1)
    url = file.ReadLine
    file.Close
    
    ' Show the URL in a message box
    MsgBox "VOS Tool is now running!" & vbCrLf & vbCrLf & _
           "Access URL: " & url & vbCrLf & vbCrLf & _
           "This URL has been copied to your clipboard." & vbCrLf & vbCrLf & _
           "Share this URL with your users.", _
           vbInformation, "VOS Tool Started"
    
    ' Copy URL to clipboard
    objShell.Run "cmd /c echo " & url & " | clip", 0, True
Else
    MsgBox "VOS Tool started, but could not capture the Cloudflared URL." & vbCrLf & vbCrLf & _
           "Check the logs at C:\temp\cloudflared.log", _
           vbExclamation, "VOS Tool Started"
End If
