#!/usr/bin/env python3
"""
Launcher for Stills Exporter GUI with AI Tagging
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import and run the GUI
from stills_exporter_gui import main

if __name__ == "__main__":
    print("=" * 60)
    print("Stills Exporter with AI Tagging")
    print("=" * 60)
    print("\nFeatures:")
    print("  ✓ Video frame extraction")
    print("  ✓ AI tagging with LangChain + Gemini")
    print("  ✓ Few-shot learning (President Inch recognition)")
    print("  ✓ Metadata embedding")
    print("\nStarting GUI...")
    print("=" * 60)
    
    main()

