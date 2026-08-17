@echo off
rem 停止 job-apply 服务（端口 8000）
setlocal enabledelayedexpansion
set "found=0"
echo 正在停止 job-apply (端口 8000)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo 终止 PID: %%a
    taskkill /F /PID %%a >nul 2>&1
    set "found=1"
)
if !found!==0 echo 未发现端口 8000 上的 job-apply 服务（可能已停止）。
echo 完成。
pause
