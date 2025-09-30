#!/usr/bin/env python3
"""
Test script to verify AI tagging with President Inch training images
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from training_manager import TrainingManager
from ctagger import ImageTagger
import os

def main():
    print("=" * 60)
    print("President Inch AI Tagger Test")
    print("=" * 60)
    
    # Load training manager
    manager = TrainingManager()
    
    # Get API key
    api_key = manager.get_api_key()
    if not api_key:
        print("\n❌ No API key configured in config/ai_config.json")
        return
    
    print(f"\n✓ API key loaded")
    
    # Get training examples
    training_examples = manager.get_training_examples(category="president_inch")
    
    if not training_examples:
        print("\n❌ No training examples found for President Inch")
        print("Run 'python add_training_images.py' first to add training images")
        return
    
    print(f"\n✓ Loaded {len(training_examples)} training examples:")
    for ex in training_examples:
        print(f"  - {ex['label']}: {Path(ex['image_path']).name}")
    
    # Initialize tagger
    print("\nInitializing AI tagger...")
    os.environ["GOOGLE_API_KEY"] = api_key
    tagger = ImageTagger()
    print("✓ Tagger initialized")
    
    # Ask user for test image
    print("\n" + "=" * 60)
    print("Test Image")
    print("=" * 60)
    print("\nEnter the path to a test image to tag:")
    print("(This should be an image that might contain President Inch)")
    
    test_image = input("\nImage path: ").strip().strip('"').strip("'")
    
    if not test_image:
        print("\n❌ No image path provided")
        return
    
    test_image_path = Path(test_image)
    
    if not test_image_path.exists():
        print(f"\n❌ Image not found: {test_image_path}")
        return
    
    print(f"\n✓ Found test image: {test_image_path.name}")
    
    # Tag the image
    print("\nAnalyzing image with AI tagger...")
    print("(This may take a few seconds...)")
    
    try:
        result = tagger.tag(str(test_image_path), training_examples)
        
        print("\n" + "=" * 60)
        print("Results")
        print("=" * 60)
        
        tags = result.tags if hasattr(result, 'tags') else result.get('tags', [])
        
        print(f"\nGenerated {len(tags)} tags:")
        for i, tag in enumerate(tags, 1):
            # Highlight if President Inch is detected
            if "president inch" in tag.lower():
                print(f"  {i}. ⭐ {tag} ⭐")
            else:
                print(f"  {i}. {tag}")
        
        # Check if President Inch was detected
        president_detected = any("president inch" in tag.lower() for tag in tags)
        
        print("\n" + "=" * 60)
        if president_detected:
            print("✅ SUCCESS! President Inch was recognized in the image!")
        else:
            print("⚠️  President Inch was NOT detected in this image.")
            print("This could mean:")
            print("  - President Inch is not in the image")
            print("  - More/better training images are needed")
            print("  - The image quality is too different from training images")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during tagging: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

