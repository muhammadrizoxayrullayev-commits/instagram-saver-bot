Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\muham\OneDrive\Desktop\link saved bot"
WshShell.Run "cmd.exe /c python main.py", 0, False
