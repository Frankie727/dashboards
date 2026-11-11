@echo off
REM Dashboard Setup Verification Script
REM Checks if all components are properly configured

setlocal enabledelayedexpansion

echo.
echo ========================================
echo  Defect Dashboard - Setup Verification
echo ========================================
echo.

set "DASHBOARD_DIR=%CD%"
set "CHECKS_PASSED=0"
set "CHECKS_TOTAL=0"

REM Helper function to check a condition
set "CHECK_PASS=echo [✓] %~1 && set /a CHECKS_PASSED+=1"
set "CHECK_FAIL=echo [✗] %~1"

REM Check 1: Dashboard directory
set /a CHECKS_TOTAL+=1
if exist "defect_dashboard.html" (
    %CHECK_PASS:~5% - defect_dashboard.html found
) else (
    %CHECK_FAIL:~5% - defect_dashboard.html NOT found
)

REM Check 2: Python script
set /a CHECKS_TOTAL+=1
if exist "fetch_ediprod_data.py" (
    %CHECK_PASS:~5% - fetch_ediprod_data.py found
) else (
    %CHECK_FAIL:~5% - fetch_ediprod_data.py NOT found
)

REM Check 3: Backend script
set /a CHECKS_TOTAL+=1
if exist "backend.js" (
    %CHECK_PASS:~5% - backend.js found
) else (
    %CHECK_FAIL:~5% - backend.js NOT found
)

REM Check 4: Setup script
set /a CHECKS_TOTAL+=1
if exist "run_dashboard.bat" (
    %CHECK_PASS:~5% - run_dashboard.bat found
) else (
    %CHECK_FAIL:~5% - run_dashboard.bat NOT found
)

REM Check 5: Package.json
set /a CHECKS_TOTAL+=1
if exist "package.json" (
    %CHECK_PASS:~5% - package.json found
) else (
    %CHECK_FAIL:~5% - package.json NOT found
)

REM Check 6: Documentation
set /a CHECKS_TOTAL+=1
if exist "README.md" (
    %CHECK_PASS:~5% - README.md found
) else (
    %CHECK_FAIL:~5% - README.md NOT found
)

REM Check 7: Quick Start
set /a CHECKS_TOTAL+=1
if exist "QUICKSTART.md" (
    %CHECK_PASS:~5% - QUICKSTART.md found
) else (
    %CHECK_FAIL:~5% - QUICKSTART.md NOT found
)

REM Check 8: Integration Guide
set /a CHECKS_TOTAL+=1
if exist "INTEGRATION_GUIDE.md" (
    %CHECK_PASS:~5% - INTEGRATION_GUIDE.md found
) else (
    %CHECK_FAIL:~5% - INTEGRATION_GUIDE.md NOT found
)

REM Check 9: Python Installation
set /a CHECKS_TOTAL+=1
echo.
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    %CHECK_FAIL:~5% - Python not found (REQUIRED)
    echo    Install from: https://www.python.org/
) else (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
    %CHECK_PASS:~5% - !PYTHON_VERSION!
)

REM Check 10: Node.js Installation
set /a CHECKS_TOTAL+=1
echo Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    %CHECK_FAIL:~5% - Node.js not found (OPTIONAL)
    echo    Install from: https://nodejs.org/ (for backend API only)
) else (
    for /f "tokens=*" %%i in ('node --version') do set "NODE_VERSION=%%i"
    %CHECK_PASS:~5% - Node.js !NODE_VERSION! found
)

REM Check 11: MCP Configuration File
set /a CHECKS_TOTAL+=1
echo Checking MCP configuration...
if exist ".vscode\settings.json" (
    %CHECK_PASS:~5% - VS Code settings found
) else (
    %CHECK_FAIL:~5% - .vscode\settings.json not found (MCP config may be needed)
)

REM Check 12: Browser Availability
set /a CHECKS_TOTAL+=1
echo Checking browser availability...
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    %CHECK_PASS:~5% - Chrome browser found
) else if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
    %CHECK_PASS:~5% - Chrome browser found
) else if exist "%ProgramFiles%\Mozilla Firefox\firefox.exe" (
    %CHECK_PASS:~5% - Firefox browser found
) else (
    echo [!] Browser not found - will use default browser
    set /a CHECKS_PASSED+=1
)

echo.
echo ========================================
echo  Verification Results
echo ========================================
echo.
echo Checks Passed: !CHECKS_PASSED!/!CHECKS_TOTAL!
echo.

if "!CHECKS_PASSED!"=="!CHECKS_TOTAL!" (
    echo ✓ All checks passed! Dashboard is ready to use.
    echo.
    echo Next steps:
    echo   1. Run: run_dashboard.bat
    echo   2. Select option A to fetch data
    echo   3. Select option C to open dashboard
    echo.
) else (
    echo ⚠ Some checks failed. Review above for details.
    echo.
    echo Required to proceed:
    echo   • Python 3.7+
    echo   • Web browser
    echo.
    echo Optional for full features:
    echo   • Node.js (for backend API)
    echo   • MCP configuration
    echo.
)

REM Check if we can run the main script
echo ========================================
echo  Quick Start Options
echo ========================================
echo.
if exist "run_dashboard.bat" (
    echo Type this command to start:
    echo   run_dashboard.bat
    echo.
)

if exist "QUICKSTART.md" (
    echo For detailed instructions:
    echo   • Open QUICKSTART.md
    echo   • Or INTEGRATION_GUIDE.md
    echo.
)

echo ========================================
echo.
pause
