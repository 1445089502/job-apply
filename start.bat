@echo off
rem Start job-apply backend (with frontend dashboard) on port 8000
cd /d "%~dp0backend"
set PYTHONUTF8=1
echo Starting... open http://127.0.0.1:8000
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
pause
