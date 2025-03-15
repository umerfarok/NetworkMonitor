@echo off
TITLE NetworkMonitor Debug Launcher
MODE CON: COLS=120 LINES=40

ECHO ========================================================
ECHO NetworkMonitor Debug Launcher
ECHO ========================================================
ECHO.

:: Check for admin privileges
NET SESSION >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO Administrator privileges required!
    ECHO Right-click on this batch file and select "Run as administrator"
    PAUSE
    EXIT /B 1
)

:: Set up the environment
SET PYTHONPATH=%~dp0
CD /D %~dp0

:: Activate virtual environment if it exists
IF EXIST "venv\Scripts\activate.bat" (
    ECHO Activating virtual environment...
    CALL venv\Scripts\activate.bat
) ELSE (
    ECHO Virtual environment not found at venv\Scripts\activate.bat
    ECHO Please ensure the virtual environment is set up correctly
    PAUSE
    EXIT /B 1
)

ECHO Running with administrator privileges
ECHO Logging to networkmonitor_debug_batch.log
ECHO.

:: Enable extended console output
SET PYTHONUNBUFFERED=1
SET PYTHONIOENCODING=UTF-8

:: Run the application with output going to both console and log file
python -u "%~dp0start_networkmonitor.py" 2>&1 | TEE networkmonitor_debug_batch.log

IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO Application exited with error code: %ERRORLEVEL%
    ECHO Check networkmonitor_debug_batch.log for details
    TYPE networkmonitor_debug_batch.log
) ELSE (
    ECHO Application exited successfully
)

:: Deactivate virtual environment
deactivate

ECHO.
ECHO Press any key to exit...
PAUSE >NUL