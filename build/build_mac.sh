#!/bin/bash

echo "Building Stills Exporter for macOS..."
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7+ from https://python.org or use Homebrew:"
    echo "brew install python"
    exit 1
fi

# Install/upgrade pip and PyInstaller
echo "Installing PyInstaller..."
python3 -m pip install --upgrade pip
python3 -m pip install pyinstaller

# Build the application
echo
echo "Building application..."
cd build
python3 build_app.py
cd ..

echo
echo "Build complete! Check the 'dist' folder for StillsExporter.app"
echo "You can drag the .app file to your Applications folder"
