#!/usr/bin/env python3
"""
Test AI analysis on existing stills
"""

import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def mock_analyze_image(image_path):
    """Mock AI analysis for testing"""
    # Generate mock tags based on filename patterns
    filename = image_path.name.lower()
    
    mock_labels = []
    mock_objects = []
    mock_text = []
    
    # Add some realistic mock data
    if 'clip1' in filename:
        mock_labels = [
            {'description': 'person', 'score': 0.95},
            {'description': 'indoor', 'score': 0.87},
            {'description': 'room', 'score': 0.82}
        ]
        mock_objects = [
            {'name': 'Person', 'score': 0.91, 'bounds': [100, 150, 200, 400]},
            {'name': 'Chair', 'score': 0.76, 'bounds': [50, 300, 150, 450]}
        ]
    else:
        mock_labels = [
            {'description': 'outdoor', 'score': 0.92},
            {'description': 'landscape', 'score': 0.88},
            {'description': 'nature', 'score': 0.85}
        ]
        mock_objects = [
            {'name': 'Tree', 'score': 0.89, 'bounds': [200, 100, 350, 400]},
            {'name': 'Building', 'score': 0.73, 'bounds': [400, 200, 600, 350]}
        ]
    
    return {
        'image_path': str(image_path),
        'labels': mock_labels,
        'objects': mock_objects,
        'text': mock_text,
        'safe_search': {
            'adult': 'VERY_UNLIKELY',
            'spoof': 'UNLIKELY',
            'medical': 'UNLIKELY',
            'violence': 'UNLIKELY',
            'racy': 'UNLIKELY'
        }
    }

def create_xml_tags(analysis_results, xml_path):
    """Create XML tags file from analysis results"""
    xml_content = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_content.append('<video_analysis>')
    xml_content.append(f'  <source_folder>{xml_path.parent.name}</source_folder>')
    xml_content.append(f'  <total_frames>{len(analysis_results)}</total_frames>')
    xml_content.append('  <frames>')
    
    for i, result in enumerate(analysis_results):
        image_name = Path(result['image_path']).name
        xml_content.append(f'    <frame id="{i+1}" image="{image_name}">')
        
        # Labels
        if result['labels']:
            xml_content.append('      <labels>')
            for label in result['labels']:
                xml_content.append(f'        <label score="{label["score"]:.2f}">{label["description"]}</label>')
            xml_content.append('      </labels>')
        
        # Objects
        if result['objects']:
            xml_content.append('      <objects>')
            for obj in result['objects']:
                bounds = obj['bounds']
                xml_content.append(f'        <object name="{obj["name"]}" score="{obj["score"]:.2f}" bounds="{bounds[0]},{bounds[1]},{bounds[2]},{bounds[3]}"/>')
            xml_content.append('      </objects>')
        
        # Text (if any)
        if result['text']:
            xml_content.append('      <text>')
            for text in result['text']:
                xml_content.append(f'        <detected>{text}</detected>')
            xml_content.append('      </text>')
        
        xml_content.append('    </frame>')
    
    xml_content.append('  </frames>')
    xml_content.append('</video_analysis>')
    
    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(xml_content))

def test_existing_stills():
    """Test AI analysis on existing stills"""
    stills_path = Path("C:/Users/15073/Videos/NeoFinder_Test/Stills")
    
    if not stills_path.exists():
        print(f"❌ Stills folder not found: {stills_path}")
        return False
    
    print(f"🔍 Analyzing existing stills in: {stills_path}")
    
    # Find image files
    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.tiff']
    image_files = []
    for ext in image_extensions:
        image_files.extend(stills_path.rglob(ext))
    
    if not image_files:
        print("❌ No image files found")
        return False
    
    print(f"Found {len(image_files)} image files")
    
    # Group by clip (assuming naming pattern like Clip1_001.png)
    clips = {}
    for img in image_files:
        # Extract clip name (everything before the last underscore)
        parts = img.stem.split('_')
        if len(parts) >= 2:
            clip_name = '_'.join(parts[:-1])
        else:
            clip_name = img.stem
        
        if clip_name not in clips:
            clips[clip_name] = []
        clips[clip_name].append(img)
    
    print(f"Found {len(clips)} clips: {list(clips.keys())}")
    
    # Analyze each clip
    for clip_name, clip_images in clips.items():
        print(f"\n📸 Analyzing {clip_name} ({len(clip_images)} images)...")
        
        # Mock analyze each image
        analysis_results = []
        for img_path in sorted(clip_images):
            print(f"  Analyzing {img_path.name}...")
            result = mock_analyze_image(img_path)
            analysis_results.append(result)
        
        # Create XML file
        xml_path = stills_path / f"{clip_name}_ai_tags.xml"
        create_xml_tags(analysis_results, xml_path)
        print(f"  ✅ Created: {xml_path.name}")
        
        # Show sample results
        if analysis_results:
            sample = analysis_results[0]
            labels = [label['description'] for label in sample['labels'][:3]]
            print(f"  Sample tags: {', '.join(labels)}")
    
    print(f"\n🎉 Analysis complete! Check the XML files in {stills_path}")
    return True

if __name__ == "__main__":
    print("🧪 Testing AI Analysis on Existing Stills")
    print("=" * 50)
    
    success = test_existing_stills()
    
    if success:
        print("\n✅ Mock AI analysis completed successfully!")
        print("📁 Check your Stills folder for *_ai_tags.xml files")
        print("\n🚀 Next steps:")
        print("1. Review the generated XML files")
        print("2. Install Google Cloud Vision for real AI analysis")
        print("3. Test with the main GUI application")
    else:
        print("\n❌ Test failed")