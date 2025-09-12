#!/usr/bin/env python3
"""
Main launcher for Stills Exporter GUI
This script launches the application from the project root directory.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from stills_exporter_gui import main
    main()
except ImportError as e:
    print(f"Error importing GUI module: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)
except Exception as e:
    print(f"Error starting application: {e}")
    sys.exit(1)
