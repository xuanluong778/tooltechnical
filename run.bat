@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Creating virtual environment...
    python -m venv .venv
)

echo [INFO] Installing/updating dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo [INFO] Stopping any old server on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul

echo [INFO] Starting FastAPI app at http://127.0.0.1:8000
echo [INFO] Open http://127.0.0.1:8000/content-ai
REM Ensure benchmark-fast mode is off for web app
set BENCH_FAST=0
REM Avoid reload loops when runtime writes app.db
if "%DEV_RELOAD%"=="1" (
    echo [INFO] DEV_RELOAD=1 -> running with --reload
    ".venv\Scripts\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
) else (
    ".venv\Scripts\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8000
)

endlocal
