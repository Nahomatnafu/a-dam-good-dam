#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.append('src')

from exif_embedder import ExifEmbedder
import subprocess

# Test clips
clips = [
    ("Clip1_Proxy", "C:/Users/15073/Videos/NeoFinder_Test/Stills/Clip1_Proxy_Stills/Clip1_Proxy_tags.xml"),
    ("Clip2_Proxy", "C:/Users/15073/Videos/NeoFinder_Test/Stills/Clip2_Proxy_Stills/Clip2_Proxy_tags.xml"),
    ("Clip3_Proxy", "C:/Users/15073/Videos/NeoFinder_Test/Stills/Clip3_Proxy_Stills/Clip3_Proxy_tags.xml")
]

embedder = ExifEmbedder()
print(f"ExifTool available: {embedder.exiftool_available}")

for clip_name, xml_path_str in clips:
    xml_path = Path(xml_path_str)
    video_path = Path(f"C:/Users/15073/Videos/NeoFinder_Test/Proxies/{clip_name}.mov")
    
    if xml_path.exists() and video_path.exists():
        print(f"\n--- Clearing and Re-embedding {clip_name} ---")
        
        # Step 1: Clear all existing metadata
        print("Clearing existing metadata...")
        clear_cmd = [
            'exiftool', '-overwrite_original',
            '-Keywords=', '-Subject=', '-HierarchicalSubject=',
            '-Description=', '-Comment=', '-UserComment=',
            str(video_path)
        ]
        subprocess.run(clear_cmd, capture_output=True)
        
        # Step 2: Re-embed with new array approach
        metadata = embedder.parse_xml_tags(xml_path)
        print(f"Keywords to embed: {metadata['keywords'][:5]}")
        
        success = embedder.embed_metadata(video_path, metadata)
        print(f"Embedding success: {success}")
        
        # Step 3: Verify what was written
        verify_cmd = ['exiftool', '-Keywords', '-Subject', str(video_path)]
        result = subprocess.run(verify_cmd, capture_output=True, text=True)
        print("Verification:")
        print(result.stdout)