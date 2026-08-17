@echo off
rem 启动 job-apply 后端（含前端看板），端口 8000
cd /d "%~dp0backend"
set PYTHONUTF8=1
echo 启动中... 浏览器打开 http://127.0.0.1:8000
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
pause
