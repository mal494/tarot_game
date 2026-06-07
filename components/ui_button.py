# components/ui_button.py

from pathlib import Path

from ursina import * # pyright: ignore[reportWildcardImportFromLibrary]
from core.game_state import GameState


class UIButton(Entity):
    """
    A polished, animated UI button for Arcana Path.
    - Hover glow
    - Press animation
    - Theme-aware styling
    - Optional click sound
    """

    def __init__(
        self,
        text: str,
        on_click=None,
        width=0.45,
        height=0.09,
        base_color=None,
        hover_color=None,
        text_color=color.white,
        sound_path="assets/sounds/ui_click.wav",
        **kwargs
    ):
        parent = kwargs.pop("parent", camera.ui)
        super().__init__(
            parent=parent,
            model="quad",
            scale=(width, height),
            collider="box",
            **kwargs
        )

        self.text_str = text
        self._click_callback = on_click
        self.sound_path = sound_path

        # Theme-aware defaults
        theme = GameState().settings.theme

        if base_color is None:
            base_color = {
                "mystic": color.rgba(80, 60, 120, 180),
                "light": color.rgba(220, 220, 240, 180),
                "dark": color.rgba(40, 40, 60, 180),
            }[theme]

        if hover_color is None:
            hover_color = {
                "mystic": color.rgba(120, 90, 180, 220),
                "light": color.rgba(255, 255, 255, 220),
                "dark": color.rgba(70, 70, 100, 220),
            }[theme]

        self.base_color = base_color
        self.hover_color = hover_color

        # Visuals
        self.color = self.base_color

        self.label = Text(
            parent=self,
            text=self.text_str,
            origin=(0, 0),
            z=-0.01,
            color=text_color,
            scale=1.2,
        )

        # Hover FX
        self._hover_glow = Entity(
            parent=self,
            model="quad",
            texture="assets/textures/glow.png",
            color=color.rgba(255, 255, 200, 0),
            scale=(width * 1.4, height * 2),
            z=0.01,
            enabled=False,
        )

    # ---------------------------------------------------------
    # Hover Events
    # ---------------------------------------------------------

    def on_mouse_enter(self):
        self._hover_glow.enabled = True
        self._hover_glow.animate_color(
            color.rgba(255, 255, 200, 80), duration=0.15
        )
        self.animate_color(self.hover_color, duration=0.15)

    def on_mouse_exit(self):
        self._hover_glow.animate_color(
            color.rgba(255, 255, 200, 0), duration=0.15
        )
        invoke(setattr, self._hover_glow, "enabled", False, delay=0.15)
        self.animate_color(self.base_color, duration=0.15)

    # ---------------------------------------------------------
    # Click Event
    # ---------------------------------------------------------

    def on_click(self):
        """
        Called automatically by Ursina when clicked.
        """
        # Press animation
        self.animate_scale(self.scale * 0.95, duration=0.07)
        invoke(self.animate_scale, self.scale, delay=0.07, duration=0.07)

       
        # Trigger callback
        if self._click_callback:
            self._click_callback()
 # Play sound
        if self.sound_path and Path(self.sound_path).exists():
            Audio(self.sound_path, autoplay=True, volume=GameState().settings.volume)
