#!/usr/bin/env python3
import os

def create_test_structure():
    base_path = "C:/Users/nahom/Videos/NeoFinder_Test"
    
    os.makedirs(f"{base_path}/Footages", exist_ok=True)
    os.makedirs(f"{base_path}/Stills", exist_ok=True)
    
    print(f"✅ Created test structure at {base_path}")
    print("   📁 Footages/ - Put your video files here")
    print("   📁 Stills/ - Extracted frames will go here")

if __name__ == "__main__":
    create_test_structure()
