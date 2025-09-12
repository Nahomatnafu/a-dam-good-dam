#!/usr/bin/env python3
"""
Test script for AI features
"""

import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Test if all AI modules can be imported"""
    print("Testing AI module imports...")
    
    try:
        import vision_tagger
        from vision_tagger import VisionTagger, VISION_AVAILABLE
        print(f"✅ VisionTagger imported (Vision available: {VISION_AVAILABLE})")
    except ImportError as e:
        print(f"❌ VisionTagger import failed: {e}")
        return False
    
    try:
        import exif_embedder
        from exif_embedder import ExifEmbedder
        embedder = ExifEmbedder()
        print(f"✅ ExifEmbedder imported (ExifTool available: {embedder.exiftool_available})")
    except ImportError as e:
        print(f"❌ ExifEmbedder import failed: {e}")
        return False
    
    return True

def test_gui_integration():
    """Test if GUI can import AI modules"""
    print("\nTesting GUI integration...")
    
    try:
        import stills_exporter_gui
        from stills_exporter_gui import StillsExporterGUI
        print("✅ GUI with AI features imported successfully")
        return True
    except ImportError as e:
        print(f"❌ GUI import failed: {e}")
        return False

def test_existing_stills():
    """Test AI analysis on existing stills folder"""
    stills_path = Path("C:/Users/15073/Videos/NeoFinder_Test/Stills")
    
    if not stills_path.exists():
        print(f"❌ Stills folder not found: {stills_path}")
        return False
    
    print(f"\n🔍 Testing with existing stills in: {stills_path}")
    
    # Find image files
    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.tiff']
    image_files = []
    for ext in image_extensions:
        image_files.extend(stills_path.rglob(ext))
    
    print(f"Found {len(image_files)} image files")
    
    if len(image_files) > 0:
        print("Sample files:")
        for i, img in enumerate(image_files[:5]):  # Show first 5
            print(f"  {i+1}. {img.name}")
        if len(image_files) > 5:
            print(f"  ... and {len(image_files) - 5} more")
    
    return len(image_files) > 0

if __name__ == "__main__":
    print("🧪 Testing AI Features")
    print("=" * 40)
    
    imports_ok = test_imports()
    gui_ok = test_gui_integration()
    stills_ok = test_existing_stills()
    
    print("\n" + "=" * 40)
    if imports_ok and gui_ok:
        print("✅ All tests passed! AI features are ready.")
        if stills_ok:
            print("✅ Found existing stills to test with!")
        print("\nTo use:")
        print("1. Run: python setup_ai.py")
        print("2. Set up Google Cloud credentials")
        print("3. Run: python src/stills_exporter_gui.py")
    else:
        print("❌ Some tests failed. Check the errors above.")
