@echo off
echo ================================================
echo Starting Todo App Backend with OpenRouter Config
echo ================================================

echo Stopping any existing backend processes...
taskkill /f /im uvicorn.exe 2>nul

echo.
echo Starting backend server...
cd backend
echo Server starting on http://localhost:8000
echo.
echo NOTE: This may take a moment to initialize...
echo.

uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

if errorlevel 1 (
    echo.
    echo ERROR: Server failed to start!
    echo Please check:
    echo 1. Python and required packages are installed
    echo 2. Port 8000 is available
    echo 3. All dependencies are properly installed
    pause
)