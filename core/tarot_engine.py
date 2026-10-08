# core/tarot_engine.py

import random
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Any


@dataclass
class TarotCard:
    """
    Represents a single tarot card from your dataset.
    """
    id: int
    name: str
    arcana: str               # "Major" or "Minor"
    suit: Optional[str]       # "Wands", "Cups", etc., or None for Major
    upright: str              # Upright meaning text
    reversed: str             # Reversed meaning text
    keywords: List[str]
    image_path: str           # Path to texture in assets/cards/
    thumbnail_path: Optional[str] = None
    # Divine Insight Core fields (see CORE.md). Optional so older card files still load.
    key: Optional[str] = None
    slug: Optional[str] = None
    short_description: Optional[str] = None
    element: Optional[str] = None
    astrology: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    life_domains: List[str] = field(default_factory=list)
    reversed_keywords: List[str] = field(default_factory=list)
    positional_text: Dict[str, str] = field(default_factory=dict)


@dataclass
class DrawnCard:
    """
    Represents a card as drawn in a reading, including orientation.
    """
    card: TarotCard
    orientation: str          # "upright" or "reversed"

    @property
    def meaning(self) -> str:
        return self.card.upright if self.orientation == "upright" else self.card.reversed

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self.card)
        data["orientation"] = self.orientation
        data["meaning"] = self.meaning
        return data


class SpreadType:
    SINGLE = "single"
    THREE = "three"
    CUSTOM = "custom"


class TarotEngine:
    """
    Core tarot logic:
    - Manages deck
    - Shuffles and draws cards
    - Handles upright/reversed orientation
    - Supports different spreads
    - Optional random seed for reproducible readings
    """

    def __init__(self, cards: List[Dict[str, Any]], seed: Optional[int] = None):
        """
        :param cards: list of dicts from tarot_cards.json
        :param seed: optional seed for reproducible randomness
        """
        self._raw_cards = cards
        self.deck: List[TarotCard] = self._build_deck(cards)
        self._rng = random.Random(seed) if seed is not None else random.Random()

    @staticmethod
    def _build_deck(cards: List[Dict[str, Any]]) -> List[TarotCard]:
        deck = []
        for c in cards:
            deck.append(
                TarotCard(
                    id=int(c.get("id", 0)),
                    name=str(c.get("card_name") or c.get("name") or "Unknown"),
                    arcana=str(c.get("arcana_type") or c.get("arcana") or "Major"),
                    suit=c.get("suit") if c.get("suit") not in (None, "", "None") else None,
                    upright=str(c.get("upright_meaning") or ""),
                    reversed=str(c.get("reversed_meaning") or ""),
                    keywords=c.get("keywords", []),
                    image_path=str(c.get("image_path") or c.get("image_url") or ""),
                    thumbnail_path=c.get("thumbnail_path"),
                    key=c.get("key"),
                    slug=c.get("slug"),
                    short_description=c.get("short_description"),
                    element=c.get("element"),
                    astrology=c.get("astrology"),
                    tags=list(c.get("tags") or []),
                    life_domains=list(c.get("life_domains") or []),
                    reversed_keywords=list(c.get("reversed_keywords") or []),
                    positional_text=dict(c.get("positional_text") or {}),
                )
            )
        return deck

    def set_seed(self, seed: Optional[int]) -> None:
        """
        Update RNG seed at runtime (e.g., for debug or replay).
        """
        self._rng = random.Random(seed) if seed is not None else random.Random()

    def _shuffle_deck(self) -> List[TarotCard]:
        """
        Returns a shuffled copy of the deck.
        """
        deck_copy = self.deck.copy()
        self._rng.shuffle(deck_copy)
        return deck_copy

    def _draw_n(self, n: int) -> List[DrawnCard]:
        """
        Draw n cards from a shuffled deck with random orientation.
        """
        if n <= 0:
            return []

        shuffled = self._shuffle_deck()
        drawn: List[DrawnCard] = []

        for card in shuffled[:n]:
            orientation = "upright" if self._rng.random() > 0.5 else "reversed"
            drawn.append(DrawnCard(card=card, orientation=orientation))

        return drawn

    # ---------- Public API ----------

    def draw_single(self) -> List[DrawnCard]:
        """
        Single‑card pull (daily card).
        """
        return self._draw_n(1)

    def draw_three(self) -> List[DrawnCard]:
        """
        Three‑card spread (past / present / future).
        """
        return self._draw_n(3)

    def draw_custom(self, count: int) -> List[DrawnCard]:
        """
        Custom spread with arbitrary card count.
        """
        return self._draw_n(count)

    def draw_spread(self, spread_type: str, count: Optional[int] = None) -> List[DrawnCard]:
        """
        Generic entry point for spreads.
        """
        if spread_type == SpreadType.SINGLE:
            return self.draw_single()
        elif spread_type == SpreadType.THREE:
            return self.draw_three()
        elif spread_type == SpreadType.CUSTOM:
            if not count or count <= 0:
                raise ValueError("Custom spread requires a positive 'count'.")
            return self.draw_custom(count)
        else:
            raise ValueError(f"Unknown spread type: {spread_type}")

    def serialize_reading(
        self,
        drawn_cards: List[DrawnCard],
        intention: Optional[str] = None,
        spread_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Helper to turn a reading into a dict for saving / AI prompts / journal.
        """
        return {
            "intention": intention,
            "spread_type": spread_type,
            "cards": [dc.to_dict() for dc in drawn_cards],
        }
