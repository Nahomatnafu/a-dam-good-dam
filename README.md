# Media Catalog - NeoFinder Alternative with AI Analysis

A cross-platform media cataloging application that scans video/image files, performs AI analysis for automatic tagging, and provides powerful search capabilities.

## 🎯 Project Overview

This project builds on the existing Stills Exporter codebase to create a comprehensive media catalog system similar to NeoFinder, but with integrated AI analysis capabilities using Google Cloud Vision API.

### Key Features (Planned)
- 📁 **Media Cataloging**: Scan folders and create searchable catalogs
- 🤖 **AI Analysis**: Automatic keyword generation using Google Vision API
- 🔍 **Advanced Search**: Search by filename, keywords, metadata
- 🏷️ **Tag Management**: Add, edit, remove tags with sidebar interface
- 👁️ **Preview Panel**: Video thumbnails and metadata display
- 📍 **File Location**: "Show in Explorer/Finder" functionality
- 💾 **Metadata Embedding**: Write keywords back to video files

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- FFmpeg (for video processing)
- ExifTool (for metadata embedding)
- Google Cloud Vision API credentials (optional, for AI analysis)

### Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd media-catalog

# Install dependencies
pip install -r requirements.txt

# Test the foundation
python test_catalog_foundation.py
```

## 📁 Project Structure

```
media-catalog/
├── src/                          # Core application code
│   ├── database.py               # SQLite catalog management
│   ├── file_scanner.py           # Directory scanning & metadata extraction
│   ├── media_catalog_gui.py      # Main GUI application (Sprint 2)
│   ├── vision_tagger.py          # AI analysis (from stills-exporter)
│   └── exif_embedder.py          # Metadata embedding (from stills-exporter)
├── catalogs/                     # SQLite database files
├── thumbnails/                   # Generated video thumbnails
├── test_data/                    # Test videos/images (NeoFinder_Test)
├── tests/                        # Test scripts
│   └── test_catalog_foundation.py
├── docs/                         # Documentation
│   ├── DEVELOPMENT.md            # Development guide
│   └── SPRINTS.md                # Sprint planning
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## 🏗️ Development Status

### ✅ Sprint 1: Foundation & Database (COMPLETED)
- Database schema with files, keywords, metadata tables
- File scanner with FFmpeg integration
- Basic search and keyword management
- Test suite for foundation components

### 🚧 Sprint 2: Basic GUI Framework (IN PROGRESS)
- Main window with menu/toolbar
- Catalog management (create/open)
- File list display

### 📋 Upcoming Sprints
- Sprint 3: Search & Filter System
- Sprint 4: Preview & Metadata Panel
- Sprint 5: Tag Management Sidebar
- Sprint 6: AI Analysis Integration
- Sprint 7: Performance & Polish
- Sprint 8: Advanced Features

## 🧪 Testing

### Test the Foundation
```bash
python test_catalog_foundation.py
```

### Test AI Features (if credentials available)
```bash
python test_ai_features.py
```

## 🤝 Contributing

### Getting Started
1. Make sure you have the test data folder (`NeoFinder_Test`) in the right location
2. Run the foundation test to ensure everything works
3. Check the current sprint status in `docs/SPRINTS.md`
4. Pick up tasks from the current sprint

### Development Workflow
1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and test thoroughly
3. Update documentation if needed
4. Create a pull request

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to classes and functions
- Test your changes before committing

## 📊 Architecture

### Database Schema
- **files**: Main file information (path, size, duration, etc.)
- **keywords**: Unique keyword list
- **file_keywords**: Many-to-many relationship between files and keywords
- **metadata**: Additional file metadata and AI analysis results

### AI Integration
- Uses existing `VisionTagger` from stills-exporter project
- Embeds keywords into video files using `ExifEmbedder`
- Supports both mock and real Google Vision API analysis

## 🔧 Configuration

### Google Cloud Vision (Optional)
1. Create a Google Cloud project
2. Enable Vision API
3. Create service account and download JSON credentials
4. Set environment variable or configure in app

### Test Data Setup
The project expects test data in: `C:/Users/15073/Videos/NeoFinder_Test/`
- Adjust paths in test files for your system
- Or create symbolic links to your test data location

## 📝 Notes for Collaborators

### Current Focus
We're building the core catalog functionality first, then adding the GUI layer. The AI analysis components already work from the stills-exporter project.

### Key Files to Understand
1. `src/database.py` - Core data management
2. `src/file_scanner.py` - File discovery and metadata extraction
3. `test_catalog_foundation.py` - Shows how everything fits together

### Next Steps
The immediate priority is Sprint 2: creating the basic GUI framework using tkinter (or potentially PyQt if we decide to upgrade).

## 🐛 Troubleshooting

### "FFmpeg not found"
- Install FFmpeg and add to PATH
- Test with: `ffmpeg -version`

### "No test directory found"
- Update paths in test files to match your system
- Or create the expected directory structure

### Database issues
- Delete `catalogs/test_catalog.db` to reset
- Check file permissions in the catalogs directory

## 📄 License

MIT License - feel free to use and modify as needed.
