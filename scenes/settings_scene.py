from ursina import *
from core.game_state import GameState
from journal.journal_manager import JournalManager
from components.ui_button import UIButton
from components.ui_panel import UIPanel
from fx.particle_fx import FloatingParticles
from scenes.scene_manager import switch_scene

class SettingsScene(Entity):
    """
    Allows users to adjust:
    - Audio volume
    - Animation speed
    - UI Theme
    - Reset Journal data
    """

    def __init__(self):
        super().__init__()
        self.ui_root = Entity(parent=camera.ui)

        GameState().set_last_scene("settings")

        # ---------------------------------------------------------
        # Background Atmosphere
        # ---------------------------------------------------------
        self.particles = FloatingParticles(
            parent=self,
            count=30,
            area=(6, 4),
            z=1
        )

        # ---------------------------------------------------------
        # Title
        # ---------------------------------------------------------
        self.title = Text(
            "Settings",
            parent=self.ui_root,
            y=0.4,
            scale=2,
            origin=(0, 0),
            color=color.rgba(255, 230, 255, 240)
        )

        # ---------------------------------------------------------
        # Volume Slider
        # ---------------------------------------------------------
        self.volume_label = Text(
            "Master Volume",
            parent=self.ui_root,
            y=0.25,
            origin=(-0.5, 0)
        )

        self.volume_slider = Slider(
            min=0, max=1,
            default=GameState().settings.volume,
            step=0.05,
            dynamic=True,
            parent=self.ui_root,
            y=0.18,
            x=-0.25,
            scale=0.7
        )
        # Slider.on_value_changed is a property that triggers when value changes
        self.volume_slider.on_value_changed = self._set_volume

        # ---------------------------------------------------------
        # Animation Speed Slider
        # ---------------------------------------------------------
        self.anim_label = Text(
            "Animation Speed",
            parent=self.ui_root,
            y=0.05,
            origin=(-0.5, 0)
        )

        self.anim_slider = Slider(
            min=0, max=3,
            default=GameState().settings.animation_speed,
            step=0.05,
            dynamic=True,
            parent=self.ui_root,
            y=-0.02,
            x=-0.25,
            scale=0.7
        )
        self.anim_slider.on_value_changed = self._set_anim_speed

        # ---------------------------------------------------------
        # Theme Selector
        # ---------------------------------------------------------
        self.theme_label = Text(
            "Theme",
            parent=self.ui_root,
            y=-0.15,
            origin=(-0.5, 0)
        )

        self.theme_buttons = [
            UIButton("Mystic", on_click=lambda: self._set_theme("mystic"), position=(-0.3, -0.25), width=0.25, parent=self.ui_root),
            UIButton("Light",  on_click=lambda: self._set_theme("light"),  position=(0, -0.25), width=0.25, parent=self.ui_root),
            UIButton("Dark",   on_click=lambda: self._set_theme("dark"),   position=(0.3, -0.25), width=0.25, parent=self.ui_root),
        ]

        # ---------------------------------------------------------
        # Reset Journal Button
        # ---------------------------------------------------------
        self.reset_btn = UIButton(
            "Reset Journal",
            on_click=self._confirm_reset,
            position=(0, -0.40),
            width=0.45,
            parent=self.ui_root,
        )

        # ---------------------------------------------------------
        # Back Button
        # ---------------------------------------------------------
        self.back_btn = UIButton(
            "Back",
            on_click=lambda: switch_scene("menu"),
            position=(0, -0.55),
            parent=self.ui_root,
        )

        # Fade-in
        self._fade = Entity(
            parent=self.ui_root,
            model="quad",
            color=color.black,
            scale=(2, 2),
            z=2
        )
        self._fade.animate_color(color.rgba(0, 0, 0, 0), duration=0.8)

    # ---------------------------------------------------------
    # Settings Handlers
    # ---------------------------------------------------------

    def _set_volume(self):
        GameState().set_volume(self.volume_slider.value)

    def _set_anim_speed(self):
        GameState().set_animation_speed(self.anim_slider.value)

    def _set_theme(self, theme):
        GameState().set_theme(theme)
        switch_scene("settings")  # reload to apply theme

    # ---------------------------------------------------------
    # Reset Journal
    # ---------------------------------------------------------

    def _confirm_reset(self):
        panel = UIPanel(
            parent=self.ui_root,
            width=0.7,
            height=0.4,
            slide_from="bottom",
            show_close=True,
            dim_background=True
        )

        Text(
            "Reset all journal entries?",
            parent=panel,
            y=0.1,
            scale=1.2,
            origin=(0, 0)
        )

        UIButton(
            "Yes, Reset",
            on_click=lambda p=panel: self._reset_journal(p),
            parent=panel,
            position=(-0.15, -0.15),
            width=0.3
        )

        UIButton(
            "Cancel",
            on_click=panel.close,
            parent=panel,
            position=(0.15, -0.15),
            width=0.3
        )

    def _reset_journal(self, panel):
        manager = JournalManager("assets/data/journal.json")
        manager.reset_journal()
        panel.close()

    # ---------------------------------------------------------
    # Cleanup
    # ---------------------------------------------------------

    def unload(self):
        destroy(self.ui_root)
        destroy(self)
