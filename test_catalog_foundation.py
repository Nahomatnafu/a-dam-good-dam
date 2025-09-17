#!/usr/bin/env python3
from pathlib import Path
from src.database import CatalogDatabase
from src.file_scanner import FileScanner

def test_catalog_foundation():
    print("🧪 Testing Catalog Foundation")
    print("=" * 50)
    
    # Create test catalog
    catalog_path = Path("catalogs/test_catalog.db")
    catalog_path.parent.mkdir(exist_ok=True)
    
    db = CatalogDatabase(catalog_path)
    scanner = FileScanner()
    
    # Test directory scanning
    test_dir = Path("C:/Users/15073/Videos/NeoFinder_Test/Proxies")
    
    if not test_dir.exists():
        print(f"❌ Test directory not found: {test_dir}")
        return
    
    print(f"📁 Scanning directory: {test_dir}")
    files = scanner.scan_directory(test_dir)
    print(f"✅ Found {len(files)} media files")
    
    # Add files to catalog
    print("\n📊 Adding files to catalog...")
    for file_info in files:
        file_id = db.add_file(file_info)
        print(f"  Added: {file_info['filename']} (ID: {file_id})")
        
        # Add some test keywords
        test_keywords = ['proxy', 'test', file_info['file_type']]
        db.add_keywords_to_file(file_id, test_keywords, source='manual')
    
    # Test search
    print("\n🔍 Testing search...")
    results = db.search_files(query="Clip")
    print(f"Search for 'Clip': {len(results)} results")
    
    for result in results[:3]:  # Show first 3
        print(f"  - {result['filename']}: {result['keywords']}")
    
    # Test keyword listing
    print("\n🏷️ All keywords:")
    keywords = db.get_all_keywords()
    for kw in keywords:
        print(f"  - {kw['keyword']}: {kw['usage_count']} files")
    
    db.close()
    print(f"\n✅ Catalog saved to: {catalog_path}")

if __name__ == "__main__":
    test_catalog_foundation()