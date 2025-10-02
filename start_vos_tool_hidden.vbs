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

' Wait for URL to be captured (check multiple times)
urlFile = "C:\temp\cloudflared_url.txt"
maxAttempts = 20  ' Try for up to 20 seconds
attempt = 0
urlFound = False

While attempt < maxAttempts And Not urlFound
    WScript.Sleep 1000  ' Wait 1 second
    attempt = attempt + 1
    
    If objFSO.FileExists(urlFile) Then
        ' Check if file has content
        Set file = objFSO.OpenTextFile(urlFile, 1)
        If Not file.AtEndOfStream Then
            url = file.ReadLine
            file.Close
            If Len(Trim(url)) > 0 Then
                urlFound = True
            End If
        Else
            file.Close
        End If
    End If
Wend

' Display result
If urlFound Then
    ' Copy URL to clipboard FIRST (before showing message)
    objShell.Run "powershell.exe -Command ""Set-Clipboard -Value '" & url & "'""", 0, True
    
    ' Show the URL in a message box
    MsgBox "VOS Tool is now running!" & vbCrLf & vbCrLf & _
           "Access URL: " & url & vbCrLf & vbCrLf & _
           "URL copied to clipboard - just paste it!" & vbCrLf & vbCrLf & _
           "Share this URL with your users.", _
           vbInformation, "VOS Tool Started"
Else
    MsgBox "VOS Tool started, but could not capture the Cloudflared URL." & vbCrLf & vbCrLf & _
           "Check the logs at C:\temp\cloudflared.log" & vbCrLf & vbCrLf & _
           "Tip: Try running get_cloudflared_url.ps1 after a few more seconds.", _
           vbExclamation, "VOS Tool Started"
End If
