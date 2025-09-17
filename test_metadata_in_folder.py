#!/usr/bin/env python3
from pathlib import Path
import subprocess

def check_video_metadata(video_path):
    """Check if video has embedded keywords/metadata"""
    try:
        cmd = ['exiftool', '-Keywords', '-Subject', '-Description', '-Comment', '-UserComment', str(video_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return "Error reading metadata"
    except Exception as e:
        return f"Error: {e}"

def main():
    test_folder = Path("C:/Users/15073/Videos/NeoFinder_Test/Test2")
    
    if not test_folder.exists():
        print(f"❌ Folder not found: {test_folder}")
        return
    
    # Find video files
    video_extensions = ['.mp4', '.mov', '.mxf', '.mkv', '.avi', '.mts', '.m2ts', '.wmv']
    video_files = []
    
    for ext in video_extensions:
        video_files.extend(test_folder.glob(f"*{ext}"))
        video_files.extend(test_folder.glob(f"*{ext.upper()}"))
    
    if not video_files:
        print(f"❌ No video files found in {test_folder}")
        return
    
    print(f"🔍 Found {len(video_files)} video files in {test_folder}")
    print("=" * 60)
    
    for video_file in sorted(video_files):
        print(f"\n📹 {video_file.name}")
        print("-" * 40)
        
        metadata = check_video_metadata(video_file)
        if metadata and metadata != "Error reading metadata":
            print(metadata)
        else:
            print("❌ No metadata found or error reading file")

if __name__ == "__main__":
    main()