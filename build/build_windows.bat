@echo off
echo Building Stills Exporter for Windows...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Install/upgrade pip and PyInstaller
echo Installing PyInstaller...
python -m pip install --upgrade pip
python -m pip install pyinstaller

REM Build the application
echo.
echo Building executable...
cd build
python build_app.py
cd ..

echo.
echo Build complete! Check the 'dist' folder for StillsExporter.exe
pause
