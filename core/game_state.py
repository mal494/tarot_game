# core/game_state.py

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

from core.utils import scale_animation_duration


@dataclass
class CurrentReading:
    """
    Holds all data for the reading currently in progress.
    """
    intention: Optional[str] = None
    spread_type: Optional[str] = None
    drawn_cards: List[Dict[str, Any]] = field(default_factory=list)
    interpretation: Optional[Dict[str, Any]] = None
    journal_entry_id: Optional[str] = None

    def reset(self):
        self.intention = None
        self.spread_type = None
        self.drawn_cards = []
        self.interpretation = None
        self.journal_entry_id = None


@dataclass
class GameSettings:
    """
    User‑adjustable settings.
    """
    volume: float = 0.8
    animation_speed: float = 1.0
    theme: str = "mystic"  # "mystic", "light", "dark"


class GameState:
    """
    Global game state manager.
    This is the single source of truth for:
    - current reading
    - settings
    - navigation context
    - cached data between scenes
    """

    _instance = None

    def __new__(cls):
        """
        Singleton pattern — ensures only one GameState exists.
        """
        if cls._instance is None:
            cls._instance = super(GameState, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.current_reading = CurrentReading()
        self.settings = GameSettings()

        # Optional: store last scene for transitions
        self.last_scene: Optional[str] = None

        # Optional: store global flags
        self.debug_mode: bool = False

        self._initialized = True

    # ---------------------------------------------------------
    # Reading Management
    # ---------------------------------------------------------

    def start_new_reading(self, intention: str, spread_type: str):
        """
        Initialize a new reading session.
        """
        self.current_reading.reset()
        self.current_reading.intention = intention
        self.current_reading.spread_type = spread_type

    def set_drawn_cards(self, cards: List[Dict[str, Any]]):
        """
        Save drawn cards from TarotEngine.
        """
        self.current_reading.drawn_cards = cards

    def set_interpretation(self, interpretation: Dict[str, Any]):
        """
        Save AI interpretation.
        """
        self.current_reading.interpretation = interpretation

    def set_journal_entry_id(self, entry_id: str):
        self.current_reading.journal_entry_id = entry_id

    # ---------------------------------------------------------
    # Settings Management
    # ---------------------------------------------------------

    def set_volume(self, value: float):
        self.settings.volume = max(0.0, min(1.0, value))

    def set_animation_speed(self, value: float):
        self.settings.animation_speed = max(0.1, min(3.0, value))

    def scaled_duration(self, base_duration: float) -> float:
        return scale_animation_duration(base_duration, self.settings.animation_speed)

    def set_theme(self, theme: str):
        if theme in ["mystic", "light", "dark"]:
            self.settings.theme = theme

    # ---------------------------------------------------------
    # Navigation Context
    # ---------------------------------------------------------

    def set_last_scene(self, scene_name: str):
        self.last_scene = scene_name
