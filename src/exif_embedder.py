#!/usr/bin/env python3
"""
ExifTool integration for embedding metadata into video files
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List
import xml.etree.ElementTree as ET

class ExifEmbedder:
    def __init__(self):
        self.exiftool_available = self.check_exiftool()
    
    def check_exiftool(self) -> bool:
        """Check if ExifTool is available"""
        try:
            result = subprocess.run(['exiftool', '-ver'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def parse_xml_tags(self, xml_path: Path) -> Dict:
        """Parse XML tags file and extract metadata"""
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        all_labels = []
        all_text = []
        total_faces = 0
        
        # Handle the new VideoTags format
        for frame in root.findall('Frame'):
            # Collect labels
            labels_elem = frame.find('Labels')
            if labels_elem is not None:
                for label in labels_elem.findall('Label'):
                    confidence = float(label.get('confidence', 0))
                    if confidence > 0.7:  # Only high-confidence labels
                        all_labels.append(label.text)
            
            # Collect text (if exists)
            text_elem = frame.find('Text')
            if text_elem is not None and text_elem.text:
                all_text.extend(text_elem.text.split(' | '))
            
            # Count faces
            faces_elem = frame.find('Faces')
            if faces_elem is not None:
                total_faces += int(faces_elem.get('count', 0))
        
        # Deduplicate and sort by frequency
        unique_labels = list(set(all_labels))
        unique_text = list(set(all_text))
        
        return {
            'keywords': unique_labels[:20],  # Top 20 labels
            'description': f"Auto-generated tags from {len(root.findall('Frame'))} frames",
            'subject': ', '.join(unique_labels[:5]),
            'comment': f"Contains text: {'; '.join(unique_text[:10])}" if unique_text else "",
            'faces_detected': total_faces > 0
        }
    
    def embed_metadata(self, video_path: Path, metadata: Dict) -> bool:
        """Embed metadata into video file using ExifTool"""
        if not self.exiftool_available:
            raise Exception("ExifTool not available")
        
        cmd = ['exiftool', '-overwrite_original']
        
        # Add metadata fields
        if metadata.get('keywords'):
            keywords_str = ';'.join(metadata['keywords'])
            cmd.extend([f'-Keywords={keywords_str}'])
        
        if metadata.get('description'):
            cmd.extend([f'-Description={metadata["description"]}'])
        
        if metadata.get('subject'):
            cmd.extend([f'-Subject={metadata["subject"]}'])
        
        if metadata.get('comment'):
            cmd.extend([f'-Comment={metadata["comment"]}'])
        
        # Add custom tags
        cmd.extend([f'-UserComment=AI_TAGGED'])
        if metadata.get('faces_detected'):
            cmd.extend([f'-PersonInImage=Detected'])
        
        cmd.append(str(video_path))
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

