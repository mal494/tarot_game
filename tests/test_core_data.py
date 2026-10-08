import json
import subprocess
import sys
import unittest
from pathlib import Path

from core.card_data_loader import CardDataLoader
from core.tarot_engine import TarotEngine

ROOT = Path(__file__).resolve().parent.parent
CARD_PATH = "assets/data/tarot_cards.json"
ELEMENTS = {"Fire", "Water", "Air", "Earth"}


def raw_cards():
    return json.loads((ROOT / CARD_PATH).read_text(encoding="utf-8"))


class CoreGeneratedDataTests(unittest.TestCase):
    def test_card_file_matches_pinned_core(self):
        result = subprocess.run(
            [sys.executable, "tools/generate_cards.py", "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_core_version_is_pinned(self):
        version = (ROOT / "core.version").read_text(encoding="utf-8").strip()
        self.assertTrue((ROOT / "data" / "core" / f"tarot_data_{version}.json").exists())

    def test_every_card_has_core_fields(self):
        cards = raw_cards()
        self.assertEqual(len(cards), 78)
        self.assertEqual(len({c["key"] for c in cards}), 78)
        self.assertEqual([c["id"] for c in cards], list(range(78)))
        for card in cards:
            with self.subTest(card=card["card_name"]):
                for field in ("short_description", "element", "astrology"):
                    self.assertTrue(card[field])
                self.assertTrue(card["tags"])
                self.assertTrue(card["life_domains"])
                self.assertTrue(card["positional_text"])

    def test_astrology_is_never_an_element(self):
        for card in raw_cards():
            parts = set(card["astrology"].split("/"))
            with self.subTest(card=card["card_name"]):
                self.assertFalse(parts <= ELEMENTS, card["astrology"])

    def test_major_arcana_suit_is_null(self):
        for card in raw_cards():
            if card["arcana_type"] == "Major":
                self.assertIsNone(card["suit"], card["card_name"])

    def test_core_fields_reach_drawn_cards(self):
        cards = CardDataLoader(CARD_PATH).load_cards(use_cache=False)
        drawn = TarotEngine(cards, seed=8).draw_three()
        for dc in drawn:
            data = dc.to_dict()
            for field in ("element", "astrology", "tags", "life_domains", "short_description"):
                self.assertIn(field, data)
            self.assertTrue(data["tags"])
            self.assertNotEqual(data["suit"], "None")


if __name__ == "__main__":
    unittest.main()
