#!/usr/bin/env python3
"""
Test XML tag detection for videos
"""

from pathlib import Path
import xml.etree.ElementTree as ET

def get_ai_tags_from_xml(video_path: Path) -> list:
    """Check for AI-generated tags XML file and extract tags"""
    try:
        # Look for XML file in the same directory or in a _stills folder
        video_stem = video_path.stem
        
        # Also try with underscores instead of spaces (common in stills exporter)
        video_stem_underscore = video_stem.replace(" ", "_").replace("'", "")
        
        possible_xml_paths = [
            # Original name
            video_path.parent / f"{video_stem}_tags.xml",
            video_path.parent / f"{video_stem}_stills" / f"{video_stem}_tags.xml",
            video_path.parent / f"{video_stem}_Stills" / f"{video_stem}_tags.xml",
            # With underscores
            video_path.parent / f"{video_stem_underscore}_tags.xml",
            video_path.parent / f"{video_stem_underscore}_stills" / f"{video_stem_underscore}_tags.xml",
            video_path.parent / f"{video_stem_underscore}_Stills" / f"{video_stem_underscore}_tags.xml",
        ]
        
        print(f"\n📹 Video: {video_path.name}")
        print(f"   Stem: {video_stem}")
        print(f"   Stem (underscore): {video_stem_underscore}")
        print(f"\n   Checking paths:")
        
        for xml_path in possible_xml_paths:
            exists = "✅" if xml_path.exists() else "❌"
            print(f"   {exists} {xml_path}")
            
            if xml_path.exists():
                tree = ET.parse(xml_path)
                root = tree.getroot()
                
                # Collect all unique tags from all frames
                all_tags = set()
                for frame in root.findall('Frame'):
                    labels = frame.find('Labels')
                    if labels is not None:
                        for label in labels.findall('Label'):
                            if label.text:
                                all_tags.add(label.text.strip())
                
                print(f"\n   🎯 Found {len(all_tags)} unique tags:")
                for tag in sorted(list(all_tags))[:10]:
                    print(f"      - {tag}")
                if len(all_tags) > 10:
                    print(f"      ... and {len(all_tags) - 10} more")
                
                return sorted(list(all_tags))
        
        print(f"\n   ⚠️  No XML file found")
        return []
    except Exception as e:
        print(f"   ❌ Error reading AI tags: {e}")
        return []

def test_videos():
    print("=" * 70)
    print("Testing XML Tag Detection")
    print("=" * 70)
    
    video_folder = Path(r"C:\Users\15073\Videos\NeoFinder_Test3\President Inch")
    
    if not video_folder.exists():
        print(f"❌ Folder not found: {video_folder}")
        return
    
    # Find all video files
    video_files = list(video_folder.glob("*.mp4")) + list(video_folder.glob("*.mov"))
    
    print(f"\nFound {len(video_files)} video files\n")
    
    for video_path in video_files:
        tags = get_ai_tags_from_xml(video_path)
        print()
    
    print("=" * 70)
    print("Test Complete")
    print("=" * 70)

if __name__ == "__main__":
    test_videos()

