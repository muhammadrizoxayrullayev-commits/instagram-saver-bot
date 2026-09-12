Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\muham\OneDrive\Desktop\link saved bot"
WshShell.Run """C:\Users\muham\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe"" main.py", 0, False
