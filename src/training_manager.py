#!/usr/bin/env python3
"""
Training image manager for few-shot learning
"""

import json
from pathlib import Path
from typing import List, Dict, Optional

class TrainingManager:
    def __init__(self, config_path: str = "config/ai_config.json"):
        """Initialize training manager with config file"""
        self.config_path = Path(config_path)
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Load configuration from JSON file"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {
            "google_api_key": "",
            "training_examples": {}
        }
    
    def save_config(self):
        """Save configuration to JSON file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_api_key(self) -> str:
        """Get Google API key (legacy – prefer get_roboflow_api_key)."""
        return self.config.get("google_api_key", "")

    def set_api_key(self, api_key: str):
        """Set Google API key (legacy – prefer set_roboflow_api_key)."""
        self.config["google_api_key"] = api_key
        self.save_config()

    def get_roboflow_api_key(self) -> str:
        """Get the Roboflow API key."""
        return self.config.get("roboflow_api_key", "")

    def set_roboflow_api_key(self, api_key: str):
        """Set the Roboflow API key and persist it to the config file."""
        self.config["roboflow_api_key"] = api_key
        self.save_config()

    def get_roboflow_model_id(self) -> str:
        """Get the Roboflow model ID (defaults to COCO if not configured)."""
        return self.config.get("roboflow_model_id", "coco-seg-0.9.7")
    
    def add_training_example(self, category: str, label: str, image_path: str):
        """Add a training example for a category"""
        if category not in self.config["training_examples"]:
            self.config["training_examples"][category] = {
                "label": label,
                "images": []
            }
        
        # Add image if not already present
        if image_path not in self.config["training_examples"][category]["images"]:
            self.config["training_examples"][category]["images"].append(image_path)
            self.save_config()
    
    def remove_training_example(self, category: str, image_path: str):
        """Remove a training example"""
        if category in self.config["training_examples"]:
            images = self.config["training_examples"][category]["images"]
            if image_path in images:
                images.remove(image_path)
                self.save_config()
    
    def get_training_examples(self, category: Optional[str] = None, max_per_category: int = 3) -> List[Dict[str, str]]:
        """
        Get training examples in the format expected by ImageTagger.

        Args:
            category: Specific category to get examples for, or None for all
            max_per_category: Maximum number of examples per category (default: 3 for efficiency)

        Returns:
            List of dicts with 'image_path' and 'label' keys
        """
        examples = []

        if category:
            # Get examples for specific category
            if category in self.config["training_examples"]:
                cat_data = self.config["training_examples"][category]
                label = cat_data["label"]
                count = 0
                for img_path in cat_data["images"]:
                    if Path(img_path).exists() and count < max_per_category:
                        examples.append({
                            "image_path": img_path,
                            "label": label
                        })
                        count += 1
        else:
            # Get all examples (limited per category for efficiency)
            for cat_name, cat_data in self.config["training_examples"].items():
                label = cat_data["label"]
                count = 0
                for img_path in cat_data["images"]:
                    if Path(img_path).exists() and count < max_per_category:
                        examples.append({
                            "image_path": img_path,
                            "label": label
                        })
                        count += 1

        return examples
    
    def list_categories(self) -> List[str]:
        """List all training categories"""
        return list(self.config["training_examples"].keys())
    
    def get_category_info(self, category: str) -> Optional[Dict]:
        """Get information about a specific category"""
        return self.config["training_examples"].get(category)


if __name__ == "__main__":
    # Example usage
    manager = TrainingManager()
    
    print("Training Manager")
    print("=" * 50)
    print(f"API Key configured: {'Yes' if manager.get_api_key() else 'No'}")
    print(f"\nCategories: {manager.list_categories()}")
    
    for category in manager.list_categories():
        info = manager.get_category_info(category)
        print(f"\n{category}:")
        print(f"  Label: {info['label']}")
        print(f"  Images: {len(info['images'])}")
        for img in info['images']:
            exists = "✓" if Path(img).exists() else "✗"
            print(f"    {exists} {img}")

