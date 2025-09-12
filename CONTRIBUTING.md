# Contributing to Stills Exporter

Thank you for your interest in contributing to Stills Exporter! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/stills-exporter.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes: `python tests/test_app.py`
6. Commit your changes: `git commit -am 'Add some feature'`
7. Push to the branch: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Setup

### Prerequisites
- Python 3.7+
- FFmpeg installed and in PATH

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/stills-exporter.git
cd stills-exporter

# Install development dependencies
pip install -r requirements.txt

# Run tests to verify setup
python tests/test_app.py

# Run the application
python src/stills_exporter_gui.py
```

## Project Structure

```
stills-exporter/
├── src/                    # Source code
│   └── stills_exporter_gui.py
├── scripts/                # PowerShell scripts
│   ├── export_stills.ps1
│   └── improved_export_stills.ps1
├── build/                  # Build scripts and tools
│   ├── build_app.py
│   ├── build_windows.bat
│   └── build_mac.sh
├── tests/                  # Test files
│   └── test_app.py
├── docs/                   # Documentation
│   └── EFFICIENCY_ANALYSIS.md
├── README.md
├── requirements.txt
├── LICENSE
└── .gitignore
```

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small
- Add comments for complex logic

## Testing

Before submitting a pull request:

1. Run the test suite: `python tests/test_app.py`
2. Test the GUI application manually
3. Test on multiple platforms if possible (Windows, macOS, Linux)
4. Verify FFmpeg integration works correctly

## Reporting Issues

When reporting issues, please include:

1. Operating system and version
2. Python version
3. FFmpeg version (`ffmpeg -version`)
4. Steps to reproduce the issue
5. Expected vs actual behavior
6. Error messages or logs

## Feature Requests

We welcome feature requests! Please:

1. Check if the feature already exists or is planned
2. Describe the use case and benefit
3. Provide examples if applicable
4. Consider if it fits the project's scope

## Areas for Contribution

- **Performance improvements**: Optimize video processing
- **UI/UX enhancements**: Improve the GUI interface
- **Platform support**: Better integration with different operating systems
- **Documentation**: Improve guides and documentation
- **Testing**: Add more comprehensive tests
- **Bug fixes**: Fix reported issues

## Pull Request Guidelines

- Keep pull requests focused on a single feature or fix
- Write clear commit messages
- Update documentation if needed
- Add tests for new functionality
- Ensure all tests pass
- Follow the existing code style

## Questions?

If you have questions about contributing, feel free to:
- Open an issue for discussion
- Contact the maintainers

Thank you for contributing to Stills Exporter!
