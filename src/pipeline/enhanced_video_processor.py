#!/usr/bin/env python3
"""
Enhanced video processor with gallery-based recognition and smart frame sampling
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Optional
import logging

class EnhancedVideoProcessor:
    def __init__(self, api_key: str, gallery_dir: str = "data/gallery"):
        """Initialize enhanced video processor"""
        self.api_key = api_key
        
        # Import components
        from ai.gallery_vision_tagger import GalleryVisionTagger
        from pipeline.smart_frame_sampler import SmartFrameSampler
        from ai.tag_filter import TagFilter
        
        self.gallery_tagger = GalleryVisionTagger(api_key=api_key, gallery_dir=gallery_dir)
        self.frame_sampler = SmartFrameSampler()
        self.tag_filter = TagFilter()
        
        logging.info("Enhanced video processor initialized")
    
    def process_video_with_gallery(self, video_path: Path, output_dir: Path, 
                                 image_format: str = "jpg") -> Dict:
        """
        Process video with gallery-based recognition
        
        Args:
            video_path: Path to video file
            output_dir: Output directory for frames and analysis
            image_format: Image format for extracted frames
            
        Returns:
            Processing results dictionary
        """
        base_name = self.get_clean_filename(video_path.name)
        clip_stills_folder = output_dir / f"{base_name}_Stills"
        clip_stills_folder.mkdir(parents=True, exist_ok=True)
        
        logging.info(f"Processing video: {video_path.name}")
        
        # Step 1: Smart frame extraction
        video_info = self.frame_sampler.get_video_info(video_path)
        duration = video_info['duration']
        
        if duration <= 0:
            logging.warning(f"Could not read duration for {video_path.name}")
            return {'success': False, 'error': 'Invalid video duration'}
        
        target_frames = self.frame_sampler.get_optimal_frame_count(duration)
        logging.info(f"Video duration: {duration:.1f}s, extracting {target_frames} frames")
        
        # Extract frames using smart sampling
        frame_paths = self.frame_sampler.extract_frames_smart(
            video_path, clip_stills_folder, target_frames, image_format
        )
        
        if not frame_paths:
            logging.warning(f"No frames extracted from {video_path.name}")
            return {'success': False, 'error': 'Frame extraction failed'}
        
        logging.info(f"Extracted {len(frame_paths)} frames")
        
        # Step 2: Gallery-based analysis
        analysis_result = self.gallery_tagger.analyze_video_frames(frame_paths, video_path)
        
        # Step 3: Create enhanced XML output
        xml_path = clip_stills_folder / f"{base_name}_tags.xml"
        self.create_enhanced_xml(analysis_result, xml_path)
        
        # Step 4: Create summary
        summary = self.create_processing_summary(analysis_result, frame_paths, duration)
        
        logging.info(f"Processing complete for {video_path.name}")
        
        return {
            'success': True,
            'video_path': str(video_path),
            'frames_extracted': len(frame_paths),
            'analysis_result': analysis_result,
            'xml_path': str(xml_path),
            'summary': summary
        }
    
    def create_enhanced_xml(self, analysis_result: Dict, xml_path: Path):
        """Create enhanced XML with gallery matches and filtered tags"""
        root = ET.Element("video_analysis")
        
        # Video metadata
        video_elem = ET.SubElement(root, "video")
        video_elem.set("path", analysis_result['video_path'])
        video_elem.set("frames_analyzed", str(analysis_result['frames_analyzed']))
        video_elem.set("aggregation_method", analysis_result['aggregation_method'])
        
        # Gallery matches
        gallery_elem = ET.SubElement(root, "gallery_matches")
        for match in analysis_result['gallery_matches']:
            match_elem = ET.SubElement(gallery_elem, "match")
            match_elem.set("label", match['gallery_label'])
            match_elem.set("category", match['gallery_category'])
            match_elem.set("confidence", f"{match['confidence']:.3f}")
            match_elem.set("frame_count", str(match['frame_count']))
            match_elem.set("match_type", match['match_type'])
        
        # Final tags
        tags_elem = ET.SubElement(root, "final_tags")
        for tag_info in analysis_result['final_tags']:
            tag_elem = ET.SubElement(tags_elem, "tag")
            tag_elem.text = tag_info['tag']
            tag_elem.set("confidence", f"{tag_info['confidence']:.3f}")
            tag_elem.set("frame_count", str(tag_info['frame_count']))
        
        # Frame-by-frame results (optional, for debugging)
        frames_elem = ET.SubElement(root, "frame_results")
        for i, frame_result in enumerate(analysis_result['frame_results']):
            frame_elem = ET.SubElement(frames_elem, "frame")
            frame_elem.set("index", str(i))
            frame_elem.set("path", frame_result['image_path'])
            
            # Frame gallery matches
            for match in frame_result.get('gallery_matches', []):
                frame_match_elem = ET.SubElement(frame_elem, "gallery_match")
                frame_match_elem.set("label", match['gallery_label'])
                frame_match_elem.set("confidence", f"{match['confidence']:.3f}")
        
        # Write XML
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ", level=0)
        tree.write(xml_path, encoding="utf-8", xml_declaration=True)
        
        logging.info(f"Enhanced XML saved: {xml_path}")
    
    def create_processing_summary(self, analysis_result: Dict, frame_paths: List[Path], 
                                duration: float) -> Dict:
        """Create processing summary"""
        gallery_matches = analysis_result['gallery_matches']
        final_tags = analysis_result['final_tags']
        
        # Extract top results
        top_gallery_match = gallery_matches[0] if gallery_matches else None
        top_tags = [tag['tag'] for tag in final_tags[:10]]
        
        # Calculate confidence statistics
        if gallery_matches:
            avg_gallery_confidence = sum(m['confidence'] for m in gallery_matches) / len(gallery_matches)
        else:
            avg_gallery_confidence = 0
        
        if final_tags:
            avg_tag_confidence = sum(t['confidence'] for t in final_tags) / len(final_tags)
        else:
            avg_tag_confidence = 0
        
        return {
            'duration': duration,
            'frames_extracted': len(frame_paths),
            'frames_analyzed': analysis_result['frames_analyzed'],
            'gallery_matches_found': len(gallery_matches),
            'final_tags_count': len(final_tags),
            'top_gallery_match': top_gallery_match['gallery_label'] if top_gallery_match else None,
            'top_gallery_confidence': top_gallery_match['confidence'] if top_gallery_match else 0,
            'top_tags': top_tags,
            'avg_gallery_confidence': avg_gallery_confidence,
            'avg_tag_confidence': avg_tag_confidence,
            'processing_method': 'gallery_based_smart_sampling'
        }
    
    def get_clean_filename(self, filename: str) -> str:
        """Clean filename for safe file operations"""
        import re
        base = Path(filename).stem
        # Remove special characters, keep alphanumeric, spaces, hyphens, underscores
        clean = re.sub(r'[^\w\-\.\(\) ]', '', base)
        # Replace multiple spaces with single underscore
        clean = re.sub(r' +', '_', clean)
        return clean
    
    def batch_process_videos(self, video_paths: List[Path], output_dir: Path, 
                           max_workers: int = 4) -> List[Dict]:
        """
        Process multiple videos in parallel
        
        Args:
            video_paths: List of video file paths
            output_dir: Output directory
            max_workers: Maximum number of parallel workers
            
        Returns:
            List of processing results
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import threading
        
        results = []
        stop_flag = threading.Event()
        
        logging.info(f"Batch processing {len(video_paths)} videos with {max_workers} workers")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all jobs
            future_to_video = {
                executor.submit(self.process_video_with_gallery, video_path, output_dir): video_path
                for video_path in video_paths
            }
            
            # Collect results
            for future in as_completed(future_to_video):
                if stop_flag.is_set():
                    break
                
                video_path = future_to_video[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result['success']:
                        logging.info(f"✅ Processed {video_path.name}")
                    else:
                        logging.warning(f"❌ Failed to process {video_path.name}: {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    logging.error(f"❌ Error processing {video_path.name}: {e}")
                    results.append({
                        'success': False,
                        'video_path': str(video_path),
                        'error': str(e)
                    })
        
        # Summary statistics
        successful = sum(1 for r in results if r['success'])
        logging.info(f"Batch processing complete: {successful}/{len(video_paths)} videos processed successfully")
        
        return results
