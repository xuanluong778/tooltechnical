@echo off
setlocal
cd /d "%~dp0\.."

if not exist "app.db" (
    echo [ERROR] app.db not found in %CD%
    exit /b 1
)

copy /Y "app.db" "app_backup_before_prompt2.db" >nul
if errorlevel 1 (
    echo [ERROR] Backup failed.
    exit /b 1
)

echo [OK] Backup saved: %CD%\app_backup_before_prompt2.db
for %%F in (app.db app_backup_before_prompt2.db) do (
    echo     %%F - %%~zF bytes
)
endlocal
