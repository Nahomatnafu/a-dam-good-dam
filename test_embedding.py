#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.append('src')

from exif_embedder import ExifEmbedder

# Test the embedding
xml_path = Path("C:/Users/15073/Videos/NeoFinder_Test/Stills/Clip1_Proxy_Stills/Clip1_Proxy_tags.xml")
video_path = Path("C:/Users/15073/Videos/NeoFinder_Test/Proxies/Clip1_Proxy.mov")

print(f"XML exists: {xml_path.exists()}")
print(f"Video exists: {video_path.exists()}")

if xml_path.exists() and video_path.exists():
    embedder = ExifEmbedder()
    print(f"ExifTool available: {embedder.exiftool_available}")
    
    # Parse XML
    metadata = embedder.parse_xml_tags(xml_path)
    print(f"Parsed metadata: {metadata}")
    
    # Embed metadata
    success = embedder.embed_metadata(video_path, metadata)
    print(f"Embedding success: {success}")