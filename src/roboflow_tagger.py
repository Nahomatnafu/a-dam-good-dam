#!/usr/bin/env python3
"""
Roboflow-based image tagger for the A-Dam-Good-Dam media catalog system.

Uses the Roboflow hosted inference API (free tier) with an object-detection
model.  The default model is COCO (80 common objects) which works with zero
training.  Swap ``model_id`` for your own custom campus model once trained.

Setup:
    pip install inference-sdk
    # Get your API key at https://app.roboflow.com → Settings → API Keys
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Default confidence threshold for keeping a detection
DEFAULT_CONFIDENCE = 0.40

# Pre-trained COCO detection model (free, no training required).
# Replace with a custom campus model once you have trained one on Roboflow.
DEFAULT_MODEL_ID = "coco-seg-0.9.7"


class RoboflowTagger:
    """
    Generates descriptive tags for a single image via Roboflow Inference.

    Args:
        api_key:    Roboflow API key.
        model_id:   Roboflow model ID to use for inference.
                    Defaults to COCO object detection (no training needed).
                    Example custom model: "my-workspace/campus-buildings/1"
        confidence: Minimum detection confidence (0-1) to include a tag.
    """

    def __init__(
        self,
        api_key: str,
        model_id: str = DEFAULT_MODEL_ID,
        confidence: float = DEFAULT_CONFIDENCE,
    ):
        self.model_id = model_id
        self.confidence = confidence
        self._client = None
        self._available = False

        if not api_key:
            logger.warning("RoboflowTagger: no API key provided – tagger disabled.")
            return

        try:
            from inference_sdk import InferenceHTTPClient  # type: ignore

            self._client = InferenceHTTPClient(
                api_url="https://infer.roboflow.com",
                api_key=api_key,
            )
            self._available = True
            logger.info(
                "✅ RoboflowTagger ready  (model: %s, threshold: %.0f%%)",
                model_id,
                confidence * 100,
            )
        except ImportError:
            logger.warning(
                "inference-sdk is not installed. "
                "Run:  pip install inference-sdk"
            )

    # ── Public interface ──────────────────────────────────────────────────────

    @property
    def available(self) -> bool:
        return self._available

    def tag(self, image_path: str) -> Dict:
        """
        Analyse *image_path* and return a result dict compatible with
        the existing ``VisionTagger.analyze_image`` output format.

        Returns::

            {
                'labels':      [{'description': str, 'score': float}, ...],
                'text':        [],
                'faces_count': int,
                'image_path':  str,
            }
        """
        if not self._available:
            return self._empty_result(image_path)

        try:
            raw = self._client.infer(str(image_path), model_id=self.model_id)
        except Exception as exc:
            logger.warning("Roboflow inference failed for %s: %s", image_path, exc)
            return self._empty_result(image_path)

        return self._parse_result(raw, image_path)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _parse_result(self, raw: Dict, image_path: str) -> Dict:
        """Convert the raw Roboflow response to the VisionTagger format."""
        predictions = raw.get("predictions", []) if isinstance(raw, dict) else []

        seen: Dict[str, float] = {}
        faces = 0

        for pred in predictions:
            label = pred.get("class", "").lower().replace("-", " ").strip()
            conf = float(pred.get("confidence", 0))
            if label and conf >= self.confidence:
                seen[label] = max(seen.get(label, 0.0), conf)
                if label == "person":
                    faces += 1

        labels = sorted(
            [{"description": k, "score": round(v, 4)} for k, v in seen.items()],
            key=lambda x: x["score"],
            reverse=True,
        )

        return {
            "labels": labels,
            "text": [],
            "faces_count": faces,
            "image_path": str(image_path),
        }

    @staticmethod
    def _empty_result(image_path: str) -> Dict:
        return {
            "labels": [],
            "text": [],
            "faces_count": 0,
            "image_path": str(image_path),
        }

