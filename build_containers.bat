@echo off
setlocal

echo Building Todo App Docker containers...

echo.
echo Building backend container...
cd backend
docker build -t todo-backend .
if %ERRORLEVEL% NEQ 0 (
    echo Failed to build backend container
    exit /b %ERRORLEVEL%
)
cd ..

echo.
echo Building frontend container...
cd frontend
docker build -t todo-frontend .
if %ERRORLEVEL% NEQ 0 (
    echo Failed to build frontend container
    exit /b %ERRORLEVEL%
)
cd ..

echo.
echo All containers built successfully!

echo.
echo To run individual containers, use the commands in the README.