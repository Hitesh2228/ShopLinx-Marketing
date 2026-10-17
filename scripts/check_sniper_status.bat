@echo off
echo ============================================================
echo   SHOPLINX AI SNIPER STATUS CHECK
echo ============================================================
powershell -Command "$p = Get-CimInstance Win32_Process | Where-Object { ($_.Name -eq 'pythonw.exe' -or $_.Name -eq 'python.exe') -and $_.CommandLine -like '*auto_scheduler.py*' }; if ($p) { Write-Host ('Status: RUNNING (PID: ' + ($p.ProcessId -join ', ') + ')') -ForegroundColor Green } else { Write-Host 'Status: STOPPED' -ForegroundColor Red }"
echo.
echo Recent Log Entries:
echo ------------------------------------------------------------
powershell -Command "if (Test-Path 'data\logs\scheduler.log') { Get-Content 'data\logs\scheduler.log' -Tail 10 } else { Write-Host 'No log file found yet.' }"
echo ============================================================
