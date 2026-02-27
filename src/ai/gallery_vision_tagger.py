#!/usr/bin/env python3
"""
Enhanced vision tagger with gallery-based recognition and smart caching
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging

# Import existing components
try:
    from src.ctagger import ImageTagger
    LANGCHAIN_AVAILABLE = True
except ImportError:
    try:
        from ctagger import ImageTagger
        LANGCHAIN_AVAILABLE = True
    except ImportError:
        LANGCHAIN_AVAILABLE = False

from .gallery_manager import GalleryManager
from .tag_filter import TagFilter

class GalleryVisionTagger:
    def __init__(self, api_key: Optional[str] = None, gallery_dir: str = "data/gallery"):
        """
        Initialize gallery-based vision tagger
        
        Args:
            api_key: Google API key for Gemini
            gallery_dir: Path to gallery directory
        """
        self.api_key = api_key
        self.gallery_manager = GalleryManager(gallery_dir)
        self.tag_filter = TagFilter()
        self.langchain_tagger = None
        self.mock_mode = False
        
        # Initialize AI tagger
        if LANGCHAIN_AVAILABLE and api_key:
            try:
                os.environ["GOOGLE_API_KEY"] = api_key
                self.langchain_tagger = ImageTagger()
                logging.info("✅ Using LangChain + Gemini for gallery-based tagging")
            except Exception as e:
                logging.warning(f"⚠️ LangChain tagger failed: {e}")
                self.mock_mode = True
        else:
            logging.warning("📝 Using mock analysis (no AI libraries available)")
            self.mock_mode = True
    
    def analyze_frame_with_gallery(self, frame_path: Path, video_path: Optional[Path] = None) -> Dict:
        """
        Analyze a single frame using gallery-based recognition
        
        Args:
            frame_path: Path to frame image
            video_path: Optional path to source video (for caching)
            
        Returns:
            Analysis result with gallery matches and filtered tags
        """
        # Check cache first
        if video_path:
            cached_result = self.gallery_manager.get_cached_frame_analysis(str(frame_path))
            if cached_result:
                logging.debug(f"Using cached analysis for {frame_path.name}")
                return cached_result
        
        # Get gallery training examples
        training_examples = self.gallery_manager.get_training_examples_for_gemini(max_per_category=3)
        
        if self.mock_mode:
            result = self.mock_analyze_frame(frame_path, training_examples)
        else:
            result = self.analyze_frame_with_ai(frame_path, training_examples)
        
        # Apply tag filtering
        raw_tags = [label['description'] for label in result.get('labels', [])]
        raw_confidences = [label.get('score', 0.8) for label in result.get('labels', [])]
        
        filtered_tags = self.tag_filter.filter_tags(raw_tags, raw_confidences)
        
        # Update result with filtered tags
        result['filtered_labels'] = filtered_tags
        result['gallery_matches'] = self.find_gallery_matches(filtered_tags)
        result['filter_stats'] = self.tag_filter.get_statistics(raw_tags, filtered_tags)
        
        # Cache result
        if video_path:
            self.gallery_manager.cache_frame_analysis(str(video_path), str(frame_path), result)
        
        return result
    
    def analyze_frame_with_ai(self, frame_path: Path, training_examples: List[Dict]) -> Dict:
        """Analyze frame using Gemini with gallery examples"""
        try:
            result = self.langchain_tagger.tag(str(frame_path), training_examples)
            tags = result.tags if hasattr(result, 'tags') else result.get('tags', [])
            
            return {
                'labels': [{'description': tag, 'score': 0.9} for tag in tags],
                'text': [],
                'faces_count': 0,
                'image_path': str(frame_path),
                'training_examples_used': len(training_examples)
            }
        except Exception as e:
            logging.warning(f"⚠️ AI tagging failed for {frame_path.name}: {e}")
            return self.mock_analyze_frame(frame_path, training_examples)
    
    def mock_analyze_frame(self, frame_path: Path, training_examples: List[Dict]) -> Dict:
        """Mock analysis for testing"""
        filename = frame_path.name.lower()
        
        mock_labels = []
        
        # Check for gallery matches in filename
        for example in training_examples:
            label = example['label'].lower()
            if any(word in filename for word in label.split()):
                mock_labels.append({'description': example['label'], 'score': 0.95})
        
        # Add generic academic tags
        if 'president' in filename or 'inch' in filename:
            mock_labels.extend([
                {'description': 'President Inch', 'score': 0.95},
                {'description': 'university president', 'score': 0.9},
                {'description': 'academic leader', 'score': 0.85}
            ])
        elif 'building' in filename or 'admin' in filename:
            mock_labels.extend([
                {'description': 'Administration Building', 'score': 0.9},
                {'description': 'campus building', 'score': 0.85},
                {'description': 'university architecture', 'score': 0.8}
            ])
        else:
            mock_labels.extend([
                {'description': 'campus scene', 'score': 0.8},
                {'description': 'university setting', 'score': 0.75},
                {'description': 'academic environment', 'score': 0.7}
            ])
        
        return {
            'labels': mock_labels,
            'text': [],
            'faces_count': 1 if 'president' in filename else 0,
            'image_path': str(frame_path),
            'training_examples_used': len(training_examples),
            'mock_mode': True
        }
    
    def find_gallery_matches(self, filtered_tags: List[Dict]) -> List[Dict]:
        """Find matches between filtered tags and gallery items"""
        gallery_items = self.gallery_manager.get_gallery_items()
        matches = []
        
        for tag_info in filtered_tags:
            tag = tag_info['tag'].lower()
            tag_confidence = tag_info['confidence']
            
            for item in gallery_items:
                item_label = item['label'].lower()
                
                # Simple matching - can be enhanced with fuzzy matching
                if (tag in item_label or item_label in tag or 
                    any(word in item_label for word in tag.split()) or
                    any(word in tag for word in item_label.split())):
                    
                    match_confidence = min(tag_confidence * 0.9, 0.95)  # Slight penalty for matching
                    
                    matches.append({
                        'gallery_item_id': item['id'],
                        'gallery_label': item['label'],
                        'gallery_category': item['category'],
                        'matched_tag': tag_info['tag'],
                        'confidence': match_confidence,
                        'match_type': 'label_similarity'
                    })
        
        # Sort by confidence and remove duplicates
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        seen_items = set()
        unique_matches = []
        
        for match in matches:
            item_id = match['gallery_item_id']
            if item_id not in seen_items:
                unique_matches.append(match)
                seen_items.add(item_id)
        
        return unique_matches[:5]  # Top 5 matches
    
    def analyze_video_frames(self, frame_paths: List[Path], video_path: Path) -> Dict:
        """
        Analyze multiple frames from a video and aggregate results
        
        Args:
            frame_paths: List of frame image paths
            video_path: Path to source video
            
        Returns:
            Aggregated analysis results
        """
        frame_results = []
        all_gallery_matches = []
        all_filtered_tags = []
        
        logging.info(f"Analyzing {len(frame_paths)} frames from {video_path.name}")
        
        for i, frame_path in enumerate(frame_paths):
            logging.debug(f"Analyzing frame {i+1}/{len(frame_paths)}: {frame_path.name}")
            
            result = self.analyze_frame_with_gallery(frame_path, video_path)
            frame_results.append(result)
            
            # Collect gallery matches
            all_gallery_matches.extend(result.get('gallery_matches', []))
            
            # Collect filtered tags
            all_filtered_tags.extend(result.get('filtered_labels', []))
        
        # Aggregate results
        aggregated_result = self.aggregate_frame_results(frame_results, video_path)
        
        return aggregated_result
    
    def aggregate_frame_results(self, frame_results: List[Dict], video_path: Path) -> Dict:
        """Aggregate results from multiple frames using confidence weighting"""
        # Aggregate gallery matches by confidence
        gallery_match_scores = {}
        tag_scores = {}
        
        for result in frame_results:
            # Process gallery matches
            for match in result.get('gallery_matches', []):
                item_id = match['gallery_item_id']
                confidence = match['confidence']
                
                if item_id not in gallery_match_scores:
                    gallery_match_scores[item_id] = {
                        'match': match,
                        'total_confidence': 0,
                        'frame_count': 0
                    }
                
                gallery_match_scores[item_id]['total_confidence'] += confidence
                gallery_match_scores[item_id]['frame_count'] += 1
            
            # Process filtered tags
            for tag_info in result.get('filtered_labels', []):
                tag = tag_info['tag']
                confidence = tag_info['confidence']
                
                if tag not in tag_scores:
                    tag_scores[tag] = {'total_confidence': 0, 'frame_count': 0}
                
                tag_scores[tag]['total_confidence'] += confidence
                tag_scores[tag]['frame_count'] += 1
        
        # Calculate final gallery matches (majority vote with confidence weighting)
        final_gallery_matches = []
        for item_id, data in gallery_match_scores.items():
            avg_confidence = data['total_confidence'] / data['frame_count']
            frame_ratio = data['frame_count'] / len(frame_results)
            
            # Require match in at least 30% of frames OR high confidence
            if frame_ratio >= 0.3 or avg_confidence >= 0.85:
                match = data['match'].copy()
                match['confidence'] = avg_confidence * frame_ratio  # Weight by frequency
                match['frame_count'] = data['frame_count']
                final_gallery_matches.append(match)
        
        # Calculate final tags
        final_tags = []
        for tag, data in tag_scores.items():
            avg_confidence = data['total_confidence'] / data['frame_count']
            frame_ratio = data['frame_count'] / len(frame_results)
            
            # Include tags that appear in multiple frames or have high confidence
            if frame_ratio >= 0.2 or avg_confidence >= 0.8:
                final_tags.append({
                    'tag': tag,
                    'confidence': avg_confidence * frame_ratio,
                    'frame_count': data['frame_count']
                })
        
        # Sort results
        final_gallery_matches.sort(key=lambda x: x['confidence'], reverse=True)
        final_tags.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {
            'video_path': str(video_path),
            'frames_analyzed': len(frame_results),
            'gallery_matches': final_gallery_matches[:10],  # Top 10
            'final_tags': final_tags[:20],  # Top 20
            'frame_results': frame_results,
            'aggregation_method': 'confidence_weighted_majority'
        }
