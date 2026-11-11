@echo off
REM Defect Dashboard Setup and Run Script
REM This script helps set up and run the defect dashboard with ediprod integration

setlocal enabledelayedexpansion

echo.
echo ========================================
echo  Defect Dashboard Setup
echo ========================================
echo.

REM Check if running in correct directory
if not exist "defect_dashboard.html" (
    echo ERROR: defect_dashboard.html not found!
    echo Please run this script from the dashboard directory.
    pause
    exit /b 1
)

echo [1] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://www.python.org/
    pause
    exit /b 1
)
echo ✓ Python found

echo.
echo [2] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Node.js not found. Backend API will not be available.
    echo To enable backend API, install Node.js from https://nodejs.org/
) else (
    echo ✓ Node.js found
)

echo.
echo [3] Available options:
echo.
echo   Option A: Fetch data from ediprod and view dashboard
echo   Option B: Start backend API server (requires Node.js)
echo   Option C: Open dashboard in browser
echo   Option Q: Quit
echo.

:menu
set /p choice="Select option (A/B/C/Q): "

if /i "%choice%"=="A" (
    echo.
    echo Fetching data from ediprod...
    echo.
    python fetch_ediprod_data.py --limit 20
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to fetch data from ediprod
        echo Make sure you have EDI-Prod MCP server configured.
        echo.
        pause
    ) else (
        echo.
        echo ✓ Data fetched successfully to dashboard_data.json
        echo.
    )
    goto menu
)

if /i "%choice%"=="B" (
    echo.
    echo Starting backend API server...
    echo This will run on http://localhost:3000
    echo Press Ctrl+C to stop the server
    echo.
    
    REM Check if node_modules exists
    if not exist "node_modules" (
        echo Installing dependencies...
        call npm install express cors
        if errorlevel 1 (
            echo ERROR: Failed to install dependencies
            pause
            exit /b 1
        )
    )
    
    REM Start the server
    node backend.js
    goto menu
)

if /i "%choice%"=="C" (
    echo.
    echo Opening dashboard in browser...
    start "" defect_dashboard.html
    echo.
    echo Dashboard opened! Check your browser.
    echo.
    goto menu
)

if /i "%choice%"=="Q" (
    echo.
    echo Exiting...
    exit /b 0
)

echo Invalid option. Please try again.
goto menu
