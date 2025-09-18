# Sprint Planning & Status

## Sprint Overview

### ✅ Sprint 1: Foundation & Database (COMPLETED)
**Duration**: Week 1  
**Goal**: Basic catalog creation and file scanning

#### Completed Tasks:
- [x] Database schema design (files, keywords, file_keywords, metadata tables)
- [x] `CatalogDatabase` class with CRUD operations
- [x] `FileScanner` class with FFmpeg integration
- [x] Search functionality (filename and keyword search)
- [x] Test suite (`test_catalog_foundation.py`)

#### Deliverables:
- Working command-line catalog system
- SQLite database with proper relationships
- File scanning with metadata extraction

---

### 🚧 Sprint 2: Basic GUI Framework (IN PROGRESS)
**Duration**: Week 2  
**Goal**: Functional GUI with catalog management

#### Tasks:
- [ ] Main window structure (menu bar, toolbar, status bar)
- [ ] Catalog management dialogs (new/open catalog)
- [ ] Folder selection for scanning
- [ ] Basic file list display (table view)
- [ ] Progress indicators for scanning

#### Acceptance Criteria:
- GUI app can create and open catalogs
- Can scan folders and display file lists
- Basic error handling and user feedback

---

### 🚧 Sprint 3: Enhanced Search & Polish (NEXT)
**Duration**: Week 3  
**Goal**: Advanced search capabilities and UI polish

#### Planned Tasks:
- [ ] **Advanced Search Panel**
  - Filter by file type (video/image)
  - Date range filtering (created/modified)
  - Keyword combination search (AND/OR logic)
  - Size range filtering

- [ ] **Tag Management Sidebar**
  - Interactive keyword list with usage counts
  - Click to filter by keyword
  - Add/remove keywords from selected files
  - Keyword autocomplete

- [ ] **Drag & Drop Support**
  - Drag folders directly into the app
  - Visual drop zones
  - Progress feedback during scanning

- [ ] **Keyboard Shortcuts**
  - Ctrl+O (Open Catalog)
  - Ctrl+N (New Catalog)
  - Ctrl+R (Refresh Catalog)
  - F5 (Refresh view)
  - Delete (Remove selected files)

- [ ] **Recent Catalogs Menu**
  - Quick access to recently opened catalogs
  - Persistent across sessions
  - "Pin" favorite catalogs

#### Deliverables:
- Professional-grade search interface
- Streamlined workflow with shortcuts
- Enhanced user experience

---

### 📋 Sprint 4: Preview & Metadata Panel (PLANNED)
**Duration**: Week 4  
**Goal**: Media preview and metadata display

#### Planned Tasks:
- [ ] Video thumbnail generation
- [ ] Preview panel layout
- [ ] Metadata display
- [ ] "Show in Explorer/Finder" functionality
- [ ] Split pane layout

---

### 📋 Sprint 5: Tag Management Sidebar (PLANNED)
**Duration**: Week 5  
**Goal**: Interactive tag editing

#### Planned Tasks:
- [ ] Tag sidebar with usage counts
- [ ] Add/remove/rename tags
- [ ] Drag-and-drop tag assignment
- [ ] Bulk tag operations
- [ ] Tag persistence to files

---

### 📋 Sprint 6: AI Analysis Integration (PLANNED)
**Duration**: Week 6  
**Goal**: Seamless AI processing

#### Planned Tasks:
- [ ] Background AI processing
- [ ] Progress tracking for analysis
- [ ] Batch analysis operations
- [ ] Settings panel for AI configuration
- [ ] Error handling and retry logic

---

### 📋 Sprint 7: Performance & Polish (PLANNED)
**Duration**: Week 7  
**Goal**: Optimization and user experience

#### Planned Tasks:
- [ ] Performance benchmarking
- [ ] Memory usage optimization
- [ ] UI polish and loading indicators
- [ ] Keyboard shortcuts
- [ ] Settings persistence

---

### 📋 Sprint 8: Advanced Features (PLANNED)
**Duration**: Week 8  
**Goal**: Nice-to-have features

#### Planned Tasks:
- [ ] Export/import catalogs
- [ ] Saved searches
- [ ] Advanced filters
- [ ] Catalog statistics
- [ ] Missing file detection

## Current Sprint Details

### Sprint 2: Basic GUI Framework

#### Architecture Decisions:
- **GUI Framework**: Starting with tkinter for simplicity, may upgrade to PyQt later
- **Layout**: Main window with menu bar, toolbar, and split panes
- **State Management**: Simple class-based state management

#### Key Components to Build:
1. **MainWindow** class - Primary application window
2. **CatalogManager** - Handle catalog creation/opening
3. **FileListView** - Display cataloged files in table format
4. **ProgressDialog** - Show scanning progress

#### File Structure for Sprint 2:
```
src/
├── media_catalog_gui.py     # Main GUI application
├── dialogs/
│   ├── catalog_dialog.py    # New/Open catalog dialogs
│   └── progress_dialog.py   # Progress tracking
└── widgets/
    └── file_list_widget.py  # File list table
```

#### Getting Started with Sprint 2:
1. Study existing GUI code in stills-exporter (`src/stills_exporter_gui.py`)
2. Create basic window structure
3. Integrate with existing database layer
4. Test with sample data

## Sprint Assignment

### For New Contributors:
- **Sprint 1**: Review and test existing foundation
- **Sprint 2**: Pick up GUI development tasks
- **Future Sprints**: Based on interests and skills

### Current Priorities:
1. Complete Sprint 2 GUI framework
2. Ensure solid integration with Sprint 1 foundation
3. Plan Sprint 3 search implementation

## Testing Strategy

### Per-Sprint Testing:
- **Sprint 1**: `test_catalog_foundation.py`
- **Sprint 2**: GUI integration tests
- **Sprint 3**: Search performance tests
- **Sprint 7**: Comprehensive benchmark suite

### Continuous Testing:
- Run foundation tests before each commit
- Manual GUI testing for user experience
- Performance monitoring for large catalogs
