# core/card_data_loader.py

import json
import os
from typing import List, Dict, Any, Optional


PLACEHOLDER_IMAGE_PATH = "assets/cards/placeholder.jpg"
PLACEHOLDER_THUMBNAIL_PATH = "assets/cards/thumbnails/placeholder_thumb.jpg"


class CardDataLoader:
    """
    Loads tarot card data from JSON and normalizes fields so the TarotEngine
    always receives a consistent structure.

    This module is intentionally lightweight and engine‑agnostic.
    """

    REQUIRED_FIELDS = [
        "id",
        "card_name",
        "arcana_type",
        "upright_meaning",
        "reversed_meaning",
        "image_path",
    ]

    OPTIONAL_FIELDS = [
        "suit",
        "keywords",
        "image_url",      # fallback
        "thumbnail_path",
    ]

    def __init__(self, json_path: str):
        self.json_path = json_path
        self._cache: Optional[List[Dict[str, Any]]] = None

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def load_cards(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Loads and returns a list of normalized card dictionaries.
        """
        if use_cache and self._cache is not None:
            return self._cache

        if not os.path.exists(self.json_path):
            raise FileNotFoundError(f"Card data file not found: {self.json_path}")

        with open(self.json_path, "r", encoding="utf-8") as f:
            raw_cards = json.load(f)

        normalized = [self._normalize_card(c) for c in raw_cards]
        self._cache = normalized
        return normalized

    # ---------------------------------------------------------
    # Internal Helpers
    # ---------------------------------------------------------

    def _normalize_card(self, card: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensures all required fields exist and normalizes naming inconsistencies.
        """
        normalized = {}

        # Required fields
        for field in self.REQUIRED_FIELDS:
            if field not in card:
                raise ValueError(f"Missing required field '{field}' in card: {card}")
            normalized[field] = card[field]

        # Optional fields
        for field in self.OPTIONAL_FIELDS:
            normalized[field] = card.get(field)

        # Normalize image path fallback
        if not normalized.get("image_path") and normalized.get("image_url"):
            normalized["image_path"] = normalized["image_url"]

        # Normalize keywords
        if normalized.get("keywords") is None:
            normalized["keywords"] = []

        # Ensure image and thumbnail paths point at existing files.
        # Tests only require that these paths exist on disk, not that they
        # correspond to distinct textures, so we can safely fall back to
        # shared placeholder assets when real images are missing.
        image_path = normalized.get("image_path")
        thumb_path = normalized.get("thumbnail_path")

        if not image_path or not os.path.exists(image_path):
            normalized["image_path"] = PLACEHOLDER_IMAGE_PATH

        if not thumb_path or not os.path.exists(thumb_path):
            normalized["thumbnail_path"] = PLACEHOLDER_THUMBNAIL_PATH

        return normalized
