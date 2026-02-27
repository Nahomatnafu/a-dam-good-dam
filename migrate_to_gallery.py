#!/usr/bin/env python3
"""
Migration script to move training images to gallery structure
and initialize gallery-based recognition system
"""

import os
import shutil
import json
import sqlite3
from pathlib import Path
from typing import Dict, List

def create_gallery_structure():
    """Create the new data directory structure"""
    base_dir = Path("data")
    
    # Create directories
    dirs = [
        "data/gallery",
        "data/cache/embeddings", 
        "data/cache/frames",
        "src/ai",
        "src/pipeline"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created {dir_path}")
    
    return base_dir

def migrate_president_inch_images():
    """Migrate existing President Inch images to gallery structure"""
    source_dir = Path("training_images/president_inch")
    target_dir = Path("data/gallery/president_inch")
    
    if not source_dir.exists():
        print("⚠️ No President Inch images found to migrate")
        return []
    
    target_dir.mkdir(parents=True, exist_ok=True)
    
    migrated_files = []
    for img_file in source_dir.glob("*.jpg"):
        target_file = target_dir / img_file.name
        shutil.copy2(img_file, target_file)
        migrated_files.append(str(target_file))
        print(f"✓ Migrated {img_file.name}")
    
    return migrated_files

def create_gallery_database():
    """Create SQLite database for gallery embeddings and metadata"""
    db_path = Path("data/gallery/gallery.db")
    
    conn = sqlite3.connect(db_path)
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
    print(f"✓ Created gallery database: {db_path}")

def create_sample_gallery_config():
    """Create sample gallery configuration"""
    config = {
        "gallery_settings": {
            "confidence_threshold": 0.75,
            "max_matches_per_frame": 3,
            "embedding_model": "gemini-2.5-flash",
            "cache_embeddings": True
        },
        "categories": {
            "people": {
                "president_inch": {
                    "label": "President Inch",
                    "description": "University President Edward Inch"
                }
            },
            "buildings": {
                "admin_building": {
                    "label": "Administration Building", 
                    "description": "Main administrative building"
                },
                "library": {
                    "label": "Library",
                    "description": "University library building"
                },
                "student_center": {
                    "label": "Student Center",
                    "description": "Student activities center"
                }
            },
            "spaces": {
                "lecture_hall_a": {
                    "label": "Lecture Hall A",
                    "description": "Large lecture hall in academic building"
                },
                "library_atrium": {
                    "label": "Library Atrium", 
                    "description": "Main entrance area of library"
                }
            }
        }
    }
    
    config_path = Path("data/gallery/gallery_config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Created gallery config: {config_path}")
    return config

def update_gitignore():
    """Add data directory to .gitignore"""
    gitignore_path = Path(".gitignore")
    
    gitignore_content = """
# Gallery and training data (keep out of repo)
/data/gallery/
/data/cache/
training_images/

# Keep structure files
!/data/gallery/.gitkeep
!/data/cache/.gitkeep
"""
    
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            existing = f.read()
        if "/data/gallery/" not in existing:
            with open(gitignore_path, 'a') as f:
                f.write(gitignore_content)
            print("✓ Updated .gitignore")
    else:
        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content)
        print("✓ Created .gitignore")

def main():
    print("=" * 60)
    print("Gallery Migration Script")
    print("=" * 60)
    
    # 1. Create directory structure
    print("\n1. Creating gallery structure...")
    create_gallery_structure()
    
    # 2. Migrate existing images
    print("\n2. Migrating President Inch images...")
    migrated_files = migrate_president_inch_images()
    
    # 3. Create database
    print("\n3. Creating gallery database...")
    create_gallery_database()
    
    # 4. Create config
    print("\n4. Creating gallery configuration...")
    config = create_sample_gallery_config()
    
    # 5. Update gitignore
    print("\n5. Updating .gitignore...")
    update_gitignore()
    
    # 6. Create .gitkeep files
    for keep_dir in ["data/gallery", "data/cache"]:
        keep_file = Path(keep_dir) / ".gitkeep"
        keep_file.touch()
    
    print("\n" + "=" * 60)
    print("Migration Complete!")
    print("=" * 60)
    print(f"✓ Migrated {len(migrated_files)} President Inch images")
    print("✓ Created gallery database and configuration")
    print("✓ Set up caching structure")
    print("\nNext steps:")
    print("1. Add building images to data/gallery/<category>/")
    print("2. Run: python build_gallery_embeddings.py")
    print("3. Test with: python test_gallery_recognition.py")

if __name__ == "__main__":
    main()
