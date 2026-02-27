#!/usr/bin/env python3
"""
Gallery-based recognition system for academic buildings and people
"""

import json
import sqlite3
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

class GalleryManager:
    def __init__(self, gallery_dir: str = "data/gallery"):
        self.gallery_dir = Path(gallery_dir)
        self.db_path = self.gallery_dir / "gallery.db"
        self.config_path = self.gallery_dir / "gallery_config.json"
        self.cache_dir = Path("data/cache")
        
        # Ensure directories exist
        self.gallery_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.config = self.load_config()
        self.init_database()
    
    def load_config(self) -> Dict:
        """Load gallery configuration"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {
            "gallery_settings": {
                "confidence_threshold": 0.75,
                "max_matches_per_frame": 3,
                "embedding_model": "gemini-2.5-flash",
                "cache_embeddings": True
            },
            "categories": {}
        }
    
    def init_database(self):
        """Initialize SQLite database for gallery and cache"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Gallery items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gallery_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT NOT NULL,
                category TEXT NOT NULL,
                image_path TEXT UNIQUE NOT NULL,
                embedding BLOB,
                metadata TEXT,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Frame cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS frame_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_path TEXT NOT NULL,
                frame_path TEXT UNIQUE NOT NULL,
                embedding BLOB,
                analysis_result TEXT,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Gallery matches table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gallery_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                frame_path TEXT NOT NULL,
                gallery_item_id INTEGER,
                confidence REAL,
                match_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (gallery_item_id) REFERENCES gallery_items (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_gallery_item(self, category: str, label: str, image_path: str, metadata: Dict = None):
        """Add an item to the gallery"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute('''
            INSERT OR REPLACE INTO gallery_items 
            (label, category, image_path, metadata)
            VALUES (?, ?, ?, ?)
        ''', (label, category, image_path, metadata_json))
        
        conn.commit()
        conn.close()
    
    def get_gallery_items(self, category: Optional[str] = None) -> List[Dict]:
        """Get gallery items, optionally filtered by category"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if category:
            cursor.execute('SELECT * FROM gallery_items WHERE category = ?', (category,))
        else:
            cursor.execute('SELECT * FROM gallery_items')
        
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items
    
    def scan_gallery_directory(self):
        """Scan gallery directory and add new items to database"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        added_count = 0
        
        for category_dir in self.gallery_dir.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith('.'):
                continue
                
            category = category_dir.name
            
            for image_file in category_dir.iterdir():
                if image_file.suffix.lower() in image_extensions:
                    # Generate label from filename or use config
                    label = self.get_label_for_item(category, image_file.stem)
                    
                    try:
                        self.add_gallery_item(category, label, str(image_file))
                        added_count += 1
                        logging.info(f"Added gallery item: {category}/{label}")
                    except Exception as e:
                        logging.warning(f"Failed to add {image_file}: {e}")
        
        return added_count
    
    def get_label_for_item(self, category: str, filename: str) -> str:
        """Get appropriate label for gallery item based on config or filename"""
        # Check config first
        categories = self.config.get("categories", {})
        
        for cat_name, cat_data in categories.items():
            if cat_name == category:
                for item_key, item_data in cat_data.items():
                    if item_key.lower() in filename.lower():
                        return item_data.get("label", filename)
        
        # Fallback to cleaned filename
        return filename.replace("_", " ").replace("-", " ").title()
    
    def get_training_examples_for_gemini(self, max_per_category: int = 3) -> List[Dict[str, str]]:
        """Get training examples in format expected by Gemini tagger"""
        items = self.get_gallery_items()
        examples = []
        category_counts = {}
        
        for item in items:
            category = item['category']
            if category_counts.get(category, 0) >= max_per_category:
                continue
                
            if Path(item['image_path']).exists():
                examples.append({
                    'image_path': item['image_path'],
                    'label': item['label']
                })
                category_counts[category] = category_counts.get(category, 0) + 1
        
        return examples
    
    def cache_frame_analysis(self, video_path: str, frame_path: str, analysis_result: Dict):
        """Cache frame analysis result"""
        if not self.config["gallery_settings"].get("cache_embeddings", True):
            return
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO frame_cache 
            (video_path, frame_path, analysis_result)
            VALUES (?, ?, ?)
        ''', (video_path, frame_path, json.dumps(analysis_result)))
        
        conn.commit()
        conn.close()
    
    def get_cached_frame_analysis(self, frame_path: str) -> Optional[Dict]:
        """Get cached frame analysis if available"""
        if not self.config["gallery_settings"].get("cache_embeddings", True):
            return None
            
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT analysis_result FROM frame_cache WHERE frame_path = ?', (frame_path,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return json.loads(row['analysis_result'])
        return None
    
    def clear_cache(self):
        """Clear frame analysis cache"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM frame_cache')
        cursor.execute('DELETE FROM gallery_matches')
        conn.commit()
        conn.close()
        logging.info("Cleared gallery cache")
    
    def get_statistics(self) -> Dict:
        """Get gallery statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count items by category
        cursor.execute('SELECT category, COUNT(*) FROM gallery_items GROUP BY category')
        category_counts = dict(cursor.fetchall())
        
        # Count cached frames
        cursor.execute('SELECT COUNT(*) FROM frame_cache')
        cached_frames = cursor.fetchone()[0]
        
        # Count matches
        cursor.execute('SELECT COUNT(*) FROM gallery_matches')
        total_matches = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "gallery_items": category_counts,
            "cached_frames": cached_frames,
            "total_matches": total_matches
        }
