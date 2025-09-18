#!/usr/bin/env python3
import subprocess
from pathlib import Path

def embed_test_keywords(video_path, keywords):
    """Embed specific keywords into video file"""
    video_file = Path(video_path)
    
    if not video_file.exists():
        print(f"❌ Video not found: {video_path}")
        return False
    
    print(f"📹 Embedding keywords into: {video_file.name}")
    print(f"🏷️ Keywords: {', '.join(keywords)}")
    
    # Build ExifTool command
    cmd = ['exiftool', '-overwrite_original']
    
    # Clear existing keywords first
    cmd.extend(['-Keywords=', '-Subject=', '-HierarchicalSubject='])
    
    # Add each keyword
    for keyword in keywords:
        cmd.extend([f'-Keywords+={keyword}'])
        cmd.extend([f'-Subject+={keyword}'])
        cmd.extend([f'-HierarchicalSubject+={keyword}'])
    
    # Add description
    cmd.extend([f'-Description=Test video with embedded keywords'])
    cmd.extend([f'-UserComment=MANUALLY_TAGGED'])
    
    cmd.append(str(video_file))
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Keywords embedded successfully!")
            return True
        else:
            print(f"❌ Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def verify_embedded_keywords(video_path):
    """Verify what keywords were actually embedded"""
    try:
        cmd = ['exiftool', '-Keywords', '-Subject', '-Description', '-UserComment', str(video_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("\n📋 Verification - Embedded metadata:")
            print(result.stdout)
        else:
            print("❌ Could not verify metadata")
    except Exception as e:
        print(f"❌ Verification error: {e}")

# Test video and keywords
video_path = "C:/Users/15073/Videos/NeoFinder_Test2/Basketball"
test_keywords = ["basketball", "women", "celebration"]

# Embed the keywords
success = embed_test_keywords(video_path, test_keywords)

if success:
    # Verify what was embedded
    verify_embedded_keywords(video_path)
    
    print("\n🎯 Next steps:")
    print("1. Test in NeoFinder - import this video and check if keywords show")
    print("2. Test in our app - add this folder to catalog and check metadata panel")
else:
    print("❌ Failed to embed keywords")