import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime

class FileScanner:
    def __init__(self):
        self.video_extensions = {'.mp4', '.mov', '.mxf', '.mkv', '.avi', 
                               '.mts', '.m2ts', '.wmv', '.webm', '.3gp', '.m4v'}
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'}
    
    def scan_directory(self, directory: Path) -> List[Dict]:
        """Scan directory for media files and extract basic info"""
        media_files = []
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        # Find all media files
        for file_path in directory.rglob("*"):
            if file_path.is_file() and self._is_media_file(file_path):
                file_info = self._extract_file_info(file_path)
                if file_info:
                    media_files.append(file_info)
        
        return media_files
    
    def _is_media_file(self, file_path: Path) -> bool:
        """Check if file is a supported media file"""
        ext = file_path.suffix.lower()
        return ext in self.video_extensions or ext in self.image_extensions
    
    def _extract_file_info(self, file_path: Path) -> Optional[Dict]:
        """Extract basic file information"""
        try:
            stat = file_path.stat()
            
            file_info = {
                'filename': file_path.name,
                'filepath': str(file_path.absolute()),
                'filesize': stat.st_size,
                'created_date': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified_date': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'file_type': self._get_file_type(file_path)
            }
            
            # Get video-specific info if it's a video
            if file_path.suffix.lower() in self.video_extensions:
                video_info = self._get_video_info(file_path)
                file_info.update(video_info)
            
            return file_info
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None
    
    def _get_file_type(self, file_path: Path) -> str:
        """Determine file type"""
        ext = file_path.suffix.lower()
        if ext in self.video_extensions:
            return 'video'
        elif ext in self.image_extensions:
            return 'image'
        return 'unknown'
    
    def _get_video_info(self, video_path: Path) -> Dict:
        """Extract video metadata using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', str(video_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                # Find video stream
                video_stream = None
                for stream in data.get('streams', []):
                    if stream.get('codec_type') == 'video':
                        video_stream = stream
                        break
                
                info = {}
                if video_stream:
                    info['width'] = video_stream.get('width')
                    info['height'] = video_stream.get('height')
                
                # Get duration from format
                format_info = data.get('format', {})
                duration = format_info.get('duration')
                if duration:
                    info['duration'] = float(duration)
                
                return info
            
        except Exception as e:
            print(f"Error getting video info for {video_path}: {e}")
        
        return {}