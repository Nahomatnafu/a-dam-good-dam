#!/usr/bin/env python3
"""
Guide for setting up Google Cloud Vision API credentials
"""

import json
import os
from pathlib import Path

def create_project_guide():
    """Show step-by-step Google Cloud setup"""
    print("🌐 Google Cloud Vision API Setup Guide")
    print("=" * 60)
    print()
    print("📋 STEP 1: Create Google Cloud Project")
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Click 'Select a project' → 'New Project'")
    print("3. Enter project name (e.g., 'stills-analyzer')")
    print("4. Click 'Create'")
    print()
    
    print("📋 STEP 2: Enable Vision API")
    print("1. In your project, go to 'APIs & Services' → 'Library'")
    print("2. Search for 'Cloud Vision API'")
    print("3. Click on it and press 'Enable'")
    print("4. Wait for it to be enabled")
    print()
    
    print("📋 STEP 3: Create Service Account")
    print("1. Go to 'APIs & Services' → 'Credentials'")
    print("2. Click 'Create Credentials' → 'Service Account'")
    print("3. Enter name: 'vision-analyzer'")
    print("4. Click 'Create and Continue'")
    print("5. For role, select 'Cloud Vision AI Service Agent'")
    print("6. Click 'Continue' → 'Done'")
    print()
    
    print("📋 STEP 4: Download JSON Key")
    print("1. Click on the service account you just created")
    print("2. Go to 'Keys' tab")
    print("3. Click 'Add Key' → 'Create new key'")
    print("4. Select 'JSON' and click 'Create'")
    print("5. Save the downloaded JSON file to this project folder")
    print("6. Rename it to something like 'google-vision-credentials.json'")
    print()
    
    print("📋 STEP 5: Test Setup")
    print("1. Place the JSON file in this project directory")
    print("2. Run: python test_google_vision.py")
    print("3. If successful, run the GUI with real AI analysis!")

def test_credentials_file():
    """Test if credentials file exists and is valid"""
    print("\n🔍 Looking for credentials file...")
    
    # Common credential file names
    possible_files = [
        "google-vision-credentials.json",
        "credentials.json",
        "service-account.json",
        "vision-credentials.json"
    ]
    
    found_files = []
    for filename in possible_files:
        if Path(filename).exists():
            found_files.append(filename)
    
    if found_files:
        print(f"✅ Found credential files: {found_files}")
        
        # Test the first one
        cred_file = found_files[0]
        try:
            with open(cred_file, 'r') as f:
                creds = json.load(f)
            
            required_fields = ['type', 'project_id', 'private_key', 'client_email']
            missing = [field for field in required_fields if field not in creds]
            
            if missing:
                print(f"⚠️ Credentials file missing fields: {missing}")
            else:
                print(f"✅ Credentials file looks valid: {cred_file}")
                return cred_file
                
        except Exception as e:
            print(f"❌ Error reading credentials: {e}")
    else:
        print("❌ No credentials file found")
        print("Expected files: " + ", ".join(possible_files))
    
    return None

if __name__ == "__main__":
    create_project_guide()
    
    input("\nPress Enter after you've downloaded the credentials JSON file...")
    
    cred_file = test_credentials_file()
    
    if cred_file:
        print(f"\n🎉 Ready to test! Your credentials file: {cred_file}")
        print("Next steps:")
        print("1. Run: python test_google_vision.py")
        print("2. If successful, run: python run_gui.py")
    else:
        print("\n📁 Place your Google Cloud credentials JSON file in this directory")
        print("Then run this script again to verify")