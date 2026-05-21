@echo off
setlocal

if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] Missing .venv. Please create venv and install deps.
  exit /b 1
)

set PYTHONUNBUFFERED=1
set PYTHONIOENCODING=utf-8
REM Ensure production worker doesn't run in benchmark-fast mode
set BENCH_FAST=0
echo [INFO] Starting keyword clustering worker...
".venv\Scripts\python.exe" scripts\keyword_cluster_worker.py

