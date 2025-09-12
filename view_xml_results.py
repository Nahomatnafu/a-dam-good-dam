#!/usr/bin/env python3
"""
View the generated XML analysis results
"""

import xml.etree.ElementTree as ET
from pathlib import Path

def view_xml_file(xml_path):
    """Display contents of an XML analysis file"""
    print(f"\n📄 {xml_path.name}")
    print("=" * 50)
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Show summary
        source_folder = root.find('source_folder').text if root.find('source_folder') is not None else "Unknown"
        total_frames = root.find('total_frames').text if root.find('total_frames') is not None else "0"
        
        print(f"Source Folder: {source_folder}")
        print(f"Total Frames: {total_frames}")
        
        # Show first few frames as examples
        frames = root.find('frames')
        if frames is not None:
            frame_list = frames.findall('frame')
            print(f"\nShowing first 3 frames (of {len(frame_list)}):")
            
            for i, frame in enumerate(frame_list[:3]):
                frame_id = frame.get('id', 'Unknown')
                image_name = frame.get('image', 'Unknown')
                print(f"\n  Frame {frame_id}: {image_name}")
                
                # Show labels
                labels_elem = frame.find('labels')
                if labels_elem is not None:
                    labels = labels_elem.findall('label')
                    print("    Labels:")
                    for label in labels:
                        score = label.get('score', '0.00')
                        text = label.text or 'Unknown'
                        print(f"      - {text} (confidence: {score})")
                
                # Show objects
                objects_elem = frame.find('objects')
                if objects_elem is not None:
                    objects = objects_elem.findall('object')
                    print("    Objects:")
                    for obj in objects:
                        name = obj.get('name', 'Unknown')
                        score = obj.get('score', '0.00')
                        bounds = obj.get('bounds', '0,0,0,0')
                        print(f"      - {name} (confidence: {score}, bounds: {bounds})")
                
                # Show text
                text_elem = frame.find('text')
                if text_elem is not None and text_elem.text:
                    print(f"    Text: {text_elem.text}")
        
    except Exception as e:
        print(f"❌ Error reading XML file: {e}")

def main():
    """View all XML analysis files"""
    stills_path = Path("C:/Users/15073/Videos/NeoFinder_Test/Stills")
    
    print("🔍 XML Analysis Results Viewer")
    print("=" * 60)
    
    # Find XML files
    xml_files = list(stills_path.glob("*_ai_tags.xml"))
    
    if not xml_files:
        print("❌ No XML analysis files found")
        print(f"Looking in: {stills_path}")
        return
    
    print(f"Found {len(xml_files)} XML analysis files:")
    for xml_file in xml_files:
        print(f"  - {xml_file.name}")
    
    # Display each file
    for xml_file in sorted(xml_files):
        view_xml_file(xml_file)
    
    print(f"\n📁 Full files located at: {stills_path}")
    print("💡 You can open these XML files in any text editor to see the complete analysis")

if __name__ == "__main__":
    main()