# Development Guide

## Setting Up Development Environment

### 1. Clone and Setup
```bash
git clone <repo-url>
cd media-catalog
pip install -r requirements.txt
```

### 2. Test Data Setup
You'll need the `NeoFinder_Test` folder with sample videos. Ask the project owner for:
- `NeoFinder_Test/Proxies/` - Sample proxy videos
- `NeoFinder_Test/Test2/` - Additional test videos

Place this folder at: `C:/Users/[username]/Videos/NeoFinder_Test/`

Or update the paths in test files to match your setup.

### 3. Verify Setup
```bash
python test_catalog_foundation.py
```

## Current Architecture

### Database Layer (`src/database.py`)
- SQLite-based catalog storage
- Tables: files, keywords, file_keywords, metadata
- Full-text search capabilities
- Optimized indexes for performance

### File Scanner (`src/file_scanner.py`)
- Recursive directory scanning
- FFmpeg integration for video metadata
- Support for multiple video/image formats
- Error handling for corrupted files

### AI Integration (Existing)
- `vision_tagger.py` - Google Vision API integration
- `exif_embedder.py` - Metadata embedding with ExifTool
- Mock mode for development without API credentials

## Development Workflow

### Sprint-Based Development
We're following 8 sprints, currently on Sprint 2. Check `docs/SPRINTS.md` for details.

### Testing Strategy
- Unit tests for each component
- Integration tests for full workflows
- Performance benchmarks (planned for Sprint 7)

### Code Organization
```
src/
├── database.py          # Data layer
├── file_scanner.py      # File system integration
├── media_catalog_gui.py # GUI layer (Sprint 2+)
├── vision_tagger.py     # AI analysis
└── exif_embedder.py     # Metadata embedding
```

## Common Development Tasks

### Adding New File Formats
1. Update `FileScanner.video_extensions` or `image_extensions`
2. Test with sample files
3. Update documentation

### Database Schema Changes
1. Modify `CatalogDatabase._create_tables()`
2. Consider migration strategy for existing catalogs
3. Update test data

### GUI Development (Sprint 2+)
- Using tkinter for cross-platform compatibility
- Consider PyQt upgrade for advanced features
- Follow existing stills-exporter GUI patterns

## Debugging Tips

### Database Issues
```python
# Connect to catalog directly
import sqlite3
conn = sqlite3.connect('catalogs/test_catalog.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM files LIMIT 5')
print(cursor.fetchall())
```

### File Scanner Issues
```python
# Test individual file processing
from src.file_scanner import FileScanner
scanner = FileScanner()
info = scanner._extract_file_info(Path('path/to/test/file.mp4'))
print(info)
```

### AI Analysis Issues
```python
# Test AI components separately
from src.vision_tagger import VisionTagger
tagger = VisionTagger(mock_mode=True)
result = tagger.analyze_image('path/to/image.jpg')
print(result)
```

## Performance Considerations

### Database Optimization
- Indexes on frequently queried columns
- Batch operations for large imports
- Connection pooling for GUI responsiveness

### File System Operations
- Async scanning for large directories
- Thumbnail caching
- Progress reporting for long operations

## Next Steps for New Contributors

1. **Understand the Foundation**: Run and study `test_catalog_foundation.py`
2. **Pick a Sprint Task**: Check current sprint in `docs/SPRINTS.md`
3. **Start Small**: Begin with bug fixes or small features
4. **Ask Questions**: Don't hesitate to ask about architecture decisions

## Useful Commands

```bash
# Run foundation tests
python test_catalog_foundation.py

# Test AI features
python test_ai_features.py

# Check database contents
sqlite3 catalogs/test_catalog.db ".tables"
sqlite3 catalogs/test_catalog.db "SELECT COUNT(*) FROM files;"

# Clean reset
rm -rf catalogs/ thumbnails/
python test_catalog_foundation.py
```