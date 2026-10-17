Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "D:\Antigravity Projects\ShopLinx Marketing"
WshShell.Run "pythonw.exe scripts\auto_scheduler.py", 0, False
Set WshShell = Nothing
