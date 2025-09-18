#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.append('src')

from database import CatalogDatabase

def check_real_catalog():
    # Find the actual catalog you created
    catalogs_dir = Path("catalogs")
    if not catalogs_dir.exists():
        print("No catalogs directory found")
        return
    
    catalog_files = list(catalogs_dir.glob("*.db"))
    print(f"Found catalog files: {[f.name for f in catalog_files]}")
    
    for catalog_file in catalog_files:
        print(f"\n📊 Checking catalog: {catalog_file.name}")
        db = CatalogDatabase(catalog_file)
        
        # Direct database query
        cursor = db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM files")
        count = cursor.fetchone()[0]
        print(f"  Total files: {count}")
        
        if count > 0:
            cursor.execute("SELECT id, filename, filepath FROM files LIMIT 5")
            files = cursor.fetchall()
            print("  Sample files:")
            for file in files:
                print(f"    ID: {file[0]}, Name: {file[1]}")
        
        # Test search_files
        result = db.search_files("")
        print(f"  search_files('') returned: {len(result)} files")
        
        db.close()

if __name__ == "__main__":
    check_real_catalog()