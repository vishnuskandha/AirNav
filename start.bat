@echo off
REM ========================================
REM AirNav - Batch Launcher
REM ========================================
REM This batch file launches the PowerShell
REM script which displays beautiful colored
REM ASCII art and handles all setup tasks
REM ========================================

REM Check if PowerShell is available
where powershell >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PowerShell is not available!
    echo.
    echo Please use Windows PowerShell or Windows PowerShell Core.
    echo Alternatively, run: python modern_app.py
    pause
    exit /b 1
)

REM Launch the PowerShell script
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1"

REM Check exit code
if errorlevel 1 (
    echo.
    echo [ERROR] PowerShell script encountered an error.
    pause
    exit /b 1
)

pause
exit /b 0
