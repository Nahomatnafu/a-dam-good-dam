#!/usr/bin/env python3
"""
Build gallery embeddings and prepare the recognition system
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai.gallery_manager import GalleryManager
from training_manager import TrainingManager

def main():
    print("=" * 60)
    print("Gallery Embeddings Builder")
    print("=" * 60)
    
    # Initialize managers
    gallery_manager = GalleryManager()
    training_manager = TrainingManager()
    
    # Check API key
    api_key = training_manager.get_api_key()
    if not api_key:
        print("\n❌ No API key configured in config/ai_config.json")
        print("Please add your Google API key first:")
        print("1. Copy config/ai_config.json.example to config/ai_config.json")
        print("2. Add your Google API key")
        return
    
    print(f"\n✓ API key configured")
    
    # Scan gallery directory for new items
    print("\n1. Scanning gallery directory...")
    added_count = gallery_manager.scan_gallery_directory()
    print(f"✓ Added {added_count} new gallery items")
    
    # Get gallery statistics
    stats = gallery_manager.get_statistics()
    print(f"\n2. Gallery Statistics:")
    print(f"   Total categories: {len(stats['gallery_items'])}")
    for category, count in stats['gallery_items'].items():
        print(f"   - {category}: {count} items")
    
    # Show gallery items
    print(f"\n3. Gallery Items:")
    items = gallery_manager.get_gallery_items()
    for item in items:
        exists = "✓" if Path(item['image_path']).exists() else "✗"
        print(f"   {exists} {item['category']}/{item['label']}: {Path(item['image_path']).name}")
    
    # Get training examples for Gemini
    print(f"\n4. Training Examples for AI:")
    training_examples = gallery_manager.get_training_examples_for_gemini(max_per_category=3)
    print(f"   Using {len(training_examples)} examples (max 3 per category):")
    for ex in training_examples:
        print(f"   - {ex['label']}: {Path(ex['image_path']).name}")
    
    # Test configuration
    print(f"\n5. Configuration Test:")
    config = gallery_manager.config
    threshold = config["gallery_settings"]["confidence_threshold"]
    print(f"   Confidence threshold: {threshold}")
    print(f"   Caching enabled: {config['gallery_settings']['cache_embeddings']}")
    print(f"   Max matches per frame: {config['gallery_settings']['max_matches_per_frame']}")
    
    print("\n" + "=" * 60)
    print("Gallery Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Add building images to data/gallery/<category>/")
    print("2. Run: python test_gallery_recognition.py")
    print("3. Process videos with: python run_media_catalog.py")
    
    # Show example directory structure
    print(f"\nExample gallery structure:")
    print("data/gallery/")
    print("├── president_inch/")
    print("│   ├── President-Edward-Inch-0001.jpg")
    print("│   └── ...")
    print("├── admin_building/")
    print("│   ├── admin_front_view.jpg")
    print("│   └── admin_entrance.jpg")
    print("├── library/")
    print("│   ├── library_exterior.jpg")
    print("│   └── library_atrium.jpg")
    print("└── student_center/")
    print("    ├── student_center_main.jpg")
    print("    └── student_center_lobby.jpg")

if __name__ == "__main__":
    main()
