import re
from typing import Any, Dict, Optional, Set

from ai.prompt_templates import build_prompt
from core.game_state import GameState
from journal.journal_manager import JournalManager


class OfflineTarotModel:
    """
    Deterministic local model used by the offline MVP.
    """

    async def generate(self, prompt: str) -> str:
        gs = GameState().current_reading
        cards = gs.drawn_cards
        names = ", ".join(f"{c['name']} ({c['orientation']})" for c in cards) or "the cards"
        core_meaning = cards[0]["meaning"] if cards else "Pause, listen inward, and choose the next step with care."

        return (
            "Summary\n"
            f"Your intention, \"{gs.intention or 'No intention provided'}\", is reflected through {names}. "
            "The reading points to a moment of reflection, choice, and gentle realignment.\n\n"
            "Analysis\n"
            f"The strongest message comes from: {core_meaning} "
            "Taken together, the cards invite you to notice what is already shifting beneath the surface and where your attention is being pulled.\n\n"
            "Guidance\n"
            "Move slowly enough to separate intuition from urgency. Write down one practical action you can take today, then give yourself space to observe what changes.\n\n"
            "Affirmation\n"
            "I trust the pattern unfolding and meet it with clarity."
        )


SECTION_HEADINGS: Set[str] = {"summary", "analysis", "guidance", "affirmation"}


class AIInterpreter:
    """
    Builds a tarot prompt, asks a model client for text, stores the result in
    GameState, and writes completed readings to the journal.
    """

    def __init__(self, model_client: Optional[Any] = None, journal_path: str = "assets/data/journal.json"):
        self.model = model_client or OfflineTarotModel()
        self.journal = JournalManager(journal_path)

    async def interpret_current_reading(self) -> Dict[str, Any]:
        gs = GameState().current_reading
        prompt = build_prompt(
            intention=gs.intention or "No intention provided",
            spread_type=gs.spread_type or "single",
            cards=gs.drawn_cards,
        )

        raw_response = await self.model.generate(prompt)
        interpretation = self._parse_response(raw_response)
        GameState().set_interpretation(interpretation)
        self._persist_reading(gs, interpretation["full_text"])

        return interpretation

    def _persist_reading(self, reading, interpretation: str) -> None:
        intention = reading.intention or "No intention provided"
        spread_type = reading.spread_type or "single"
        entry_id = reading.journal_entry_id

        if entry_id:
            self.journal.update_entry(
                entry_id=entry_id,
                intention=intention,
                spread_type=spread_type,
                cards=reading.drawn_cards,
                interpretation=interpretation,
            )
            return

        entry = self.journal.save_entry(
            intention=intention,
            spread_type=spread_type,
            cards=reading.drawn_cards,
            interpretation=interpretation,
        )
        GameState().set_journal_entry_id(entry["id"])

    def _parse_response(self, text: str) -> Dict[str, Any]:
        sections = {
            "summary": self._extract_section(text, "summary"),
            "analysis": self._extract_section(text, "analysis"),
            "guidance": self._extract_section(text, "guidance"),
            "affirmation": self._extract_section(text, "affirmation"),
            "full_text": text.strip(),
        }
        return sections

    @staticmethod
    def _normalize_heading(line: str) -> Optional[str]:
        stripped = line.strip()
        if not stripped:
            return None

        cleaned = re.sub(r"^#+\s*", "", stripped)
        cleaned = re.sub(r"^\*\*(.+)\*\*$", r"\1", cleaned)
        cleaned = cleaned.strip().lower().rstrip(":")
        cleaned = re.sub(r"^\d+\.\s*", "", cleaned)
        cleaned = re.sub(r"^\d+\)\s*", "", cleaned)

        if cleaned in SECTION_HEADINGS:
            return cleaned
        return None

    def _extract_section(self, text: str, keyword: str) -> str:
        lines = text.splitlines()
        capture = False
        buffer = []

        for line in lines:
            heading = self._normalize_heading(line)
            if heading == keyword:
                capture = True
                continue
            if capture and heading:
                break
            if capture:
                buffer.append(line)

        return "\n".join(buffer).strip()
