#!/usr/bin/env python3
"""
Test Google Cloud Vision API with real credentials
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def find_credentials():
    """Find credentials file"""
    possible_files = [
        "google-vision-credentials.json",
        "credentials.json", 
        "service-account.json",
        "vision-credentials.json"
    ]
    
    for filename in possible_files:
        if Path(filename).exists():
            return filename
    return None

def test_vision_api():
    """Test Google Vision API"""
    print("🧪 Testing Google Cloud Vision API")
    print("=" * 50)
    
    # Find credentials
    cred_file = find_credentials()
    if not cred_file:
        print("❌ No credentials file found!")
        print("Run: python setup_google_cloud.py")
        return False
    
    print(f"📁 Using credentials: {cred_file}")
    
    try:
        from vision_tagger import VisionTagger, VISION_AVAILABLE
        
        if not VISION_AVAILABLE:
            print("❌ Google Vision library not installed")
            print("Run: pip install google-cloud-vision")
            return False
        
        print("✅ Google Vision library available")
        
        # Test with credentials
        tagger = VisionTagger(cred_file)
        
        if tagger.mock_mode:
            print("⚠️ Still in mock mode - credentials may be invalid")
            return False
        else:
            print("✅ Google Vision client initialized successfully!")
            print("🎉 Ready for real AI analysis!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_vision_api()
    
    if success:
        print("\n🚀 Next steps:")
        print("1. Run: python run_gui.py")
        print("2. Enable AI Tagging in the GUI")
        print("3. Process your soccer videos!")
        print("4. Get real AI analysis instead of mock data!")
    else:
        print("\n🔧 Troubleshooting:")
        print("1. Check your credentials file")
        print("2. Verify Google Cloud project setup")
        print("3. Make sure Vision API is enabled")