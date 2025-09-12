#!/usr/bin/env python3
import subprocess
import sys
import os

def test_setup():
    print("=== Python Setup Test ===")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    print("\n=== FFmpeg Test ===")
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ FFmpeg is working!")
            first_line = result.stdout.split('\n')[0]
            print(f"   {first_line}")
        else:
            print("❌ FFmpeg failed")
    except FileNotFoundError:
        print("❌ FFmpeg not found in PATH")
        print("   Add C:\\ffmpeg\\bin to your PATH variable")
    except Exception as e:
        print(f"❌ FFmpeg error: {e}")
    
    print("\n=== GUI Dependencies Test ===")
    try:
        import tkinter
        print("✅ tkinter is available")
    except ImportError:
        print("❌ tkinter not available")
    
    print("\n=== Project Files Test ===")
    required_files = ['run.py', 'src/stills_exporter_gui.py']
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} found")
        else:
            print(f"❌ {file} missing")

if __name__ == "__main__":
    test_setup()