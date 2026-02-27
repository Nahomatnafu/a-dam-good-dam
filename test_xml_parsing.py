#!/usr/bin/env python3
"""
Test the updated XML parsing for AI tags
"""

import xml.etree.ElementTree as ET
from pathlib import Path

def test_xml_parsing():
    """Test parsing the new XML format"""
    
    # Test with your actual XML file (FridayTest_2 has high-confidence building matches)
    xml_path = Path(r"C:\Users\15073\Videos\NeoFinder_Test\FridayTest\FridayTest_2_Stills\FridayTest_2_tags.xml")
    
    if not xml_path.exists():
        print(f"❌ XML file not found: {xml_path}")
        return
    
    print(f"✅ Found XML file: {xml_path.name}")
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        print(f"📄 Root element: {root.tag}")
        
        # Parse final tags (show with confidence for debugging)
        final_tags = root.find('final_tags')
        if final_tags is not None:
            print(f"\n🏷️ Final Tags ({len(final_tags.findall('tag'))} tags):")
            all_tags = []
            for tag in final_tags.findall('tag'):
                if tag.text:
                    confidence = tag.get('confidence', '0')
                    tag_with_confidence = f"{tag.text.strip()} ({float(confidence):.2f})"
                    all_tags.append(tag.text.strip())  # Add clean tag to list
                    print(f"   • {tag_with_confidence}")

        # Parse gallery matches with filtering
        gallery_matches = root.find('gallery_matches')
        if gallery_matches is not None:
            matches = gallery_matches.findall('match')
            print(f"\n🏛️ Gallery Matches ({len(matches)} total matches):")
            building_confidence_threshold = 0.65
            seen_buildings = set()

            for match in matches:
                category = match.get('category', '')
                confidence = float(match.get('confidence', '0'))
                status = "✅ INCLUDED" if confidence >= building_confidence_threshold else "❌ FILTERED OUT"
                print(f"   • {category} ({confidence:.2f}) - {status}")

                if category and confidence >= building_confidence_threshold:
                    if category not in seen_buildings:
                        all_tags.append(f"🏛️ {category}")
                        seen_buildings.add(category)
        
        print(f"\n📊 Total AI tags found: {len(all_tags)}")
        return all_tags
        
    except Exception as e:
        print(f"❌ Error parsing XML: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_gui_xml_method():
    """Test the GUI's get_ai_tags_from_xml method"""
    
    # Import the GUI method
    import sys
    sys.path.append('src')
    from media_catalog_gui import MediaCatalogGUI
    
    # Create a dummy GUI instance just to test the method
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    gui = MediaCatalogGUI(root)
    
    # Test with your video path (FridayTest_2 has high-confidence building matches)
    video_path = Path(r"C:\Users\15073\Videos\NeoFinder_Test\FridayTest\FridayTest_2.mov")
    
    print(f"\n🧪 Testing GUI method with: {video_path.name}")
    
    ai_tags = gui.get_ai_tags_from_xml(video_path)
    
    if ai_tags:
        print(f"✅ GUI method found {len(ai_tags)} AI tags:")
        for tag in ai_tags[:10]:  # Show first 10
            print(f"   • {tag}")
        if len(ai_tags) > 10:
            print(f"   ... and {len(ai_tags) - 10} more")
    else:
        print("❌ GUI method found no AI tags")
    
    root.destroy()
    return ai_tags

if __name__ == "__main__":
    print("🧪 Testing XML Parsing for AI Tags")
    print("=" * 50)
    
    # Test direct XML parsing
    direct_tags = test_xml_parsing()
    
    # Test GUI method
    gui_tags = test_gui_xml_method()
    
    print("\n📊 Summary:")
    print(f"Direct parsing: {len(direct_tags) if direct_tags else 0} tags")
    print(f"GUI method: {len(gui_tags) if gui_tags else 0} tags")
    
    if direct_tags and gui_tags:
        print("✅ Both methods working!")
    elif direct_tags:
        print("⚠️ Direct parsing works, but GUI method needs fixing")
    else:
        print("❌ XML parsing not working")
