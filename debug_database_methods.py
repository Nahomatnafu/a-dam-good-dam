#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.append('src')

from database import CatalogDatabase

def check_database_methods():
    # Create test database
    db_path = Path("catalogs/debug_test.db")
    db_path.parent.mkdir(exist_ok=True)
    
    db = CatalogDatabase(db_path)
    
    print("Available CatalogDatabase methods:")
    methods = [method for method in dir(db) if not method.startstart('_')]
    for method in methods:
        print(f"  - {method}")
    
    # Test search_files method
    try:
        result = db.search_files("")
        print(f"\nsearch_files('') returned: {type(result)} - {result}")
    except Exception as e:
        print(f"\nsearch_files('') error: {e}")
    
    # Check if there are actually files in the database
    cursor = db.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM files")
    count = cursor.fetchone()[0]
    print(f"\nDirect database query - Total files: {count}")
    
    if count > 0:
        cursor.execute("SELECT id, filename, filepath FROM files LIMIT 5")
        files = cursor.fetchall()
        print("Sample files:")
        for file in files:
            print(f"  ID: {file[0]}, Name: {file[1]}, Path: {file[2]}")

if __name__ == "__main__":
    check_database_methods()
