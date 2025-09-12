#!/usr/bin/env python3
"""
Setup script for AI features
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'google-cloud-vision'])
        print("✓ Google Cloud Vision installed")
    except subprocess.CalledProcessError:
        print("✗ Failed to install Google Cloud Vision")
        return False
    return True

def check_exiftool():
    """Check ExifTool installation"""
    try:
        result = subprocess.run(['exiftool', '-ver'], capture_output=True)
        if result.returncode == 0:
            print("✓ ExifTool is available")
            return True
    except FileNotFoundError:
        pass
    
    print("✗ ExifTool not found")
    print("Install from: https://exiftool.org/")
    return False

def setup_credentials():
    """Guide user through credentials setup"""
    print("\n📋 Google Cloud Vision Setup:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create a new project or select existing")
    print("3. Enable Vision API")
    print("4. Create service account credentials")
    print("5. Download JSON key file")
    print("6. Use the JSON file path in the application")

if __name__ == "__main__":
    print("🚀 Setting up AI features...")
    
    vision_ok = install_requirements()
    exiftool_ok = check_exiftool()
    
    if vision_ok:
        setup_credentials()
    
    print(f"\n📊 Setup Status:")
    print(f"   Vision API: {'✓' if vision_ok else '✗'}")
    print(f"   ExifTool: {'✓' if exiftool_ok else '✗'}")