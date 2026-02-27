#!/usr/bin/env python3
"""
Helper script to add training images to the AI configuration
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from training_manager import TrainingManager

def main():
    manager = TrainingManager()
    
    print("=" * 60)
    print("Training Image Manager")
    print("=" * 60)
    
    # Check for President Inch images
    president_inch_folder = Path("training_images/president_inch")
    
    if not president_inch_folder.exists():
        print(f"\n❌ Folder not found: {president_inch_folder}")
        print("Please create the folder and add images first.")
        return
    
    # Find all image files
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    image_files = []
    for ext in image_extensions:
        image_files.extend(president_inch_folder.glob(f"*{ext}"))
        image_files.extend(president_inch_folder.glob(f"*{ext.upper()}"))
    
    if not image_files:
        print(f"\n❌ No images found in {president_inch_folder}")
        print(f"Supported formats: {', '.join(image_extensions)}")
        return
    
    print(f"\n✓ Found {len(image_files)} images in {president_inch_folder}")
    print("\nImages:")
    for img in image_files:
        print(f"  - {img.name}")
    
    # Add images to configuration
    print(f"\nAdding images to 'president_inch' category with label 'President Inch'...")
    
    for img_path in image_files:
        manager.add_training_example(
            category="president_inch",
            label="President Inch",
            image_path=str(img_path)
        )
    
    print(f"✅ Added {len(image_files)} training images!")
    
    # Show summary
    print("\n" + "=" * 60)
    print("Configuration Summary")
    print("=" * 60)
    
    api_key = manager.get_api_key()
    print(f"API Key: {'✓ Configured' if api_key else '✗ Not configured'}")
    
    print(f"\nTraining Categories:")
    for category in manager.list_categories():
        info = manager.get_category_info(category)
        print(f"\n  {category}:")
        print(f"    Label: {info['label']}")
        print(f"    Images: {len(info['images'])}")
        for img in info['images']:
            exists = "✓" if Path(img).exists() else "✗"
            print(f"      {exists} {img}")
    
    total_examples = len(manager.get_training_examples())
    print(f"\n✅ Total training examples: {total_examples}")
    print("\nYou can now use the Stills Exporter GUI with AI tagging enabled!")

if __name__ == "__main__":
    main()

