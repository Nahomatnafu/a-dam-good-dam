# Installation Guide

This guide covers different ways to install and run Stills Exporter.

## Prerequisites

### Required
- **Python 3.7+** (for running from source)
- **FFmpeg** (must be installed and in PATH)

### FFmpeg Installation

#### Windows
1. Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extract to `C:\ffmpeg` (or your preferred location)
3. Add `C:\ffmpeg\bin` to your system PATH:
   - Open System Properties → Advanced → Environment Variables
   - Edit the PATH variable and add the FFmpeg bin directory
   - Restart your command prompt/terminal

#### macOS
```bash
# Using Homebrew (recommended)
brew install ffmpeg

# Using MacPorts
sudo port install ffmpeg
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# CentOS/RHEL/Fedora
sudo dnf install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg
```

### Verify FFmpeg Installation
```bash
ffmpeg -version
```
You should see version information if FFmpeg is properly installed.

## Installation Methods

### Method 1: Download Pre-built Executable (Easiest)

1. Go to the [Releases](https://github.com/yourusername/stills-exporter/releases) page
2. Download the appropriate file for your system:
   - Windows: `StillsExporter.exe`
   - macOS: `StillsExporter.app`
   - Linux: `StillsExporter` (AppImage)
3. Run the downloaded file

### Method 2: Run from Source (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/yourusername/stills-exporter.git
cd stills-exporter

# Run the application
python run.py

# Or on Windows, double-click run.bat
```

### Method 3: Install as Python Package

```bash
# Clone and install
git clone https://github.com/yourusername/stills-exporter.git
cd stills-exporter
pip install -e .

# Run from anywhere
stills-exporter
```

### Method 4: Build Your Own Executable

#### Windows
```bash
# Clone the repository
git clone https://github.com/yourusername/stills-exporter.git
cd stills-exporter

# Run the build script
build\build_windows.bat

# Find the executable in dist/StillsExporter.exe
```

#### macOS
```bash
# Clone the repository
git clone https://github.com/yourusername/stills-exporter.git
cd stills-exporter

# Run the build script
./build/build_mac.sh

# Find the app in dist/StillsExporter.app
```

#### Linux
```bash
# Clone the repository
git clone https://github.com/yourusername/stills-exporter.git
cd stills-exporter

# Install PyInstaller
pip install pyinstaller

# Build
cd build
python build_app.py

# Find the executable in dist/StillsExporter
```

## Development Setup

For contributors and developers:

```bash
# Clone the repository
git clone https://github.com/yourusername/stills-exporter.git
cd stills-exporter

# Install development dependencies
pip install -r requirements.txt

# Run tests
python tests/test_app.py

# Run the application
python run.py
```

## Troubleshooting

### "FFmpeg not found" Error
- Ensure FFmpeg is installed and in your system PATH
- Test with: `ffmpeg -version`
- On Windows, you may need to restart your terminal after adding FFmpeg to PATH

### "Python not found" Error (Windows)
- Install Python from [python.org](https://python.org)
- Make sure to check "Add Python to PATH" during installation
- Or use the Microsoft Store version of Python

### Permission Denied (macOS/Linux)
```bash
# Make scripts executable
chmod +x build/build_mac.sh
chmod +x run.py
```

### Import Errors
- Make sure you're running from the project root directory
- Check that all files are in the correct locations according to the project structure

### GUI Won't Start
- Ensure you have a display/desktop environment (not running in headless mode)
- On Linux, you may need to install tkinter: `sudo apt install python3-tk`

## System Requirements

### Minimum
- Python 3.7+
- 2GB RAM
- 100MB free disk space
- FFmpeg

### Recommended
- Python 3.9+
- 4GB+ RAM (for parallel processing)
- SSD storage (for faster I/O)
- Multi-core CPU (for parallel processing benefits)

## Uninstallation

### Pre-built Executable
Simply delete the executable file.

### Python Package Installation
```bash
pip uninstall stills-exporter
```

### Source Installation
Delete the cloned repository folder.

## Getting Help

If you encounter issues:

1. Check this installation guide
2. Review the main [README.md](../README.md)
3. Check the [Issues](https://github.com/yourusername/stills-exporter/issues) page
4. Create a new issue with:
   - Your operating system and version
   - Python version (`python --version`)
   - FFmpeg version (`ffmpeg -version`)
   - Error messages or screenshots
