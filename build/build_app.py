#!/usr/bin/env python3
"""
Build script for creating standalone executables of Stills Exporter
Supports Windows (.exe) and macOS (.app) builds
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Success!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def check_dependencies():
    """Check if required tools are available"""
    print("Checking dependencies...")
    
    # Check Python
    python_version = sys.version_info
    if python_version < (3, 7):
        print("❌ Python 3.7+ is required")
        return False
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check PyInstaller
    try:
        import PyInstaller
        print(f"✅ PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        if not run_command([sys.executable, "-m", "pip", "install", "pyinstaller"], "Installing PyInstaller"):
            return False
    
    return True

def build_executable():
    """Build the standalone executable"""
    system = platform.system().lower()
    
    # Base PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",  # Single executable file
        "--windowed",  # No console window (GUI app)
        "--name", "StillsExporter",
        "--clean",  # Clean build
    ]
    
    # Platform-specific options
    if system == "windows":
        cmd.extend([
            "--icon", "icon.ico" if Path("icon.ico").exists() else None,
            "--add-data", "README.md;.",
        ])
        output_name = "StillsExporter.exe"
    elif system == "darwin":  # macOS
        cmd.extend([
            "--icon", "icon.icns" if Path("icon.icns").exists() else None,
            "--add-data", "README.md:.",
        ])
        output_name = "StillsExporter.app"
    else:  # Linux
        cmd.extend([
            "--add-data", "README.md:.",
        ])
        output_name = "StillsExporter"
    
    # Remove None values
    cmd = [arg for arg in cmd if arg is not None]
    
    # Add the main script
    cmd.append("src/stills_exporter_gui.py")
    
    # Build
    if not run_command(cmd, f"Building {output_name}"):
        return False
    
    # Check if build was successful
    dist_path = Path("dist") / ("StillsExporter.exe" if system == "windows" else "StillsExporter")
    if system == "darwin":
        dist_path = Path("dist") / "StillsExporter.app"
    
    if dist_path.exists():
        print(f"✅ Build successful! Executable created at: {dist_path}")
        print(f"📁 File size: {dist_path.stat().st_size / (1024*1024):.1f} MB")
        return True
    else:
        print("❌ Build failed - executable not found")
        return False

def create_readme():
    """Create a README file for the application"""
    readme_content = """# Stills Exporter

A cross-platform GUI application for extracting frames from video files.

## Features

- Extract multiple frames from video files
- Support for various video formats (MP4, MOV, MKV, AVI, etc.)
- Parallel processing for faster extraction
- Clean, intuitive GUI
- Cross-platform (Windows, macOS, Linux)

## Requirements

- FFmpeg must be installed and available in your system PATH
- Download FFmpeg from: https://ffmpeg.org/download.html

## Usage

1. Launch the application
2. Select your source folder containing video files
3. Choose an output folder for the extracted frames
4. Configure settings (frames per clip, image format, etc.)
5. Click "Start Export" to begin processing

## Installation of FFmpeg

### Windows:
1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract to a folder (e.g., C:\\ffmpeg)
3. Add the bin folder to your PATH environment variable

### macOS:
```bash
# Using Homebrew
brew install ffmpeg

# Using MacPorts
sudo port install ffmpeg
```

### Linux:
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg
```

## Support

For issues or questions, please check that FFmpeg is properly installed and accessible from the command line.
"""
    
    with open("README.md", "w") as f:
        f.write(readme_content)
    print("✅ README.md created")

def main():
    """Main build process"""
    print("🚀 Stills Exporter Build Script")
    print("=" * 40)
    
    # Check if main script exists
    main_script = Path("src/stills_exporter_gui.py")
    if not main_script.exists():
        print("❌ src/stills_exporter_gui.py not found")
        print("Make sure you're running this from the project root directory")
        return 1
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed")
        return 1
    
    # Create README
    create_readme()
    
    # Build executable
    if not build_executable():
        print("❌ Build failed")
        return 1
    
    print("\n🎉 Build completed successfully!")
    print("\nNext steps:")
    print("1. Test the executable in the 'dist' folder")
    print("2. Make sure FFmpeg is installed on target systems")
    print("3. Distribute the executable along with the README")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
