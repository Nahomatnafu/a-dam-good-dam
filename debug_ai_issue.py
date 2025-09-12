#!/usr/bin/env python3
"""
Debug why AI analysis isn't working in GUI
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_ai_imports():
    """Test AI module imports"""
    print("🔍 Testing AI imports...")
    
    try:
        from vision_tagger import VisionTagger, VISION_AVAILABLE
        print(f"✅ VisionTagger imported, VISION_AVAILABLE: {VISION_AVAILABLE}")
    except ImportError as e:
        print(f"❌ VisionTagger import failed: {e}")
    
    try:
        from exif_embedder import ExifEmbedder
        embedder = ExifEmbedder()
        print(f"✅ ExifEmbedder imported, exiftool_available: {embedder.exiftool_available}")
    except ImportError as e:
        print(f"❌ ExifEmbedder import failed: {e}")

def test_mock_analysis():
    """Test mock analysis on a sample image"""
    print("\n🧪 Testing mock analysis...")
    
    # Create a dummy image path for testing
    test_path = Path("test_image.png")
    
    try:
        from vision_tagger import VisionTagger
        tagger = VisionTagger()
        
        # This should work even without real credentials
        print("Mock analysis test would work here")
        
    except Exception as e:
        print(f"❌ Mock analysis failed: {e}")

if __name__ == "__main__":
    print("🔧 Debugging AI Analysis Issues")
    print("=" * 50)
    
    test_ai_imports()
    test_mock_analysis()
    
    print("\n💡 Solutions:")
    print("1. Install Google Vision: pip install google-cloud-vision")
    print("2. Or fix mock analysis in vision_tagger.py")
    print("3. Check GUI AI processing logic")