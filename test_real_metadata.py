#!/usr/bin/env python3
from pathlib import Path
import subprocess

def check_real_metadata(video_path):
    """Check actual embedded metadata in video file"""
    try:
        cmd = ['exiftool', '-Keywords', '-Subject', '-Description', '-Comment', '-UserComment', str(video_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return "Error reading metadata"
    except Exception as e:
        return f"Error: {e}"

# Test your basketball videos
test_videos = [
    "C:/Users/15073/Videos/NeoFinder_Test/Test2/Basketball1.mov",
    "C:/Users/15073/Videos/NeoFinder_Test/Test2/Basketball2.mov", 
    "C:/Users/15073/Videos/NeoFinder_Test/Test2/Basketball3.mov"
]

for video_path in test_videos:
    video_file = Path(video_path)
    if video_file.exists():
        print(f"\n📹 {video_file.name}")
        print("-" * 40)
        metadata = check_real_metadata(video_file)
        print(metadata if metadata else "❌ No embedded metadata found")