# journal/journal_entry.py

import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Any
from core.utils import formatted_date


@dataclass
class JournalEntry:
    """
    Represents a single tarot journal entry.
    Used by JournalManager for JSON persistence.
    """

    intention: str
    spread_type: str
    cards: List[Dict[str, Any]]
    interpretation: str
    date: str = field(default_factory=formatted_date)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "date": self.date,
            "intention": self.intention,
            "spread_type": self.spread_type,
            "cards": self.cards,
            "interpretation": self.interpretation,
        }

    # ---------------------------------------------------------
    # Deserialization
    # ---------------------------------------------------------

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "JournalEntry":
        return JournalEntry(
            id=data.get("id", str(uuid.uuid4())),
            date=data.get("date", formatted_date()),
            intention=data.get("intention", ""),
            spread_type=data.get("spread_type", "single"),
            cards=data.get("cards", []),
            interpretation=data.get("interpretation", "")
        )
