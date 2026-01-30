@echo off
REM Startup script for the Todo App Backend on Windows

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo.
    echo ⚠️  Warning: .env file not found!
    echo Please copy .env.example to .env and configure your database settings:
    echo copy .env.example .env
    echo Then edit .env with your Neon database connection string
    exit /b 1
)

REM Setup database tables
echo Setting up database tables...
python setup_database.py

REM Start the application
echo Starting the application...
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload