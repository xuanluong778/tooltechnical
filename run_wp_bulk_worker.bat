@echo off
setlocal

if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] Missing .venv. Please create venv and install deps.
  exit /b 1
)

set PYTHONUNBUFFERED=1
set PYTHONIOENCODING=utf-8
echo [INFO] Starting WordPress bulk update worker...
".venv\Scripts\python.exe" scripts\wp_bulk_worker.py

