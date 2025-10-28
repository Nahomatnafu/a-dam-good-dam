#!/usr/bin/env python3
"""
Demo script for gallery-based recognition system
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pipeline.enhanced_video_processor import EnhancedVideoProcessor
from training_manager import TrainingManager

def demo_single_video():
    """Demo processing a single video"""
    print("=" * 60)
    print("Gallery-Based Video Processing Demo")
    print("=" * 60)
    
    # Get API key
    training_manager = TrainingManager()
    api_key = training_manager.get_api_key()
    
    if not api_key:
        print("❌ No API key configured in config/ai_config.json")
        print("Please add your Google API key first")
        return
    
    # Find a test video
    video_extensions = ['.mp4', '.mov', '.avi', '.mkv']
    test_video = None
    
    for ext in video_extensions:
        videos = list(Path(".").glob(f"*{ext}"))
        if videos:
            test_video = videos[0]
            break
    
    if not test_video:
        print("❌ No test video found in current directory")
        print("Please place a test video (.mp4, .mov, .avi, .mkv) in the current directory")
        return
    
    print(f"Processing video: {test_video}")
    
    # Initialize processor
    processor = EnhancedVideoProcessor(api_key=api_key)
    
    # Process video
    output_dir = Path("demo_output")
    result = processor.process_video_with_gallery(test_video, output_dir)
    
    if result['success']:
        print("\n✅ Processing successful!")
        print(f"Frames extracted: {result['frames_extracted']}")
        print(f"XML output: {result['xml_path']}")
        
        # Show summary
        summary = result['summary']
        print(f"\nSummary:")
        print(f"  Duration: {summary['duration']:.1f} seconds")
        print(f"  Gallery matches: {summary['gallery_matches_found']}")
        print(f"  Top gallery match: {summary['top_gallery_match']}")
        print(f"  Top tags: {', '.join(summary['top_tags'][:5])}")
        
        # Show gallery matches
        gallery_matches = result['analysis_result']['gallery_matches']
        if gallery_matches:
            print(f"\nGallery Matches:")
            for i, match in enumerate(gallery_matches[:5], 1):
                print(f"  {i}. {match['gallery_label']} (confidence: {match['confidence']:.2f})")
        
        print(f"\nOutput files saved to: {output_dir}")
        
    else:
        print(f"❌ Processing failed: {result.get('error', 'Unknown error')}")

def demo_batch_processing():
    """Demo batch processing multiple videos"""
    print("\n" + "=" * 60)
    print("Batch Processing Demo")
    print("=" * 60)
    
    # Get API key
    training_manager = TrainingManager()
    api_key = training_manager.get_api_key()
    
    if not api_key:
        print("❌ No API key configured")
        return
    
    # Find test videos
    video_extensions = ['.mp4', '.mov', '.avi', '.mkv']
    test_videos = []
    
    for ext in video_extensions:
        test_videos.extend(Path(".").glob(f"*{ext}"))
    
    if len(test_videos) < 2:
        print("❌ Need at least 2 videos for batch demo")
        print("Please place multiple test videos in the current directory")
        return
    
    # Limit to first 3 videos for demo
    test_videos = test_videos[:3]
    
    print(f"Batch processing {len(test_videos)} videos:")
    for video in test_videos:
        print(f"  - {video.name}")
    
    # Initialize processor
    processor = EnhancedVideoProcessor(api_key=api_key)
    
    # Process videos
    output_dir = Path("batch_demo_output")
    results = processor.batch_process_videos(test_videos, output_dir, max_workers=2)
    
    # Show results
    successful = sum(1 for r in results if r['success'])
    print(f"\nBatch processing complete: {successful}/{len(results)} videos processed successfully")
    
    for result in results:
        video_name = Path(result['video_path']).name
        if result['success']:
            summary = result['summary']
            print(f"✅ {video_name}: {summary['gallery_matches_found']} gallery matches, {summary['final_tags_count']} tags")
        else:
            print(f"❌ {video_name}: {result.get('error', 'Unknown error')}")

def main():
    print("Gallery-Based Recognition System Demo")
    print("This demo will process videos using the new gallery system")
    print()
    
    # Check if gallery is set up
    gallery_dir = Path("data/gallery")
    if not gallery_dir.exists():
        print("❌ Gallery not set up. Please run:")
        print("1. python migrate_to_gallery.py")
        print("2. python build_gallery_embeddings.py")
        return
    
    # Run demos
    demo_single_video()
    
    # Ask if user wants batch demo
    try:
        response = input("\nRun batch processing demo? (y/n): ").lower().strip()
        if response == 'y':
            demo_batch_processing()
    except KeyboardInterrupt:
        print("\nDemo cancelled")

if __name__ == "__main__":
    main()
