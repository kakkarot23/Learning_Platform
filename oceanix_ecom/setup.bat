@echo off
REM OCEANIX E-Commerce Platform - Quick Setup Script for Windows

echo.
echo ========================================
echo   OCEANIX E-Commerce Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo [1/6] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/6] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/6] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [4/6] Running database migrations...
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Failed to run migrations
    pause
    exit /b 1
)

echo [5/6] Creating superuser account...
echo.
echo Please enter superuser details:
python manage.py createsuperuser
if errorlevel 1 (
    echo ERROR: Failed to create superuser
    pause
    exit /b 1
)

echo [6/6] Loading sample products...
python manage.py load_sample_products
if errorlevel 1 (
    echo ERROR: Failed to load sample products
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Your OCEANIX website is ready to run!
echo.
echo To start the development server, run:
echo   python manage.py runserver
echo.
echo Then open your browser and visit:
echo   http://127.0.0.1:8000/
echo.
echo For admin panel, go to:
echo   http://127.0.0.1:8000/admin/
echo.
pause
