#!/usr/bin/env python3
"""
Context-aware tag filtering for academic video content
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Set
import logging

class TagFilter:
    def __init__(self, config_path: str = "config/tag_filter_config.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        
        # Compile regex patterns for efficiency
        self.blacklist_patterns = [re.compile(pattern, re.IGNORECASE) 
                                 for pattern in self.config.get("blacklist_patterns", [])]
    
    def load_config(self) -> Dict:
        """Load tag filtering configuration"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        
        # Default configuration
        default_config = {
            "mode": "hybrid",  # "whitelist", "blacklist", or "hybrid"
            "academic_whitelist": [
                # People
                "president inch", "professor", "student", "faculty", "staff",
                "speaker", "presenter", "administrator", "dean", "chancellor",
                
                # Buildings & Spaces
                "administration building", "admin building", "library", "student center",
                "lecture hall", "classroom", "auditorium", "gymnasium", "cafeteria",
                "dormitory", "residence hall", "laboratory", "lab", "office building",
                "campus", "quad", "courtyard", "plaza", "atrium", "entrance",
                
                # Academic Activities
                "graduation", "commencement", "ceremony", "conference", "seminar",
                "lecture", "presentation", "meeting", "event", "celebration",
                "research", "study", "learning", "teaching", "education",
                
                # Academic Objects
                "podium", "lectern", "projector", "screen", "whiteboard", "blackboard",
                "diploma", "degree", "award", "trophy", "banner", "flag",
                "book", "computer", "laptop", "tablet", "microphone",
                
                # Academic Clothing
                "graduation gown", "cap and gown", "academic regalia", "suit",
                "business attire", "uniform", "name tag", "badge"
            ],
            
            "generic_blacklist": [
                # Generic descriptors
                "man", "woman", "person", "people", "human", "individual",
                "male", "female", "adult", "young", "old", "elderly",
                
                # Generic objects
                "object", "thing", "item", "stuff", "material", "surface",
                "background", "foreground", "scene", "image", "photo",
                
                # Generic colors (unless specific)
                "red", "blue", "green", "yellow", "black", "white", "gray",
                "brown", "orange", "purple", "pink", "color", "colored",
                
                # Generic body parts
                "hand", "arm", "leg", "foot", "head", "face", "eye", "nose",
                "mouth", "hair", "skin", "body", "torso", "shoulder",
                
                # Generic actions (unless academic)
                "sitting", "standing", "walking", "looking", "holding",
                "wearing", "using", "touching", "moving", "being",
                
                # Generic locations
                "indoor", "outdoor", "inside", "outside", "room", "space",
                "area", "place", "location", "position", "spot"
            ],
            
            "blacklist_patterns": [
                r"^(very|quite|really|extremely|highly)\s+\w+$",  # Intensity modifiers
                r"^\w{1,2}$",  # Very short words
                r"^(the|and|or|but|in|on|at|to|for|of|with|by)$",  # Articles/prepositions
                r"^\d+$",  # Pure numbers
                r"^(left|right|top|bottom|center|middle)$",  # Positional
                r"^(large|small|big|little|tiny|huge|massive)$",  # Size without context
            ],
            
            "confidence_boost": {
                # Boost confidence for academic terms
                "president inch": 1.2,
                "administration building": 1.1,
                "library": 1.1,
                "student center": 1.1,
                "graduation": 1.2,
                "commencement": 1.2
            },
            
            "context_rules": {
                # If these terms appear, boost related academic terms
                "academic_context_triggers": ["university", "college", "campus", "academic"],
                "building_context_triggers": ["building", "hall", "center", "library"],
                "event_context_triggers": ["ceremony", "graduation", "commencement", "event"]
            }
        }
        
        # Save default config if it doesn't exist
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def filter_tags(self, tags: List[str], confidence_scores: List[float] = None) -> List[Dict]:
        """
        Filter tags based on configuration and return with adjusted confidence
        
        Args:
            tags: List of tag strings
            confidence_scores: Optional list of confidence scores (0-1)
            
        Returns:
            List of dicts with 'tag' and 'confidence' keys
        """
        if confidence_scores is None:
            confidence_scores = [0.8] * len(tags)  # Default confidence
        
        filtered_results = []
        mode = self.config.get("mode", "hybrid")
        
        # Normalize tags
        normalized_tags = [tag.lower().strip() for tag in tags]
        
        # Detect context
        context = self.detect_context(normalized_tags)
        
        for i, (tag, confidence) in enumerate(zip(normalized_tags, confidence_scores)):
            if not tag or len(tag) < 2:
                continue
            
            # Apply filtering based on mode
            should_include = False
            
            if mode == "whitelist":
                should_include = self.is_whitelisted(tag)
            elif mode == "blacklist":
                should_include = not self.is_blacklisted(tag)
            elif mode == "hybrid":
                # Include if whitelisted OR (not blacklisted AND has academic context)
                should_include = (self.is_whitelisted(tag) or 
                                (not self.is_blacklisted(tag) and self.has_academic_context(tag, context)))
            
            if should_include:
                # Apply confidence adjustments
                adjusted_confidence = self.adjust_confidence(tag, confidence, context)
                
                filtered_results.append({
                    'tag': tags[i],  # Use original case
                    'confidence': min(1.0, adjusted_confidence)
                })
        
        # Sort by confidence (highest first)
        filtered_results.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Limit to top results
        max_tags = self.config.get("max_tags", 20)
        return filtered_results[:max_tags]
    
    def is_whitelisted(self, tag: str) -> bool:
        """Check if tag is in academic whitelist"""
        whitelist = self.config.get("academic_whitelist", [])
        return any(term.lower() in tag or tag in term.lower() for term in whitelist)
    
    def is_blacklisted(self, tag: str) -> bool:
        """Check if tag is in generic blacklist or matches blacklist patterns"""
        # Check explicit blacklist
        blacklist = self.config.get("generic_blacklist", [])
        if any(term.lower() == tag or tag == term.lower() for term in blacklist):
            return True
        
        # Check regex patterns
        return any(pattern.match(tag) for pattern in self.blacklist_patterns)
    
    def detect_context(self, tags: List[str]) -> Set[str]:
        """Detect academic context from tag list"""
        context = set()
        context_rules = self.config.get("context_rules", {})
        
        for context_type, triggers in context_rules.items():
            if any(trigger in tag for tag in tags for trigger in triggers):
                context.add(context_type)
        
        return context
    
    def has_academic_context(self, tag: str, context: Set[str]) -> bool:
        """Check if tag has academic relevance given context"""
        # Academic terms are always relevant
        if self.is_whitelisted(tag):
            return True
        
        # Check context-specific relevance
        if "academic_context_triggers" in context:
            academic_terms = ["education", "learning", "teaching", "research", "study"]
            if any(term in tag for term in academic_terms):
                return True
        
        if "building_context_triggers" in context:
            building_terms = ["entrance", "door", "window", "floor", "ceiling", "wall"]
            if any(term in tag for term in building_terms):
                return True
        
        if "event_context_triggers" in context:
            event_terms = ["audience", "crowd", "applause", "speech", "stage"]
            if any(term in tag for term in event_terms):
                return True
        
        return False
    
    def adjust_confidence(self, tag: str, confidence: float, context: Set[str]) -> float:
        """Adjust confidence based on academic relevance and context"""
        # Apply confidence boosts from config
        boost_map = self.config.get("confidence_boost", {})
        for term, boost in boost_map.items():
            if term.lower() in tag:
                confidence *= boost
                break
        
        # Context-based adjustments
        if "academic_context_triggers" in context and self.is_whitelisted(tag):
            confidence *= 1.1  # Boost academic terms in academic context
        
        return confidence
    
    def get_statistics(self, original_tags: List[str], filtered_results: List[Dict]) -> Dict:
        """Get filtering statistics"""
        return {
            "original_count": len(original_tags),
            "filtered_count": len(filtered_results),
            "filter_rate": 1 - (len(filtered_results) / max(1, len(original_tags))),
            "top_tags": [r['tag'] for r in filtered_results[:5]],
            "avg_confidence": sum(r['confidence'] for r in filtered_results) / max(1, len(filtered_results))
        }
