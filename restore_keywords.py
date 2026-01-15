#!/usr/bin/env python3
"""
Restore keywords that were lost during file updates
"""

from src.database import CatalogDatabase
from pathlib import Path

def restore_keywords():
    """Restore keywords based on folder structure and previous patterns"""
    
    # Find the latest catalog
    catalog_dir = Path('catalogs')
    db_files = list(catalog_dir.glob('*.db'))
    latest_db = max(db_files, key=lambda f: f.stat().st_mtime)
    print(f"Using catalog: {latest_db.name}")
    
    db = CatalogDatabase(latest_db)
    
    # Get all files
    files = db.search_files('')
    print(f"Found {len(files)} files")
    
    # Restore keywords based on patterns
    for file_info in files:
        filename = file_info['filename']
        filepath = Path(file_info['filepath'])
        file_id = db.get_file_id(file_info['filepath'])
        
        if not file_id:
            print(f"❌ Could not find file ID for {filename}")
            continue
        
        print(f"\n📁 Processing: {filename}")
        
        # Clear existing keywords
        db.clear_file_keywords(file_id)
        
        # Generate keywords based on filename and folder
        keywords = []
        
        # Folder-based keywords
        folder_name = filepath.parent.name.lower()
        if 'fridaytest' in folder_name or 'friday' in folder_name:
            keywords.extend(['test', 'friday', 'sample'])
        
        # Filename-based keywords
        filename_lower = filename.lower()
        if 'fridaytest_2' in filename_lower or 'fridaytest_3' in filename_lower:
            keywords.extend(['scene', 'outdoor', 'person'])
        
        # Add file type
        keywords.append('video')
        
        # Add generic keywords
        if 'clip' in filename_lower or 'test' in filename_lower:
            keywords.append('clip')
        
        # Remove duplicates
        keywords = list(set(keywords))
        
        if keywords:
            print(f"   Adding keywords: {', '.join(keywords)}")
            db.add_keywords_to_file(file_id, keywords, source='restored')
        else:
            print(f"   No keywords to add")
    
    # Show final status
    print("\n📊 Final status:")
    updated_files = db.search_files('')
    for file_info in updated_files:
        name = file_info['filename']
        keywords = file_info.get('keywords', 'None')
        print(f"   {name}: {keywords}")

if __name__ == "__main__":
    restore_keywords()
