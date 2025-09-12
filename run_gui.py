#!/usr/bin/env python3
"""
Launch the Stills Exporter GUI
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    import tkinter as tk
    from stills_exporter_gui import StillsExporterGUI
    
    def main():
        print("🚀 Starting Stills Exporter GUI...")
        
        root = tk.Tk()
        app = StillsExporterGUI(root)
        
        print("✅ GUI loaded successfully!")
        print("💡 Configure your settings and click 'Start Export'")
        
        root.mainloop()
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're in the correct directory and have all dependencies installed")
except Exception as e:
    print(f"❌ Error starting GUI: {e}")