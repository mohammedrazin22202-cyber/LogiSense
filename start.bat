@echo off
title TRACK FLEET COMMAND
color 0B

echo.
echo  ============================================
echo    TRACK FLEET COMMAND - Starting...
echo  ============================================
echo.

:: Check Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found.
    echo  Please install Python from https://www.python.org/downloads/
    echo  Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

:: Install dependencies
echo  [1/3] Installing dependencies...
python -m pip install flask openpyxl mysql-connector-python --quiet
if errorlevel 1 (
    echo  [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo        Done.

:: Check if orders_master.xlsx exists
if not exist "orders_master.xlsx" (
    echo.
    echo  [WARNING] orders_master.xlsx not found in this folder.
    echo  Please copy orders_master.xlsx into this folder and re-run.
    pause
    exit /b 1
)

:: Seed database
echo  [2/3] Seeding MySQL database from orders_master.xlsx...
echo         (Make sure MySQL is running and config.py credentials are correct)
python backend\seed.py
if errorlevel 1 (
    echo  [ERROR] Database seeding failed.
    echo          Check that MySQL is running and backend\config.py has the right credentials.
    pause
    exit /b 1
)
echo        Done.

:: Start the server
echo  [3/3] Starting server on http://localhost:1995
echo.
echo  ============================================
echo    Open your browser at:
echo    http://localhost:1995
echo  ============================================
echo.
echo  Press Ctrl+C to stop the server.
echo.

:: Open browser automatically after 2 seconds
start "" timeout /t 2 >nul
start "" "http://localhost:1995"

:: Run server
python backend\server.py

pause
