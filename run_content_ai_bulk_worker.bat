@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] Missing .venv
  exit /b 1
)
set PYTHONUNBUFFERED=1
echo [INFO] Content AI bulk worker (optional — server auto-starts worker by default)
".venv\Scripts\python.exe" scripts\content_ai_bulk_worker.py
endlocal
