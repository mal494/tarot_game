# scenes/menu_scene.py

from ursina import *
from components.ui_button import UIButton
from fx.particle_fx import FloatingParticles
from core.game_state import GameState
from scenes.scene_manager import switch_scene


class MenuScene(Entity):
    """
    Main Menu Scene for Arcana Path.
    Includes:
    - Title logo
    - Start Reading
    - Journal
    - Settings
    - Exit
    - Ambient particles + mystical atmosphere
    """

    def __init__(self):
        super().__init__()
        self.ui_root = Entity(parent=camera.ui)

        GameState().set_last_scene("menu")

        # Background particles
        self.particles = FloatingParticles(
            parent=self,
            count=50,
            area=(6, 4),
            z=1
        )

        # Title
        self.title = Text(
            "ARCANA PATH",
            parent=self.ui_root,
            y=0.35,
            scale=3,
            origin=(0, 0),
            color=color.rgba(255, 230, 255, 240)
        )

        # Buttons
        self.start_btn = UIButton(
            "Start Reading",
            on_click=self.start_reading,
            position=(0, 0.1),
            parent=self.ui_root,
        )

        self.journal_btn = UIButton(
            "Tarot Journal",
            on_click=self.open_journal,
            position=(0, -0.05),
            parent=self.ui_root,
        )

        self.settings_btn = UIButton(
            "Settings",
            on_click=self.open_settings,
            position=(0, -0.20),
            parent=self.ui_root,
        )

        self.exit_btn = UIButton(
            "Exit",
            on_click=lambda: os._exit(0),
            position=(0, -0.35),
            parent=self.ui_root,
        )

        # Fade-in effect
        self._fade = Entity(
            parent=self.ui_root,
            model="quad",
            color=color.black,
            scale=(2, 2),
            z=2
        )
        self._fade.animate_color(color.rgba(0, 0, 0, 0), duration=0.8)

    # ---------------------------------------------------------
    # Button Callbacks
    # ---------------------------------------------------------

    def start_reading(self):
        switch_scene("reading")

    def open_journal(self):
        switch_scene("journal")

    def open_settings(self):
        switch_scene("settings")

    # ---------------------------------------------------------
    # Cleanup
    # ---------------------------------------------------------

    def unload(self):
        """
        Called by scene_manager before switching scenes.
        """
        destroy(self.ui_root)
        destroy(self)
