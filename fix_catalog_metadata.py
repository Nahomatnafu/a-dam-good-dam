#!/usr/bin/env python3
"""
Fix catalog metadata issues - file sizes and keywords display
"""

from src.database import CatalogDatabase
from src.file_scanner import FileScanner
from pathlib import Path

def fix_catalog_metadata():
    """Fix file sizes and metadata in the catalog"""
    
    # Find the latest catalog
    catalog_dir = Path('catalogs')
    if not catalog_dir.exists():
        print("No catalogs directory found")
        return
    
    db_files = list(catalog_dir.glob('*.db'))
    if not db_files:
        print("No catalog databases found")
        return
    
    latest_db = max(db_files, key=lambda f: f.stat().st_mtime)
    print(f"Using catalog: {latest_db.name}")
    
    db = CatalogDatabase(latest_db)
    scanner = FileScanner()
    
    # Get all files from database
    files = db.search_files('')
    print(f"Found {len(files)} files in database")
    
    updated_count = 0
    for i, file_info in enumerate(files):
        filepath = Path(file_info['filepath'])
        print(f"\n{i+1}. Checking: {filepath.name}")
        
        if not filepath.exists():
            print(f"   ❌ File not found: {filepath}")
            continue
        
        # Get current info from database
        current_size = file_info.get('filesize')
        current_keywords = file_info.get('keywords')
        
        print(f"   Current size: {current_size}")
        print(f"   Current keywords: {current_keywords}")
        
        # Get fresh file info
        fresh_info = scanner._extract_file_info(filepath)
        if fresh_info:
            fresh_size = fresh_info.get('filesize', 0)
            print(f"   Fresh size: {fresh_size} bytes ({fresh_size / (1024*1024):.1f} MB)")
            
            # Update database if size is missing or different
            if current_size is None or current_size != fresh_size:
                print(f"   ✅ Updating file info in database")
                db.add_file(fresh_info)
                updated_count += 1
            else:
                print(f"   ✓ File info is current")
        else:
            print(f"   ❌ Could not get fresh file info")
    
    print(f"\n🎉 Updated {updated_count} files")
    
    # Show final status
    print("\n📊 Final database status:")
    updated_files = db.search_files('')
    for file_info in updated_files:
        name = file_info['filename']
        size = file_info.get('filesize', 0)
        size_mb = size / (1024*1024) if size else 0
        keywords = file_info.get('keywords', 'None')
        print(f"   {name}: {size_mb:.1f} MB, Keywords: {keywords}")

if __name__ == "__main__":
    fix_catalog_metadata()
