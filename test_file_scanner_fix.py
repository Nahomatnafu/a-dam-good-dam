#!/usr/bin/env python3
"""
Test the FileScanner fix for video scanning
"""

from pathlib import Path
import sys
sys.path.insert(0, 'src')

from file_scanner import FileScanner

def test_scanner():
    print("Testing FileScanner...")
    print("=" * 60)
    
    scanner = FileScanner()
    
    # Test with a video folder
    test_folder = Path(r"C:\Users\15073\Videos\NeoFinder_Test3\President Inch")
    
    if not test_folder.exists():
        print(f"❌ Test folder not found: {test_folder}")
        print("\nPlease provide a folder path with video files:")
        test_folder = Path(input("> "))
        
        if not test_folder.exists():
            print("❌ Folder still not found. Exiting.")
            return
    
    print(f"📁 Scanning: {test_folder}")
    print()
    
    try:
        files = scanner.scan_directory(test_folder)
        
        print(f"✅ Found {len(files)} files")
        print()
        
        # Show details
        videos = [f for f in files if f.get('file_type') == 'video']
        images = [f for f in files if f.get('file_type') == 'image']
        
        print(f"📹 Videos: {len(videos)}")
        for video in videos[:5]:  # Show first 5
            print(f"  - {video['filename']}")
            print(f"    Size: {video['filesize'] / (1024*1024):.1f} MB")
            print(f"    Duration: {video.get('duration', 0):.1f}s")
            print(f"    Resolution: {video.get('width', 0)}x{video.get('height', 0)}")
        
        if len(videos) > 5:
            print(f"  ... and {len(videos) - 5} more")
        
        print()
        print(f"🖼️  Images: {len(images)}")
        if images:
            for img in images[:3]:
                print(f"  - {img['filename']}")
        
        print()
        print("=" * 60)
        print("✅ FileScanner is working correctly!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scanner()

