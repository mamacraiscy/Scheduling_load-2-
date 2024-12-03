@echo off
rem Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and try again.
    pause
    exit /b
)

rem Check if Django is installed globally
python -c "import django" >nul 2>&1
if %errorlevel% neq 0 (
    echo Django is not installed globally. Please install Django and try again.
    pause
    exit /b
)

rem Start Django development server
echo Starting Django server...
python manage.py runserver

rem Prevent the batch file from closing immediately
pause
