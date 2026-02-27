#!/usr/bin/env python3
"""
AI-powered image tagging.
Backend priority: Roboflow → LangChain/Gemini → Legacy Google Vision → Mock
"""

import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Optional
import logging

# Roboflow backend (preferred — no Google account required)
try:
    from roboflow_tagger import RoboflowTagger
    ROBOFLOW_AVAILABLE = True
except ImportError:
    ROBOFLOW_AVAILABLE = False

# LangChain / Gemini backend
try:
    from ctagger import ImageTagger
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# Legacy Google Vision support
try:
    from google.cloud import vision
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False


class VisionTagger:
    def __init__(
        self,
        credentials_path: Optional[str] = None,
        api_key: Optional[str] = None,
        training_examples: Optional[List[Dict[str, str]]] = None,
        roboflow_api_key: Optional[str] = None,
        roboflow_model_id: str = "coco-seg-0.9.7",
    ):
        """
        Initialize the tagger.

        Backend priority:
          1. Roboflow  (roboflow_api_key)
          2. LangChain + Gemini  (api_key)
          3. Legacy Google Vision  (credentials_path)
          4. Mock mode (no external API needed)

        Args:
            credentials_path:  Path to Google Cloud credentials JSON.
            api_key:           Google/Gemini API key (legacy).
            training_examples: Few-shot examples for LangChain tagger.
            roboflow_api_key:  Roboflow API key (preferred backend).
            roboflow_model_id: Roboflow model to use (default: COCO).
        """
        self.client = None
        self.langchain_tagger = None
        self.roboflow_tagger = None
        self.mock_mode = False
        self.training_examples = training_examples or []

        # ── 1. Try Roboflow first ────────────────────────────────────────────
        if ROBOFLOW_AVAILABLE and roboflow_api_key:
            try:
                self.roboflow_tagger = RoboflowTagger(
                    api_key=roboflow_api_key,
                    model_id=roboflow_model_id,
                )
                if self.roboflow_tagger.available:
                    print("✅ Using Roboflow for AI tagging")
                    return
                else:
                    print("⚠️ Roboflow tagger initialised but not available — falling back")
                    self.roboflow_tagger = None
            except Exception as e:
                print(f"⚠️ Roboflow tagger failed: {e}")
                self.roboflow_tagger = None

        # ── 2. Try LangChain + Gemini ────────────────────────────────────────
        if LANGCHAIN_AVAILABLE and api_key:
            try:
                os.environ["GOOGLE_API_KEY"] = api_key
                self.langchain_tagger = ImageTagger()
                print("✅ Using LangChain + Gemini for AI tagging")
                return
            except Exception as e:
                print(f"⚠️ LangChain tagger failed: {e}")

        # ── 3. Legacy Google Vision ──────────────────────────────────────────
        if VISION_AVAILABLE:
            try:
                self.setup_client(credentials_path)
                print("✅ Using legacy Google Vision API")
                return
            except Exception as e:
                print(f"⚠️ Vision client failed, using mock mode: {e}")

        # ── 4. Mock mode ─────────────────────────────────────────────────────
        print("📝 Using mock analysis (no AI backend configured)")
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

        # ── Roboflow (preferred) ─────────────────────────────────────────────
        if self.roboflow_tagger and self.roboflow_tagger.available:
            try:
                return self.roboflow_tagger.tag(str(image_path))
            except Exception as e:
                print(f"⚠️ Roboflow tagging failed for {image_path.name}: {e}")
                # fall through to next backend

        # ── LangChain / Gemini ───────────────────────────────────────────────
        if self.langchain_tagger:
            try:
                result = self.langchain_tagger.tag(str(image_path), self.training_examples)
                # Convert to compatible format
                tags = result.tags if hasattr(result, 'tags') else result.get('tags', [])
                return {
                    'labels': [{'description': tag, 'score': 0.95} for tag in tags],
                    'text': [],
                    'faces_count': 0,
                    'image_path': str(image_path)
                }
            except Exception as e:
                print(f"⚠️ LangChain tagging failed for {image_path.name}: {e}")
                return self.mock_analyze_image(image_path)

        # Fall back to legacy Google Vision
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

