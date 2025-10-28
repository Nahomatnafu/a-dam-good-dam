#!/usr/bin/env python3
"""
Evaluation script for gallery-based recognition system
"""

import sys
import time
import json
import statistics
from pathlib import Path
from typing import List, Dict, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai.gallery_vision_tagger import GalleryVisionTagger
from ai.gallery_manager import GalleryManager
from training_manager import TrainingManager
from pipeline.smart_frame_sampler import SmartFrameSampler

class GallerySystemEvaluator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.gallery_tagger = GalleryVisionTagger(api_key=api_key)
        self.gallery_manager = GalleryManager()
        self.frame_sampler = SmartFrameSampler()
        
        self.results = {
            'precision_at_k': {},
            'recall': {},
            'processing_times': [],
            'accuracy_scores': [],
            'gallery_match_rates': []
        }
    
    def evaluate_single_image(self, image_path: Path, expected_labels: List[str]) -> Dict:
        """Evaluate recognition on a single image"""
        start_time = time.time()
        
        result = self.gallery_tagger.analyze_frame_with_gallery(image_path)
        
        processing_time = time.time() - start_time
        
        # Extract predicted labels
        predicted_gallery = [m['gallery_label'].lower() for m in result.get('gallery_matches', [])]
        predicted_tags = [t['tag'].lower() for t in result.get('filtered_labels', [])]
        all_predicted = predicted_gallery + predicted_tags
        
        # Normalize expected labels
        expected_normalized = [label.lower() for label in expected_labels]
        
        # Calculate metrics
        metrics = self.calculate_metrics(all_predicted, expected_normalized)
        metrics['processing_time'] = processing_time
        metrics['gallery_matches_found'] = len(predicted_gallery)
        metrics['total_tags_found'] = len(all_predicted)
        
        return metrics
    
    def evaluate_video(self, video_path: Path, expected_labels: List[str]) -> Dict:
        """Evaluate recognition on a video"""
        start_time = time.time()
        
        # Extract frames
        output_dir = Path("data/cache/eval_frames")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        frame_paths = self.frame_sampler.extract_frames_smart(video_path, output_dir, target_frames=5)
        
        if not frame_paths:
            return {'error': 'No frames extracted'}
        
        # Analyze video
        result = self.gallery_tagger.analyze_video_frames(frame_paths, video_path)
        
        processing_time = time.time() - start_time
        
        # Extract predicted labels
        predicted_gallery = [m['gallery_label'].lower() for m in result.get('gallery_matches', [])]
        predicted_tags = [t['tag'].lower() for t in result.get('final_tags', [])]
        all_predicted = predicted_gallery + predicted_tags
        
        # Normalize expected labels
        expected_normalized = [label.lower() for label in expected_labels]
        
        # Calculate metrics
        metrics = self.calculate_metrics(all_predicted, expected_normalized)
        metrics['processing_time'] = processing_time
        metrics['frames_analyzed'] = result['frames_analyzed']
        metrics['gallery_matches_found'] = len(predicted_gallery)
        metrics['total_tags_found'] = len(all_predicted)
        
        return metrics
    
    def calculate_metrics(self, predicted: List[str], expected: List[str]) -> Dict:
        """Calculate precision, recall, and accuracy metrics"""
        if not expected:
            return {'precision': 0, 'recall': 0, 'f1': 0, 'accuracy': 0}
        
        # Convert to sets for easier calculation
        predicted_set = set(predicted)
        expected_set = set(expected)
        
        # True positives: predicted labels that are in expected
        true_positives = len(predicted_set.intersection(expected_set))
        
        # False positives: predicted labels that are not in expected
        false_positives = len(predicted_set - expected_set)
        
        # False negatives: expected labels that were not predicted
        false_negatives = len(expected_set - predicted_set)
        
        # Calculate metrics
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Accuracy: correct predictions / total expected
        accuracy = true_positives / len(expected_set) if expected_set else 0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'accuracy': accuracy,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'predicted_labels': list(predicted_set),
            'expected_labels': list(expected_set),
            'matched_labels': list(predicted_set.intersection(expected_set))
        }
    
    def precision_at_k(self, predicted: List[str], expected: List[str], k: int) -> float:
        """Calculate precision@k metric"""
        if not predicted or not expected:
            return 0.0
        
        top_k_predicted = predicted[:k]
        expected_set = set(expected)
        
        relevant_in_top_k = sum(1 for pred in top_k_predicted if pred in expected_set)
        return relevant_in_top_k / min(k, len(top_k_predicted))
    
    def run_evaluation_suite(self, test_data: List[Dict]) -> Dict:
        """Run complete evaluation suite"""
        print("=" * 60)
        print("Gallery System Evaluation")
        print("=" * 60)
        
        all_metrics = []
        processing_times = []
        
        for i, test_item in enumerate(test_data, 1):
            print(f"\nTest {i}/{len(test_data)}: {test_item['name']}")
            
            file_path = Path(test_item['path'])
            expected_labels = test_item['expected_labels']
            
            if not file_path.exists():
                print(f"  ❌ File not found: {file_path}")
                continue
            
            # Determine if it's an image or video
            if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
                metrics = self.evaluate_single_image(file_path, expected_labels)
            else:
                metrics = self.evaluate_video(file_path, expected_labels)
            
            if 'error' in metrics:
                print(f"  ❌ Error: {metrics['error']}")
                continue
            
            all_metrics.append(metrics)
            processing_times.append(metrics['processing_time'])
            
            # Print results
            print(f"  Precision: {metrics['precision']:.3f}")
            print(f"  Recall: {metrics['recall']:.3f}")
            print(f"  F1: {metrics['f1']:.3f}")
            print(f"  Accuracy: {metrics['accuracy']:.3f}")
            print(f"  Processing time: {metrics['processing_time']:.2f}s")
            print(f"  Matched: {metrics['matched_labels']}")
        
        # Calculate aggregate metrics
        if all_metrics:
            avg_precision = statistics.mean(m['precision'] for m in all_metrics)
            avg_recall = statistics.mean(m['recall'] for m in all_metrics)
            avg_f1 = statistics.mean(m['f1'] for m in all_metrics)
            avg_accuracy = statistics.mean(m['accuracy'] for m in all_metrics)
            avg_processing_time = statistics.mean(processing_times)
            
            print("\n" + "=" * 60)
            print("Aggregate Results")
            print("=" * 60)
            print(f"Average Precision: {avg_precision:.3f}")
            print(f"Average Recall: {avg_recall:.3f}")
            print(f"Average F1: {avg_f1:.3f}")
            print(f"Average Accuracy: {avg_accuracy:.3f}")
            print(f"Average Processing Time: {avg_processing_time:.2f}s")
            print(f"Total Tests: {len(all_metrics)}")
            
            return {
                'avg_precision': avg_precision,
                'avg_recall': avg_recall,
                'avg_f1': avg_f1,
                'avg_accuracy': avg_accuracy,
                'avg_processing_time': avg_processing_time,
                'total_tests': len(all_metrics),
                'individual_results': all_metrics
            }
        else:
            print("\n❌ No successful evaluations")
            return {'error': 'No successful evaluations'}

def create_sample_test_data() -> List[Dict]:
    """Create sample test data structure"""
    return [
        {
            'name': 'President Inch Image',
            'path': 'data/gallery/president_inch/President-Edward-Inch-0001.jpg',
            'expected_labels': ['president inch', 'university president']
        },
        {
            'name': 'Admin Building Image',
            'path': 'data/gallery/admin_building/admin_front.jpg',
            'expected_labels': ['administration building', 'campus building']
        },
        {
            'name': 'Sample Video',
            'path': 'test_video.mp4',
            'expected_labels': ['campus', 'university']
        }
    ]

def main():
    # Get API key
    training_manager = TrainingManager()
    api_key = training_manager.get_api_key()
    
    if not api_key:
        print("❌ No API key configured in config/ai_config.json")
        return
    
    # Create evaluator
    evaluator = GallerySystemEvaluator(api_key)
    
    # Create or load test data
    test_data_path = Path("evaluation_test_data.json")
    
    if test_data_path.exists():
        with open(test_data_path, 'r') as f:
            test_data = json.load(f)
        print(f"Loaded test data from {test_data_path}")
    else:
        test_data = create_sample_test_data()
        with open(test_data_path, 'w') as f:
            json.dump(test_data, f, indent=2)
        print(f"Created sample test data: {test_data_path}")
        print("Please update the test data with your actual test files and expected labels")
    
    # Run evaluation
    results = evaluator.run_evaluation_suite(test_data)
    
    # Save results
    results_path = Path("evaluation_results.json")
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {results_path}")

if __name__ == "__main__":
    main()
