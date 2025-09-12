#!/usr/bin/env python3
"""
Setup script for Stills Exporter
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="stills-exporter",
    version="1.0.0",
    author="Stills Exporter Team",
    description="A cross-platform GUI application for extracting frames from video files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/stills-exporter",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Video",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies - uses only Python standard library
    ],
    extras_require={
        "dev": [
            "pyinstaller>=5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "stills-exporter=stills_exporter_gui:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
