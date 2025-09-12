#!/usr/bin/env python3
"""
Simple test script to verify the Stills Exporter functionality
"""

import sys
import subprocess
import shutil
from pathlib import Path

def test_ffmpeg():
    """Test if FFmpeg is available"""
    print("Testing FFmpeg availability...")
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ FFmpeg found: {version_line}")
            return True
        else:
            print("❌ FFmpeg command failed")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        print("❌ FFmpeg command timed out")
        return False

def test_python_modules():
    """Test if required Python modules are available"""
    print("\nTesting Python modules...")
    
    modules = ['tkinter', 'threading', 'subprocess', 'pathlib', 'json', 'concurrent.futures']
    all_good = True
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} not available")
            all_good = False
    
    return all_good

def test_gui_import():
    """Test if the GUI module can be imported"""
    print("\nTesting GUI module import...")
    try:
        # Determine src directory path relative to this script
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        src_path = project_root / "src"

        if not src_path.exists():
            print(f"❌ Source directory not found: {src_path}")
            return False

        sys.path.insert(0, str(src_path))

        # Try to import the main class
        from stills_exporter_gui import StillsExporterGUI
        print("✅ GUI module imports successfully")
        return True
    except ImportError as e:
        print(f"❌ GUI module import failed: {e}")
        print(f"Source path: {src_path}")
        return False
    except Exception as e:
        print(f"❌ GUI module error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Stills Exporter Test Suite")
    print("=" * 40)
    
    tests = [
        ("FFmpeg", test_ffmpeg),
        ("Python Modules", test_python_modules),
        ("GUI Import", test_gui_import)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All tests passed! The application should work correctly.")
        print("\nNext steps:")
        print("1. Run 'python stills_exporter_gui.py' to start the GUI")
        print("2. Or run 'python build_app.py' to create a standalone executable")
    else:
        print("⚠️  Some tests failed. Please address the issues above.")
        print("\nCommon solutions:")
        print("- Install FFmpeg: https://ffmpeg.org/download.html")
        print("- Ensure Python 3.7+ is installed")
        print("- Install missing modules: pip install -r requirements.txt")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
