' Save as RunStreamlit.vbs
Set objShell = CreateObject("Wscript.Shell")
objShell.CurrentDirectory = "C:\Users\almisria\Desktop\Final tools\VOS TOOL - final"
objShell.Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ""streamlit run app.py""", 0, False
