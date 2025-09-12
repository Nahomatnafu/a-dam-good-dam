#!/usr/bin/env python3
"""
Install Google Cloud Vision API
"""

import subprocess
import sys

def install_google_vision():
    """Install Google Cloud Vision"""
    print("📦 Installing Google Cloud Vision API...")
    
    try:
        # Try the main package
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', 
            'google-cloud-vision', '--user'
        ])
        print("✅ Google Cloud Vision installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Google Cloud Vision")
        return False

def test_import():
    """Test if the import works"""
    try:
        from google.cloud import vision
        print("✅ Google Cloud Vision import successful!")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Installing Google Cloud Vision")
    print("=" * 40)
    
    success = install_google_vision()
    if success:
        print("\n🧪 Testing import...")
        test_import()
    
    print("\n📋 Next steps:")
    print("1. Get Google Cloud credentials JSON file")
    print("2. Test with: python debug_ai_issue.py")
    print("3. Run GUI again: python run_gui.py")