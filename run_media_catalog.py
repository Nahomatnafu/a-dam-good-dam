#!/usr/bin/env python3
"""
Launcher for Media Catalog with integrated AI Stills Exporter
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import and run the GUI
from media_catalog_gui import main

if __name__ == "__main__":
    print("=" * 60)
    print("Media Catalog with AI Tagging")
    print("=" * 60)
    print("\nFeatures:")
    print("  ✓ Catalog and organize video files")
    print("  ✓ Search by keywords and tags")
    print("  ✓ Preview videos and thumbnails")
    print("  ✓ Integrated AI Stills Exporter")
    print("  ✓ AI tagging with President Inch recognition")
    print("\nStarting GUI...")
    print("=" * 60)
    
    main()

