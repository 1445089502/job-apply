@echo off
rem Stop job-apply service on port 8000
setlocal enabledelayedexpansion
set "found=0"
echo Stopping job-apply (port 8000)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo Kill PID: %%a
    taskkill /F /PID %%a >nul 2>&1
    set "found=1"
)
if !found!==0 echo No job-apply service found on port 8000.
echo Done.
pause
