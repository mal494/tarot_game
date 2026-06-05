import asyncio
import tempfile
import unittest
from pathlib import Path

from ai.interpreter import AIInterpreter
from ai.prompt_templates import build_prompt
from core import utils
from core.card_data_loader import CardDataLoader
from core.game_state import GameState
from core.tarot_engine import SpreadType, TarotEngine
from journal.journal_manager import JournalManager, JournalCorruptError


CARD_PATH = "assets/data/tarot_cards.json"


class TarotDataTests(unittest.TestCase):
    def test_loads_full_placeholder_deck(self):
        cards = CardDataLoader(CARD_PATH).load_cards(use_cache=False)

        self.assertEqual(len(cards), 78)
        self.assertEqual(cards[0]["card_name"], "The Fool")
        self.assertEqual(cards[-1]["card_name"], "King of Pentacles")

    def test_card_image_and_thumbnail_paths_exist(self):
        cards = CardDataLoader(CARD_PATH).load_cards(use_cache=False)

        for card in cards:
            with self.subTest(card=card["card_name"]):
                self.assertTrue(Path(card["image_path"]).exists())
                self.assertTrue(Path(card["thumbnail_path"]).exists())

    def test_draw_serialization_is_flat(self):
        cards = CardDataLoader(CARD_PATH).load_cards(use_cache=False)
        engine = TarotEngine(cards, seed=1)

        drawn = engine.draw_single()
        serialized = drawn[0].to_dict()

        self.assertIn("name", serialized)
        self.assertIn("image_path", serialized)
        self.assertIn("orientation", serialized)
        self.assertIn("meaning", serialized)
        self.assertNotIn("card", serialized)

    def test_draws_single_and_three_card_spreads(self):
        cards = CardDataLoader(CARD_PATH).load_cards(use_cache=False)
        engine = TarotEngine(cards, seed=2)

        self.assertEqual(len(engine.draw_spread(SpreadType.SINGLE)), 1)
        self.assertEqual(len(engine.draw_spread(SpreadType.THREE)), 3)

    def test_prompt_uses_flat_card_data(self):
        cards = CardDataLoader(CARD_PATH).load_cards(use_cache=False)
        drawn = [card.to_dict() for card in TarotEngine(cards, seed=3).draw_single()]

        prompt = build_prompt("clarity", "single", drawn)

        self.assertIn("clarity", prompt)
        self.assertIn(drawn[0]["name"], prompt)
        self.assertIn(drawn[0]["orientation"], prompt)


class JournalTests(unittest.TestCase):
    def test_save_load_delete_and_reset(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "journal.json"
            manager = JournalManager(str(path))

            entry = manager.save_entry(
                intention="clarity",
                spread_type="single",
                cards=[{"name": "The Fool", "orientation": "upright"}],
                interpretation="A fresh beginning.",
                date="2026-06-04 22:00",
            )

            self.assertEqual(len(manager.load_entries()), 1)
            manager.delete_entry(entry["id"])
            self.assertEqual(manager.load_entries(), [])

            manager.save_entry("focus", "single", [], "Listen inward.")
            manager.reset_journal()
            self.assertEqual(manager.load_entries(), [])

    def test_corrupt_journal_raises_and_creates_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "journal.json"
            path.write_text("{not valid json", encoding="utf-8")
            manager = JournalManager(str(path))

            with self.assertRaises(JournalCorruptError) as ctx:
                manager.load_entries()

            self.assertFalse(path.exists())
            self.assertTrue(ctx.exception.backup_path.exists())
            self.assertIn("invalid JSON", str(ctx.exception))

    def test_non_list_journal_raises_and_creates_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "journal.json"
            path.write_text('{"entries": []}', encoding="utf-8")
            manager = JournalManager(str(path))

            with self.assertRaises(JournalCorruptError) as ctx:
                manager.load_entries()

            self.assertFalse(path.exists())
            self.assertTrue(ctx.exception.backup_path.exists())

    def test_fresh_manager_after_corrupt_backup_starts_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "journal.json"
            path.write_text("{bad", encoding="utf-8")
            manager = JournalManager(str(path))

            with self.assertRaises(JournalCorruptError):
                manager.load_entries()

            recovered = JournalManager(str(path))
            self.assertEqual(recovered.load_entries(), [])


class OfflineInterpreterTests(unittest.TestCase):
    def test_offline_interpreter_returns_sections(self):
        cards = CardDataLoader(CARD_PATH).load_cards(use_cache=False)
        drawn = [card.to_dict() for card in TarotEngine(cards, seed=4).draw_three()]
        state = GameState()
        state.start_new_reading("clarity", SpreadType.THREE)
        state.set_drawn_cards(drawn)

        with tempfile.TemporaryDirectory() as tmp:
            journal_path = str(Path(tmp) / "journal.json")
            result = asyncio.run(AIInterpreter(journal_path=journal_path).interpret_current_reading())

            self.assertTrue(result["summary"])
            self.assertTrue(result["analysis"])
            self.assertTrue(result["guidance"])
            self.assertTrue(result["affirmation"])
            self.assertTrue(result["full_text"])
            self.assertEqual(len(JournalManager(journal_path).load_entries()), 1)

    def test_double_interpret_updates_single_journal_entry(self):
        cards = CardDataLoader(CARD_PATH).load_cards(use_cache=False)
        drawn = [card.to_dict() for card in TarotEngine(cards, seed=5).draw_single()]
        state = GameState()
        state.start_new_reading("clarity", SpreadType.SINGLE)
        state.set_drawn_cards(drawn)

        with tempfile.TemporaryDirectory() as tmp:
            journal_path = str(Path(tmp) / "journal.json")
            interpreter = AIInterpreter(journal_path=journal_path)

            asyncio.run(interpreter.interpret_current_reading())
            asyncio.run(interpreter.interpret_current_reading())

            entries = JournalManager(journal_path).load_entries()
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["id"], state.current_reading.journal_entry_id)

    def test_new_reading_creates_new_journal_entry(self):
        cards = CardDataLoader(CARD_PATH).load_cards(use_cache=False)

        with tempfile.TemporaryDirectory() as tmp:
            journal_path = str(Path(tmp) / "journal.json")
            interpreter = AIInterpreter(journal_path=journal_path)

            state = GameState()
            state.start_new_reading("first", SpreadType.SINGLE)
            state.set_drawn_cards(
                [card.to_dict() for card in TarotEngine(cards, seed=6).draw_single()]
            )
            asyncio.run(interpreter.interpret_current_reading())
            first_entry_id = state.current_reading.journal_entry_id

            state.start_new_reading("second", SpreadType.SINGLE)
            state.set_drawn_cards(
                [card.to_dict() for card in TarotEngine(cards, seed=7).draw_single()]
            )
            asyncio.run(interpreter.interpret_current_reading())

            entries = JournalManager(journal_path).load_entries()
            self.assertEqual(len(entries), 2)
            self.assertNotEqual(first_entry_id, state.current_reading.journal_entry_id)


class InterpreterParsingTests(unittest.TestCase):
    def setUp(self):
        self.interpreter = AIInterpreter()

    def test_parses_bare_headings_from_offline_model(self):
        text = (
            "Summary\n"
            "Short summary here.\n\n"
            "Analysis\n"
            "Deep analysis.\n\n"
            "Guidance\n"
            "Advice here.\n\n"
            "Affirmation\n"
            "I trust myself."
        )
        result = self.interpreter._parse_response(text)

        self.assertEqual(result["summary"], "Short summary here.")
        self.assertEqual(result["analysis"], "Deep analysis.")
        self.assertEqual(result["guidance"], "Advice here.")
        self.assertEqual(result["affirmation"], "I trust myself.")

    def test_parses_numbered_headings(self):
        text = (
            "1. Summary\n"
            "Overview here.\n\n"
            "2. Analysis\n"
            "Deep dive.\n\n"
            "3. Guidance\n"
            "Do this today.\n\n"
            "4. Affirmation\n"
            "I am calm."
        )
        result = self.interpreter._parse_response(text)

        self.assertEqual(result["summary"], "Overview here.")
        self.assertEqual(result["analysis"], "Deep dive.")
        self.assertEqual(result["guidance"], "Do this today.")
        self.assertEqual(result["affirmation"], "I am calm.")

    def test_parses_markdown_headings(self):
        text = (
            "### Summary\n"
            "Overview.\n\n"
            "**Analysis**\n"
            "Details.\n\n"
            "## Guidance\n"
            "Advice.\n\n"
            "Affirmation:\n"
            "Yes."
        )
        result = self.interpreter._parse_response(text)

        self.assertEqual(result["summary"], "Overview.")
        self.assertEqual(result["analysis"], "Details.")
        self.assertEqual(result["guidance"], "Advice.")
        self.assertEqual(result["affirmation"], "Yes.")


class UtilityTests(unittest.TestCase):
    def test_weighted_choice_rejects_invalid_inputs(self):
        with self.assertRaises(ValueError):
            utils.weighted_choice({})
        with self.assertRaises(ValueError):
            utils.weighted_choice({"a": 0, "b": 0})
        with self.assertRaises(ValueError):
            utils.weighted_choice({"a": 1, "b": -2})

    def test_save_json_creates_parent_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nested" / "data.json"
            utils.save_json(str(path), {"ok": True})

            self.assertEqual(utils.load_json(str(path)), {"ok": True})

    def test_hex_and_truncate_validation(self):
        self.assertEqual(utils.hex_to_rgb("#ffffff"), (1.0, 1.0, 1.0))
        with self.assertRaises(ValueError):
            utils.hex_to_rgb("#fff")
        with self.assertRaises(ValueError):
            utils.truncate("hello", 3)

    def test_scale_animation_duration_scales_inversely_with_speed(self):
        self.assertAlmostEqual(utils.scale_animation_duration(1.2, 2.0), 0.6)
        self.assertAlmostEqual(utils.scale_animation_duration(0.4, 0.5), 0.8)

    def test_scale_animation_duration_rejects_non_positive_speed(self):
        with self.assertRaises(ValueError):
            utils.scale_animation_duration(1.0, 0)


class GameStateTests(unittest.TestCase):
    def test_last_scene_and_reading_reset(self):
        state = GameState()
        state.set_last_scene("menu")
        state.start_new_reading("focus", SpreadType.SINGLE)
        state.set_drawn_cards([{"name": "The Fool"}])

        self.assertEqual(state.last_scene, "menu")
        self.assertEqual(state.current_reading.intention, "focus")
        self.assertEqual(len(state.current_reading.drawn_cards), 1)

        state.start_new_reading("clarity", SpreadType.THREE)
        self.assertEqual(state.current_reading.intention, "clarity")
        self.assertEqual(state.current_reading.drawn_cards, [])

    def test_scaled_duration_uses_animation_speed_setting(self):
        state = GameState()
        state.set_animation_speed(2.0)
        self.assertAlmostEqual(state.scaled_duration(1.0), 0.5)

        state.set_animation_speed(0.5)
        self.assertAlmostEqual(state.scaled_duration(1.0), 2.0)


if __name__ == "__main__":
    unittest.main()
