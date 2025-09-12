#!/usr/bin/env python3
"""
Setup script for AI features
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing Google Cloud Vision...")
    
    # Try different installation methods
    packages_to_try = [
        'google-cloud-vision',
        'google-cloud-vision==3.4.0',
        'google-cloud-vision>=3.0.0'
    ]
    
    for package in packages_to_try:
        try:
            print(f"Trying: {package}")
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 
                package, '--user', '--no-cache-dir'
            ])
            print(f"✅ Successfully installed {package}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}")
            continue
    
    print("❌ All installation attempts failed")
    print("💡 Try manually: pip install google-cloud-vision")
    return False

def check_exiftool():
    """Check ExifTool installation"""
    try:
        result = subprocess.run(['exiftool', '-ver'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ ExifTool is available (version {version})")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ ExifTool not found")
    print("📥 Quick install for Windows:")
    print("   1. Download from: https://exiftool.org/")
    print("   2. Extract exiftool(-k).exe to C:\\Windows\\System32\\")
    print("   3. Rename to exiftool.exe")
    print("   4. Or add to PATH")
    return False

def test_vision_import():
    """Test if Vision API can be imported"""
    try:
        from google.cloud import vision
        print("✅ Google Cloud Vision import successful")
        return True
    except ImportError as e:
        print(f"❌ Google Cloud Vision import failed: {e}")
        return False

def create_test_credentials():
    """Create a dummy credentials file for testing"""
    test_creds = {
        "type": "service_account",
        "project_id": "your-project-id",
        "private_key_id": "key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n",
        "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
        "client_id": "client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token"
    }
    
    import json
    test_path = "test_credentials.json"
    with open(test_path, 'w') as f:
        json.dump(test_creds, f, indent=2)
    
    print(f"📝 Created template credentials file: {test_path}")
    print("   Replace with your actual Google Cloud credentials")

def setup_credentials():
    """Guide user through credentials setup"""
    print("\n📋 Google Cloud Vision Setup Guide:")
    print("=" * 50)
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create a new project or select existing one")
    print("3. Enable the Vision API:")
    print("   - Go to APIs & Services > Library")
    print("   - Search for 'Vision API'")
    print("   - Click Enable")
    print("4. Create service account credentials:")
    print("   - Go to APIs & Services > Credentials")
    print("   - Click 'Create Credentials' > 'Service Account'")
    print("   - Fill in details and create")
    print("   - Click on the service account")
    print("   - Go to 'Keys' tab")
    print("   - Click 'Add Key' > 'Create new key' > JSON")
    print("   - Download the JSON file")
    print("5. In the app, browse to select this JSON file")
    print("=" * 50)
    
    create_test_credentials()

if __name__ == "__main__":
    print("🚀 Setting up AI features for Stills Exporter...")
    print("=" * 60)
    
    # Install requirements
    vision_installed = install_requirements()
    
    # Test import
    vision_working = False
    if vision_installed:
        vision_working = test_vision_import()
    
    # Check ExifTool
    exiftool_ok = check_exiftool()
    
    # Setup guide
    setup_credentials()
    
    print("\n" + "=" * 60)
    print("📊 Setup Summary:")
    print(f"   Google Vision API: {'✅ Ready' if vision_working else '❌ Not Ready'}")
    print(f"   ExifTool: {'✅ Ready' if exiftool_ok else '❌ Not Ready'}")
    
    if vision_working and exiftool_ok:
        print("\n🎉 All AI features are ready!")
    elif vision_working:
        print("\n⚠️  AI tagging ready, but metadata embedding unavailable")
    else:
        print("\n❌ AI features not ready")
    
    print("\n🚀 Next steps:")
    print("1. Run: python test_ai_features.py")
    print("2. Run: python src/stills_exporter_gui.py")
    print("3. Test with existing stills in C:/Users/15073/Videos/NeoFinder_Test/Stills")

