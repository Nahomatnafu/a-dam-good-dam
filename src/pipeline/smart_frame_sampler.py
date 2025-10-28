#!/usr/bin/env python3
"""
Smart frame sampling for video analysis with scene detection and motion filtering
"""

import subprocess
import json
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict
import logging

class SmartFrameSampler:
    def __init__(self):
        self.motion_threshold = 0.1  # Minimum motion to consider frame
        self.scene_threshold = 0.3   # Scene change threshold
        
    def get_video_info(self, video_path: Path) -> Dict:
        """Get video metadata using ffprobe"""
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', str(video_path)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                format_info = data.get('format', {})
                
                # Find video stream
                video_stream = None
                for stream in data.get('streams', []):
                    if stream.get('codec_type') == 'video':
                        video_stream = stream
                        break
                
                return {
                    'duration': float(format_info.get('duration', 0)),
                    'fps': eval(video_stream.get('r_frame_rate', '30/1')) if video_stream else 30,
                    'width': video_stream.get('width', 0) if video_stream else 0,
                    'height': video_stream.get('height', 0) if video_stream else 0
                }
        except Exception as e:
            logging.warning(f"Failed to get video info for {video_path}: {e}")
        
        return {'duration': 0, 'fps': 30, 'width': 0, 'height': 0}
    
    def detect_scenes_ffmpeg(self, video_path: Path, threshold: float = 0.3) -> List[float]:
        """Use FFmpeg scene detection to find scene boundaries"""
        cmd = [
            'ffmpeg', '-i', str(video_path), '-vf', f'select=gt(scene\\,{threshold})',
            '-f', 'null', '-'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            # Parse scene change timestamps from stderr
            scene_times = []
            for line in result.stderr.split('\n'):
                if 'pts_time:' in line:
                    try:
                        time_str = line.split('pts_time:')[1].split()[0]
                        scene_times.append(float(time_str))
                    except (IndexError, ValueError):
                        continue
            
            return sorted(scene_times)
        except Exception as e:
            logging.warning(f"Scene detection failed for {video_path}: {e}")
            return []
    
    def calculate_smart_timestamps(self, video_path: Path, target_frames: int = 10) -> List[float]:
        """Calculate optimal frame timestamps using scene detection and motion analysis"""
        video_info = self.get_video_info(video_path)
        duration = video_info['duration']
        
        if duration <= 0:
            return []
        
        # Try scene detection first
        scene_times = self.detect_scenes_ffmpeg(video_path, self.scene_threshold)
        
        if len(scene_times) >= target_frames:
            # Use scene boundaries, taking every nth scene
            step = len(scene_times) // target_frames
            selected_times = scene_times[::step][:target_frames]
        elif len(scene_times) > 0:
            # Mix scene boundaries with uniform sampling
            timestamps = scene_times.copy()
            
            # Add uniform samples to reach target
            remaining = target_frames - len(scene_times)
            if remaining > 0:
                uniform_times = self.calculate_uniform_timestamps(duration, remaining, scene_times)
                timestamps.extend(uniform_times)
            
            selected_times = sorted(timestamps)[:target_frames]
        else:
            # Fallback to uniform sampling with motion filtering
            selected_times = self.calculate_uniform_timestamps(duration, target_frames)
        
        # Ensure we don't sample too close to start/end
        epsilon = min(0.5, duration * 0.02)  # 500ms or 2% of duration
        selected_times = [max(epsilon, min(duration - epsilon, t)) for t in selected_times]
        
        return sorted(selected_times)
    
    def calculate_uniform_timestamps(self, duration: float, count: int, avoid_times: List[float] = None) -> List[float]:
        """Calculate uniform timestamps, avoiding specified times"""
        if avoid_times is None:
            avoid_times = []
        
        timestamps = []
        for i in range(1, count + 1):
            t = (duration * i) / (count + 1)
            
            # Avoid times too close to scene boundaries
            if avoid_times:
                min_distance = min(abs(t - avoid_t) for avoid_t in avoid_times)
                if min_distance < 2.0:  # Less than 2 seconds from scene boundary
                    # Shift timestamp
                    t = t + 2.0 if t < duration - 2.0 else t - 2.0
            
            timestamps.append(t)
        
        return timestamps
    
    def extract_frames_smart(self, video_path: Path, output_dir: Path, 
                           target_frames: int = 10, format: str = "jpg") -> List[Path]:
        """Extract frames using smart sampling"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamps = self.calculate_smart_timestamps(video_path, target_frames)
        if not timestamps:
            logging.warning(f"No timestamps calculated for {video_path}")
            return []
        
        base_name = video_path.stem
        extracted_frames = []
        
        # Extract frames at calculated timestamps
        for i, timestamp in enumerate(timestamps):
            output_path = output_dir / f"{base_name}_frame_{i+1:03d}.{format}"
            
            cmd = [
                'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                '-ss', str(timestamp), '-i', str(video_path),
                '-frames:v', '1', '-q:v', '2',  # High quality
                str(output_path)
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, timeout=30)
                if result.returncode == 0 and output_path.exists():
                    extracted_frames.append(output_path)
                    logging.debug(f"Extracted frame at {timestamp:.2f}s: {output_path.name}")
                else:
                    logging.warning(f"Failed to extract frame at {timestamp:.2f}s")
            except subprocess.TimeoutExpired:
                logging.warning(f"Timeout extracting frame at {timestamp:.2f}s")
            except Exception as e:
                logging.warning(f"Error extracting frame at {timestamp:.2f}s: {e}")
        
        logging.info(f"Extracted {len(extracted_frames)}/{len(timestamps)} frames from {video_path.name}")
        return extracted_frames
    
    def filter_frames_by_motion(self, frame_paths: List[Path], threshold: float = 0.1) -> List[Path]:
        """Filter frames by motion content (remove static frames)"""
        if len(frame_paths) < 2:
            return frame_paths
        
        filtered_frames = []
        prev_frame = None
        
        for frame_path in frame_paths:
            try:
                # Load frame
                frame = cv2.imread(str(frame_path), cv2.IMREAD_GRAYSCALE)
                if frame is None:
                    continue
                
                if prev_frame is not None:
                    # Calculate motion between frames
                    diff = cv2.absdiff(frame, prev_frame)
                    motion_score = np.mean(diff) / 255.0
                    
                    if motion_score > threshold:
                        filtered_frames.append(frame_path)
                else:
                    # Always include first frame
                    filtered_frames.append(frame_path)
                
                prev_frame = frame
                
            except Exception as e:
                logging.warning(f"Error processing frame {frame_path}: {e}")
                # Include frame if we can't process it
                filtered_frames.append(frame_path)
        
        logging.info(f"Motion filtering: {len(filtered_frames)}/{len(frame_paths)} frames kept")
        return filtered_frames
    
    def get_optimal_frame_count(self, duration: float) -> int:
        """Calculate optimal number of frames based on video duration"""
        if duration <= 0:
            return 5
        elif duration <= 30:      # 0-30 seconds: 5 frames
            return 5
        elif duration <= 60:      # 30s-1min: 8 frames
            return 8
        elif duration <= 120:     # 1-2 minutes: 12 frames
            return 12
        elif duration <= 300:     # 2-5 minutes: 15 frames
            return 15
        elif duration <= 600:     # 5-10 minutes: 20 frames
            return 20
        elif duration <= 1800:    # 10-30 minutes: 25 frames
            return 25
        else:                     # 30+ minutes: 30 frames max
            return 30
