# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-11

### Added
- Cross-platform GUI application with tkinter
- Parallel processing support for faster video processing
- Support for multiple video formats (MP4, MOV, MKV, AVI, MTS, M2TS, WMV, WebM, 3GP, M4V)
- Multiple output formats (PNG, JPG, BMP, TIFF)
- Real-time progress tracking and logging
- Settings persistence (remembers user preferences)
- Configurable parallel workers (1-16 threads)
- Smart frame selection avoiding head/tail slates
- Clean filename sanitization
- Comprehensive error handling
- Cross-platform build scripts (Windows, macOS, Linux)
- Professional project structure
- Comprehensive documentation
- Test suite for validation
- MIT License

### PowerShell Scripts
- Original PowerShell script (`scripts/export_stills.ps1`)
- Improved PowerShell script with parallel processing (`scripts/improved_export_stills.ps1`)

### Build System
- PyInstaller-based build system
- Windows batch file for easy building
- macOS shell script for easy building
- Cross-platform Python build script

### Documentation
- Comprehensive README with installation and usage instructions
- Efficiency analysis comparing original vs improved versions
- Installation guide with troubleshooting
- Contributing guidelines
- Project structure documentation

### Performance Improvements
- 2-4x faster processing with parallel execution
- Batch frame extraction for reduced overhead
- Optimized file I/O operations
- Better resource utilization on multi-core systems

### Features
- **GUI Interface**: Clean, intuitive interface with progress tracking
- **Batch Processing**: Process multiple videos simultaneously
- **Format Support**: Wide range of input video formats and output image formats
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Standalone Executables**: Build standalone apps for distribution
- **Command Line**: PowerShell scripts for automation
- **Error Handling**: Robust error handling and user feedback
- **Settings**: Persistent settings and configuration

## [Unreleased]

### Planned
- GPU acceleration support
- Drag-and-drop interface
- Video preview thumbnails
- Batch job queuing
- Custom timestamp selection
- Video metadata extraction
- Integration with video editing software
- Plugin system for custom processors

---

## Version History

- **v1.0.0**: Initial release with GUI, parallel processing, and cross-platform support
