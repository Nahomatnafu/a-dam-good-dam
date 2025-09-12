#!/usr/bin/env python3
"""
Google Vision API integration for automatic image tagging
"""

import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Optional
import logging

try:
    from google.cloud import vision
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False

class VisionTagger:
    def __init__(self, credentials_path: Optional[str] = None):
        self.client = None
        self.mock_mode = False
        
        if VISION_AVAILABLE:
            try:
                self.setup_client(credentials_path)
            except Exception as e:
                print(f"⚠️ Vision client failed, using mock mode: {e}")
                self.mock_mode = True
        else:
            print("📝 Using mock analysis (Google Vision not available)")
            self.mock_mode = True
    
    def setup_client(self, credentials_path: Optional[str] = None):
        """Initialize Google Vision client"""
        if not VISION_AVAILABLE:
            raise ImportError("Google Cloud Vision library not installed. Run: pip install google-cloud-vision")
            
        if credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            
        try:
            self.client = vision.ImageAnnotatorClient()
        except Exception as e:
            raise Exception(f"Failed to initialize Vision client: {e}")
    
    def analyze_image(self, image_path: Path) -> Dict:
        """Analyze single image and return tags"""
        if self.mock_mode:
            return self.mock_analyze_image(image_path)
        
        try:
            # Real Google Vision analysis
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
                
            image = vision.Image(content=content)
            
            # Get labels, text, faces...
            labels_response = self.client.label_detection(image=image)
            labels = labels_response.label_annotations
            
            text_response = self.client.text_detection(image=image)
            texts = text_response.text_annotations
            
            faces_response = self.client.face_detection(image=image)
            faces = faces_response.face_annotations
            
            return {
                'labels': [{'description': label.description, 'score': label.score} 
                          for label in labels],
                'text': [text.description for text in texts] if texts else [],
                'faces_count': len(faces),
                'image_path': str(image_path)
            }
        except Exception as e:
            # If billing error or any API error, fall back to mock mode
            if "BILLING_DISABLED" in str(e) or "403" in str(e):
                print(f"⚠️ Billing not enabled, switching to mock mode for {image_path.name}")
                self.mock_mode = True
                return self.mock_analyze_image(image_path)
            else:
                raise e
    
    def mock_analyze_image(self, image_path: Path) -> Dict:
        """Mock AI analysis for testing"""
        filename = image_path.name.lower()
        
        # Generate mock tags based on filename patterns
        mock_labels = []
        if 'soccer' in filename or 'football' in filename:
            mock_labels = [
                {'description': 'Sports', 'score': 0.95},
                {'description': 'Soccer', 'score': 0.92},
                {'description': 'Ball', 'score': 0.88},
                {'description': 'Player', 'score': 0.85},
                {'description': 'Field', 'score': 0.82}
            ]
        else:
            mock_labels = [
                {'description': 'Person', 'score': 0.90},
                {'description': 'Outdoor', 'score': 0.85},
                {'description': 'Scene', 'score': 0.80}
            ]
        
        return {
            'labels': mock_labels,
            'text': [],
            'faces_count': 1,
            'image_path': str(image_path)
        }
    
    def create_xml_tags(self, analysis_results: List[Dict], output_path: Path):
        """Create XML file with all analysis results"""
        root = ET.Element("VideoTags")
        
        for result in analysis_results:
            frame_elem = ET.SubElement(root, "Frame")
            frame_elem.set("path", result['image_path'])
            
            # Labels
            labels_elem = ET.SubElement(frame_elem, "Labels")
            for label in result['labels']:
                label_elem = ET.SubElement(labels_elem, "Label")
                label_elem.set("confidence", f"{label['score']:.3f}")
                label_elem.text = label['description']
            
            # Text
            if result['text']:
                text_elem = ET.SubElement(frame_elem, "Text")
                text_elem.text = ' | '.join(result['text'])
            
            # Faces
            if result['faces_count'] > 0:
                faces_elem = ET.SubElement(frame_elem, "Faces")
                faces_elem.set("count", str(result['faces_count']))
        
        # Write XML
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ", level=0)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)

