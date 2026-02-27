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
                video_info = self._get_video_info_simple(file_path)
                if video_info:
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

    def _get_video_info_simple(self, file_path: Path) -> Optional[Dict]:
        """Get basic video info without ffprobe (for faster scanning)"""
        try:
            # Try to get detailed info with ffprobe
            return self._get_video_info_detailed(file_path)
        except Exception as e:
            # Fallback to basic info if ffprobe fails
            print(f"Using basic info for {file_path.name}: {e}")
            return {
                'duration': 0,
                'width': 0,
                'height': 0,
                'codec': 'unknown'
            }

    def _get_video_info_detailed(self, file_path: Path) -> Optional[Dict]:
        """Get detailed video info using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', str(file_path)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode != 0:
                return None

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
                'width': video_stream.get('width', 0) if video_stream else 0,
                'height': video_stream.get('height', 0) if video_stream else 0,
                'codec': video_stream.get('codec_name', '') if video_stream else ''
            }

        except Exception as e:
            return None

    def get_video_info(self, filepath: Path) -> Dict:
        """Get video file information including embedded metadata"""
        try:
            # Get basic file info
            stat = filepath.stat()
            
            # Get video metadata using ffprobe
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', str(filepath)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                raise Exception(f"ffprobe failed: {result.stderr}")
            
            data = json.loads(result.stdout)
            format_info = data.get('format', {})
            
            # Find video stream
            video_stream = None
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                    break
            
            # Extract embedded metadata using ExifTool
            embedded_metadata = self.extract_embedded_metadata(filepath)
            
            return {
                'filepath': str(filepath),
                'filename': filepath.name,
                'filesize': stat.st_size,
                'file_type': 'video',
                'duration': float(format_info.get('duration', 0)),
                'width': video_stream.get('width', 0) if video_stream else 0,
                'height': video_stream.get('height', 0) if video_stream else 0,
                'codec': video_stream.get('codec_name', '') if video_stream else '',
                'created_date': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified_date': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                # Add embedded metadata
                'keywords': embedded_metadata['keywords'],
                'description': embedded_metadata['description'],
                'comment': embedded_metadata['comment'],
                'user_comment': embedded_metadata['user_comment']
            }
            
        except Exception as e:
            print(f"Error getting video info for {filepath}: {e}")
            return None
    
    def extract_embedded_metadata(self, filepath: Path) -> Dict:
        """Extract embedded metadata from video file using ExifTool"""
        try:
            cmd = ['exiftool', '-Keywords', '-Subject', '-Description', '-Comment', '-UserComment', '-json', str(filepath)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                import json
                metadata = json.loads(result.stdout)[0]
                
                # Extract keywords from various fields
                keywords = []
                
                # Get Keywords field (can be string or array)
                if 'Keywords' in metadata:
                    kw = metadata['Keywords']
                    if isinstance(kw, list):
                        keywords.extend(kw)
                    elif isinstance(kw, str):
                        keywords.append(kw)
                
                # Get Subject field as backup
                if 'Subject' in metadata and not keywords:
                    subj = metadata['Subject']
                    if isinstance(subj, list):
                        keywords.extend(subj)
                    elif isinstance(subj, str):
                        keywords.append(subj)
                
                return {
                    'keywords': list(set(keywords)),  # Remove duplicates
                    'description': metadata.get('Description', ''),
                    'comment': metadata.get('Comment', ''),
                    'user_comment': metadata.get('UserComment', '')
                }
            else:
                return {'keywords': [], 'description': '', 'comment': '', 'user_comment': ''}
                
        except Exception as e:
            print(f"Error extracting metadata from {filepath}: {e}")
            return {'keywords': [], 'description': '', 'comment': '', 'user_comment': ''}

