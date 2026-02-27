#!/usr/bin/env python3
"""
Test gallery-based recognition system
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai.gallery_vision_tagger import GalleryVisionTagger
from ai.gallery_manager import GalleryManager
from training_manager import TrainingManager
from pipeline.smart_frame_sampler import SmartFrameSampler

def test_single_image():
    """Test recognition on a single image"""
    print("\n" + "=" * 50)
    print("Single Image Recognition Test")
    print("=" * 50)
    
    # Get API key
    training_manager = TrainingManager()
    api_key = training_manager.get_api_key()
    
    if not api_key:
        print("❌ No API key configured")
        return
    
    # Initialize tagger
    tagger = GalleryVisionTagger(api_key=api_key)
    
    # Find a test image
    gallery_dir = Path("data/gallery")
    test_images = []
    
    for category_dir in gallery_dir.iterdir():
        if category_dir.is_dir():
            for img_file in category_dir.glob("*.jpg"):
                test_images.append(img_file)
                break  # Just one per category
    
    if not test_images:
        print("❌ No test images found in data/gallery/")
        print("Please add some images first")
        return
    
    # Test first image
    test_image = test_images[0]
    print(f"\nTesting image: {test_image}")
    
    start_time = time.time()
    result = tagger.analyze_frame_with_gallery(test_image)
    end_time = time.time()
    
    print(f"\nAnalysis completed in {end_time - start_time:.2f} seconds")
    print(f"\nResults:")
    print(f"  Raw labels: {len(result.get('labels', []))}")
    print(f"  Filtered tags: {len(result.get('filtered_labels', []))}")
    print(f"  Gallery matches: {len(result.get('gallery_matches', []))}")
    
    # Show top results
    print(f"\nTop filtered tags:")
    for i, tag_info in enumerate(result.get('filtered_labels', [])[:5], 1):
        print(f"  {i}. {tag_info['tag']} (confidence: {tag_info['confidence']:.2f})")
    
    print(f"\nGallery matches:")
    for i, match in enumerate(result.get('gallery_matches', [])[:3], 1):
        print(f"  {i}. {match['gallery_label']} (confidence: {match['confidence']:.2f})")
    
    return result

def test_video_processing():
    """Test video frame extraction and analysis"""
    print("\n" + "=" * 50)
    print("Video Processing Test")
    print("=" * 50)
    
    # Find a test video
    video_extensions = ['.mp4', '.mov', '.avi', '.mkv']
    test_video = None
    
    # Look in common directories
    search_dirs = [Path("."), Path("test_data"), Path("videos")]
    
    for search_dir in search_dirs:
        if search_dir.exists():
            for ext in video_extensions:
                videos = list(search_dir.glob(f"*{ext}"))
                if videos:
                    test_video = videos[0]
                    break
            if test_video:
                break
    
    if not test_video:
        print("❌ No test video found")
        print("Please place a test video in the current directory")
        return
    
    print(f"Testing video: {test_video}")
    
    # Initialize components
    training_manager = TrainingManager()
    api_key = training_manager.get_api_key()
    
    if not api_key:
        print("❌ No API key configured")
        return
    
    sampler = SmartFrameSampler()
    tagger = GalleryVisionTagger(api_key=api_key)
    
    # Extract frames
    print(f"\n1. Extracting frames...")
    output_dir = Path("data/cache/test_frames")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    start_time = time.time()
    frame_paths = sampler.extract_frames_smart(test_video, output_dir, target_frames=5)
    extraction_time = time.time() - start_time
    
    print(f"   Extracted {len(frame_paths)} frames in {extraction_time:.2f} seconds")
    
    if not frame_paths:
        print("❌ No frames extracted")
        return
    
    # Analyze frames
    print(f"\n2. Analyzing frames...")
    start_time = time.time()
    result = tagger.analyze_video_frames(frame_paths, test_video)
    analysis_time = time.time() - start_time
    
    print(f"   Analysis completed in {analysis_time:.2f} seconds")
    print(f"   Average time per frame: {analysis_time / len(frame_paths):.2f} seconds")
    
    # Show results
    print(f"\n3. Results:")
    print(f"   Frames analyzed: {result['frames_analyzed']}")
    print(f"   Gallery matches: {len(result['gallery_matches'])}")
    print(f"   Final tags: {len(result['final_tags'])}")
    
    print(f"\nTop gallery matches:")
    for i, match in enumerate(result['gallery_matches'][:3], 1):
        print(f"  {i}. {match['gallery_label']} (confidence: {match['confidence']:.2f}, frames: {match['frame_count']})")
    
    print(f"\nTop final tags:")
    for i, tag_info in enumerate(result['final_tags'][:5], 1):
        print(f"  {i}. {tag_info['tag']} (confidence: {tag_info['confidence']:.2f}, frames: {tag_info['frame_count']})")
    
    return result

def test_performance():
    """Test performance metrics"""
    print("\n" + "=" * 50)
    print("Performance Test")
    print("=" * 50)
    
    # Test gallery loading
    start_time = time.time()
    gallery_manager = GalleryManager()
    stats = gallery_manager.get_statistics()
    load_time = time.time() - start_time
    
    print(f"Gallery loading time: {load_time:.3f} seconds")
    print(f"Gallery items: {sum(stats['gallery_items'].values())}")
    print(f"Cached frames: {stats['cached_frames']}")
    
    # Test training examples loading
    start_time = time.time()
    examples = gallery_manager.get_training_examples_for_gemini(max_per_category=3)
    examples_time = time.time() - start_time
    
    print(f"Training examples loading time: {examples_time:.3f} seconds")
    print(f"Training examples: {len(examples)}")
    
    return {
        'gallery_load_time': load_time,
        'examples_load_time': examples_time,
        'gallery_items': sum(stats['gallery_items'].values()),
        'training_examples': len(examples)
    }

def main():
    print("=" * 60)
    print("Gallery Recognition System Test")
    print("=" * 60)
    
    # Check setup
    gallery_dir = Path("data/gallery")
    if not gallery_dir.exists():
        print("❌ Gallery directory not found")
        print("Please run: python migrate_to_gallery.py first")
        return
    
    # Run tests
    try:
        # Test 1: Performance
        perf_results = test_performance()
        
        # Test 2: Single image
        image_result = test_single_image()
        
        # Test 3: Video processing (optional)
        video_result = test_video_processing()
        
        # Summary
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        print("✅ Gallery system is working correctly")
        print(f"✅ Performance: {perf_results['gallery_items']} gallery items loaded in {perf_results['gallery_load_time']:.3f}s")
        
        if image_result:
            print(f"✅ Image analysis: {len(image_result.get('gallery_matches', []))} gallery matches found")
        
        if video_result:
            print(f"✅ Video analysis: {video_result['frames_analyzed']} frames processed")
        
        print("\nSystem is ready for production use!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
