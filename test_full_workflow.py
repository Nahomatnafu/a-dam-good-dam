#!/usr/bin/env python3
"""
Test the complete workflow: Extract stills -> AI analysis -> View results
"""

import sys
import subprocess
from pathlib import Path
import time

def run_command(cmd, description):
    """Run a command and show the result"""
    print(f"\n🔄 {description}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"Errors: {result.stderr}")
            
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
        return False
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

def main():
    print("🧪 Testing Full Stills Exporter Workflow")
    print("=" * 60)
    
    # Step 1: Launch GUI (user will need to configure and run manually)
    print("\n📋 STEP 1: Launch GUI Application")
    print("Run this command to start the GUI:")
    print("python run_gui.py")
    print("\nIn the GUI:")
    print("1. Set Source Folder to your video folder")
    print("2. Set Output Folder (e.g., C:/Users/15073/Videos/NeoFinder_Test/NewStills)")
    print("3. Enable 'AI Tagging' checkbox")
    print("4. Set frames per clip (e.g., 5)")
    print("5. Click 'Start Export'")
    
    input("\nPress Enter after you've run the export in the GUI...")
    
    # Step 2: Check for new XML files
    print("\n📋 STEP 2: Check for Generated Files")
    output_path = input("Enter the output folder path you used: ").strip()
    
    if not output_path:
        output_path = "C:/Users/15073/Videos/NeoFinder_Test/NewStills"
    
    output_dir = Path(output_path)
    if not output_dir.exists():
        print(f"❌ Output directory not found: {output_dir}")
        return
    
    # Find XML files
    xml_files = list(output_dir.rglob("*_tags.xml"))
    image_files = list(output_dir.rglob("*.png")) + list(output_dir.rglob("*.jpg"))
    
    print(f"Found {len(image_files)} image files")
    print(f"Found {len(xml_files)} XML files")
    
    if xml_files:
        print("\nXML files found:")
        for xml_file in xml_files:
            print(f"  - {xml_file}")
    
    # Step 3: View results
    if xml_files:
        print("\n📋 STEP 3: View Analysis Results")
        
        # Create a custom viewer for the new files
        viewer_code = f'''
import xml.etree.ElementTree as ET
from pathlib import Path

def view_xml_file(xml_path):
    print(f"\\n📄 {{xml_path.name}}")
    print("=" * 50)
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        source_folder = root.find('source_folder')
        total_frames = root.find('total_frames')
        
        print(f"Source: {{source_folder.text if source_folder is not None else 'Unknown'}}")
        print(f"Frames: {{total_frames.text if total_frames is not None else '0'}}")
        
        frames = root.find('frames')
        if frames is not None:
            frame_list = frames.findall('frame')
            print(f"\\nFirst 2 frames (of {{len(frame_list)}}):")
            
            for frame in frame_list[:2]:
                frame_id = frame.get('id', 'Unknown')
                image_name = frame.get('image', 'Unknown')
                print(f"\\n  Frame {{frame_id}}: {{image_name}}")
                
                labels_elem = frame.find('labels')
                if labels_elem is not None:
                    labels = labels_elem.findall('label')
                    if labels:
                        print("    Labels:")
                        for label in labels[:3]:
                            score = label.get('score', '0.00')
                            text = label.text or 'Unknown'
                            print(f"      - {{text}} ({{score}})")
                
                objects_elem = frame.find('objects')
                if objects_elem is not None:
                    objects = objects_elem.findall('object')
                    if objects:
                        print("    Objects:")
                        for obj in objects[:2]:
                            name = obj.get('name', 'Unknown')
                            score = obj.get('score', '0.00')
                            print(f"      - {{name}} ({{score}})")
    
    except Exception as e:
        print(f"❌ Error: {{e}}")

# View all XML files
xml_files = list(Path("{output_dir}").rglob("*_tags.xml"))
for xml_file in sorted(xml_files):
    view_xml_file(xml_file)
'''
        
        # Write and run the viewer
        viewer_path = Path("temp_viewer.py")
        with open(viewer_path, 'w') as f:
            f.write(viewer_code)
        
        success = run_command([sys.executable, str(viewer_path)], "Viewing XML Results")
        
        # Cleanup
        if viewer_path.exists():
            viewer_path.unlink()
        
        if success:
            print("\n✅ Workflow test completed successfully!")
        else:
            print("\n⚠️ Some issues occurred during viewing")
    else:
        print("\n❌ No XML files found. Make sure AI tagging was enabled in the GUI.")
    
    print(f"\n📁 Check your output folder: {output_dir}")

if __name__ == "__main__":
    main()