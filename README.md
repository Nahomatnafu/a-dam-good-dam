# Stills Exporter

A cross-platform GUI application for extracting frames from video files with parallel processing for maximum efficiency.

## 🚀 Features

- **Cross-platform**: Works on Windows, macOS, and Linux
- **Parallel processing**: Process multiple videos simultaneously for faster extraction
- **Multiple video formats**: Supports MP4, MOV, MKV, AVI, MTS, M2TS, WMV, WebM, 3GP, M4V, and more
- **Flexible output**: Choose PNG, JPG, BMP, or TIFF formats
- **Smart frame selection**: Evenly spaced frames avoiding head/tail slates
- **Clean interface**: Simple, intuitive GUI
- **Progress tracking**: Real-time progress updates and logging
- **Settings persistence**: Remembers your preferences

## 📋 Requirements

### Essential
- **FFmpeg** must be installed and available in your system PATH
- **Python 3.7+** (for running from source)

### FFmpeg Installation

#### Windows:
1. Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add the `bin` folder to your PATH environment variable

#### macOS:
```bash
# Using Homebrew (recommended)
brew install ffmpeg

# Using MacPorts
sudo port install ffmpeg
```

#### Linux:
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# CentOS/RHEL/Fedora
sudo dnf install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg
```

## 🚀 Quick Start

### Running from Source
```bash
# Clone the repository
git clone https://github.com/yourusername/stills-exporter.git
cd stills-exporter

# Run the application
python run.py
# or on Windows: double-click run.bat
```

## 🏗️ Building Standalone Application

### Quick Build (Recommended)

#### Windows:
1. Double-click `build/build_windows.bat`
2. Wait for the build to complete
3. Find `StillsExporter.exe` in the `dist` folder

#### macOS:
1. Open Terminal in the project folder
2. Run: `./build/build_mac.sh`
3. Find `StillsExporter.app` in the `dist` folder

### Manual Build
```bash
# Install dependencies
pip install pyinstaller

# Run build script
cd build
python build_app.py
```

## 🎯 Usage

### GUI Application
1. Launch the application (`StillsExporter.exe` or `StillsExporter.app`)
2. **Source Folder**: Select folder containing your video files
3. **Output Folder**: Choose where to save extracted frames
4. **Settings**:
   - **Frames per clip**: Number of frames to extract from each video (1-100)
   - **Image format**: PNG (best quality), JPG (smaller files), BMP, or TIFF
   - **Parallel workers**: Number of videos to process simultaneously (1-16)
5. Click **Start Export**
6. Monitor progress in the log area

### Command Line (PowerShell - Original)
```powershell
.\scripts\export_stills.ps1 -InputDir "C:\Videos" -OutputDir "C:\Stills" -FramesPerClip 10 -ImageExt png
```

### Command Line (PowerShell - Improved with Parallel Processing)
```powershell
.\scripts\improved_export_stills.ps1 -InputDir "C:\Videos" -OutputDir "C:\Stills" -FramesPerClip 10 -ImageExt png -MaxParallel 4
```

## ⚡ Performance Improvements

The new version includes several efficiency improvements over the original PowerShell script:

### Original Script Efficiency
Your original PowerShell script was already quite good:
- ✅ Accurate seeking with `-ss` after `-i`
- ✅ Smart timestamp calculation
- ✅ Clean filename handling
- ✅ Good error handling

### New Improvements
1. **Parallel Processing**: Process multiple videos simultaneously
2. **Batch Frame Extraction**: Extract multiple frames in single FFmpeg calls when possible
3. **Optimized File I/O**: Reduced disk operations
4. **Better Resource Management**: Configurable worker threads
5. **Cross-platform Compatibility**: Works on Windows, macOS, and Linux

### Performance Comparison
- **Original**: Sequential processing, ~1 video at a time
- **Improved**: Parallel processing, 2-8 videos simultaneously
- **Expected speedup**: 2-4x faster on multi-core systems

## 📁 Output Structure

Extracted frames are saved with the following naming convention:
```
{clean_video_name}_{frame_number}.{extension}

Examples:
- MyVideo_001.png
- MyVideo_002.png
- Another_Clip_001.jpg
```

## 🔧 Configuration

The GUI application automatically saves your settings to:
- **Windows**: `%USERPROFILE%\.stills_exporter_config.json`
- **macOS/Linux**: `~/.stills_exporter_config.json`

## 🐛 Troubleshooting

### "FFmpeg not found"
- Ensure FFmpeg is installed and in your system PATH
- Test by opening terminal/command prompt and typing: `ffmpeg -version`

### "No video files found"
- Check that your source folder contains supported video files
- Supported formats: MP4, MOV, MKV, AVI, MTS, M2TS, WMV, WebM, 3GP, M4V

### Application won't start
- Ensure you have Python 3.7+ installed (if running from source)
- Check that all dependencies are installed: `pip install -r requirements.txt`

### Slow performance
- Reduce the number of parallel workers if your system is struggling
- Use JPG format instead of PNG for faster processing
- Ensure your storage drive has sufficient free space

## 📝 Project Structure

```
stills-exporter/
├── src/                        # Source code
│   └── stills_exporter_gui.py  # Main GUI application
├── scripts/                    # PowerShell scripts
│   ├── export_stills.ps1       # Original PowerShell script
│   └── improved_export_stills.ps1  # Improved script with parallel processing
├── build/                      # Build scripts and tools
│   ├── build_app.py            # Build script for creating executables
│   ├── build_windows.bat       # Windows build helper
│   └── build_mac.sh            # macOS build helper
├── tests/                      # Test files
│   └── test_app.py             # Test suite
├── docs/                       # Documentation
│   └── EFFICIENCY_ANALYSIS.md  # Performance analysis
├── run.py                      # Main launcher script
├── run.bat                     # Windows launcher
├── requirements.txt            # Python dependencies
├── LICENSE                     # MIT License
├── CONTRIBUTING.md             # Contribution guidelines
└── README.md                   # This file
```

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.

## 📄 License

This project is open source. Feel free to use, modify, and distribute as needed.

---

**Note**: This application is a wrapper around FFmpeg. All video processing is performed by FFmpeg, which is a separate, powerful multimedia framework.
