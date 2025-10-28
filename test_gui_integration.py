#!/usr/bin/env python3
"""
Test script to verify GUI integration with gallery system
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        from src.ai.gallery_vision_tagger import GalleryVisionTagger
        print("✅ GalleryVisionTagger imported successfully")
    except ImportError as e:
        print(f"❌ GalleryVisionTagger import failed: {e}")
        return False
    
    try:
        from src.ai.gallery_manager import GalleryManager
        print("✅ GalleryManager imported successfully")
    except ImportError as e:
        print(f"❌ GalleryManager import failed: {e}")
        return False
    
    try:
        from src.pipeline.enhanced_video_processor import EnhancedVideoProcessor
        print("✅ EnhancedVideoProcessor imported successfully")
    except ImportError as e:
        print(f"❌ EnhancedVideoProcessor import failed: {e}")
        return False
    
    return True

def test_gallery_system():
    """Test that gallery system is functional"""
    print("\nTesting gallery system...")
    
    try:
        from src.ai.gallery_manager import GalleryManager
        
        gallery_manager = GalleryManager()
        stats = gallery_manager.get_statistics()
        
        print(f"✅ Gallery system functional:")
        print(f"  Total items: {stats.get('total_items', 0)}")
        print(f"  Categories: {stats.get('categories', 0)}")
        print(f"  Cached frames: {stats.get('cached_frames', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Gallery system test failed: {e}")
        return False

def test_enhanced_processor():
    """Test that enhanced processor can be initialized"""
    print("\nTesting enhanced processor...")
    
    try:
        from src.pipeline.enhanced_video_processor import EnhancedVideoProcessor

        # Test with dummy API key
        processor = EnhancedVideoProcessor(api_key="test_key")
        print("✅ EnhancedVideoProcessor initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced processor test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("GUI Integration Test")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Gallery System Test", test_gallery_system),
        ("Enhanced Processor Test", test_enhanced_processor)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! GUI integration is ready.")
        print("\nNext steps:")
        print("1. Run: python src/stills_exporter_gui.py")
        print("2. Enable 'AI Tagging' checkbox")
        print("3. Enable 'Use Gallery Recognition' checkbox")
        print("4. Process a video to test the new system")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
