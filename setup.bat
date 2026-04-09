@echo off
REM setup.bat - Setup script for Windows

echo.
echo ========================================================
echo   Smart City Traffic Management System - Setup
echo ========================================================
echo.

REM Check Python
echo [*] Checking Python version...
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.11+
    pause
    exit /b 1
)

REM Create virtual environment
if not exist "venv" (
    echo [*] Creating virtual environment...
    python -m venv venv
) else (
    echo [✓] Virtual environment already exists
)

REM Activate virtual environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Upgrade pip
echo [*] Upgrading pip...
python -m pip install --upgrade pip setuptools

REM Install requirements
echo [*] Installing dependencies from requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)

REM Download YOLO model
echo [*] Downloading YOLO model...
echo     (This may take a few minutes first time...)
python -c "from ultralytics import YOLO; model = YOLO('yolov8s.pt'); print('✅ Model downloaded')"

REM Check static files
echo [*] Checking for video files...
if exist "static\traffic1.mp4" (
    echo     ✓ traffic1.mp4 found
) else (
    echo     ⚠ traffic1.mp4 NOT found
    echo       Add MP4 files to static\ folder
)

echo.
echo ========================================================
echo   Setup Complete!
echo ========================================================
echo.
echo To run the application:
echo   python app.py
echo.
echo Dashboard will be available at:
echo   http://localhost:5000
echo.
pause
