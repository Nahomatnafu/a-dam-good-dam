import subprocess
from pathlib import Path

class ThumbnailGenerator:
    def __init__(self, thumbnail_dir="thumbnails"):
        self.thumbnail_dir = Path(thumbnail_dir)
        self.thumbnail_dir.mkdir(exist_ok=True)
    
    def generate_thumbnail(self, video_path, size="160x120"):
        """Generate first frame thumbnail"""
        video_path = Path(video_path)
        thumb_path = self.thumbnail_dir / f"{video_path.stem}.jpg"
        
        if thumb_path.exists():
            return thumb_path
        
        cmd = [
            'ffmpeg', '-i', str(video_path), 
            '-ss', '00:00:01', '-frames:v', '1',
            '-s', size, str(thumb_path)
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            return thumb_path if thumb_path.exists() else None
        except:
            return None