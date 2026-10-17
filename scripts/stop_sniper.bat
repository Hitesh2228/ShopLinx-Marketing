@echo off
echo Stopping ShopLinx AI Sniper process...
powershell -Command "Get-CimInstance Win32_Process | Where-Object { ($_.Name -eq 'pythonw.exe' -or $_.Name -eq 'python.exe') -and $_.CommandLine -like '*auto_scheduler.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; Write-Host ('Stopped Process ID: ' + $_.ProcessId) }"
echo ShopLinx AI Sniper has been stopped.
