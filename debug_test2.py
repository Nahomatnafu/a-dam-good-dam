#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.append('src')

from file_scanner import FileScanner

def debug_test2_folder():
    test_path = Path("C:/Users/15073/Videos/NeoFinder_Test2")
    
    if not test_path.exists():
        print(f"❌ Folder doesn't exist: {test_path}")
        return
    
    print(f"🔍 Scanning: {test_path}")
    
    # List all files
    all_files = list(test_path.rglob("*"))
    print(f"Total files found: {len(all_files)}")
    
    for file in all_files:
        if file.is_file():
            print(f"  📄 {file}")
    
    # Test scanner
    scanner = FileScanner()
    media_files = scanner.scan_directory(test_path)
    print(f"\n📹 Media files found: {len(media_files)}")
    
    for media in media_files:
        print(f"  🎬 {media['filename']} ({media['file_type']})")

if __name__ == "__main__":
    debug_test2_folder()