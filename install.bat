@echo off
setlocal enabledelayedexpansion

REM Network Monitor Installer for Windows
REM Run this script as Administrator

echo.
echo =========================================
echo     Network Monitor - Easy Installer
echo =========================================
echo.

REM Check if running as Administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: This installer must be run as Administrator!
    echo.
    echo Right-click on this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.9+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo    Python %PYVER% found
echo.

echo [2/5] Checking Npcap installation...
if exist "C:\Windows\System32\Npcap\wpcap.dll" (
    echo    Npcap is installed
) else if exist "C:\Windows\System32\wpcap.dll" (
    echo    WinPcap found (may need Npcap for best compatibility)
) else (
    echo WARNING: Npcap not detected!
    echo.
    echo Please download and install Npcap from https://npcap.com
    echo During installation, enable "Install Npcap in WinPcap API-compatible Mode"
    echo.
    set /p CONTINUE="Continue anyway? (y/n): "
    if /i not "!CONTINUE!"=="y" (
        exit /b 1
    )
)
echo.

echo [3/5] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo    Virtual environment created
) else (
    echo    Virtual environment already exists
)
echo.

echo [4/5] Installing Python dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)
echo    Dependencies installed successfully
echo.

echo [5/5] Testing installation...
python -c "from networkmonitor.monitor import NetworkController; print('OK')" >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Some components may not be working correctly
    echo    Run the application to see detailed error messages
) else (
    echo    Installation verified successfully
)
echo.

echo =========================================
echo     Installation Complete!
echo =========================================
echo.
echo To start Network Monitor:
echo    1. Double-click "start.bat" (recommended)
echo    2. Or run: python -m networkmonitor
echo.
echo The web interface will open automatically at:
echo    http://localhost:5000
echo.
echo For Vercel deployment, the frontend will connect to
echo your local backend at http://localhost:5000
echo.

REM Create start script
echo @echo off > start.bat
echo call venv\Scripts\activate.bat >> start.bat
echo python -m networkmonitor >> start.bat

echo Created start.bat for easy launching
echo.
pause
