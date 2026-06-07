# components/text_input.py

from ursina import Entity, Text, camera, color, invoke
from core.game_state import GameState


class UITextInput(Entity):
    """
    A polished, theme-aware text input field for Arcana Path.
    - Glow border on focus
    - Placeholder text
    - Smooth color transitions
    - Optional submit callback
    """

    def __init__(
        self,
        placeholder: str = "Enter text...",
        width: float = 0.7,
        height: float = 0.09,
        max_chars: int = 200,
        on_submit=None,
        text_color=color.white,
        placeholder_color=color.rgba(200, 200, 200, 120),
        **kwargs
    ):
        parent = kwargs.pop("parent", camera.ui)
        super().__init__(
            parent=parent,
            model="quad",
            scale=(width, height),
            collider="box",
            z=-0.4,
            **kwargs
        )

        self.placeholder = placeholder
        self.max_chars = max_chars
        self.on_submit = on_submit
        self.text_color = text_color
        self.placeholder_color = placeholder_color

        # Theme-aware background
        theme = GameState().settings.theme
        self.color = {
            "mystic": color.rgba(50, 40, 80, 200),
            "light": color.rgba(240, 240, 255, 200),
            "dark": color.rgba(30, 30, 50, 200),
        }[theme]

        # Glow border
        self.glow = Entity(
            parent=self,
            model="quad",
            texture="assets/textures/glow.png",
            color=color.rgba(255, 255, 200, 0),
            scale=(width * 1.3, height * 2),
            z=0.01,
            enabled=False,
        )

        # Text label
        self.text_entity = Text(
            parent=self,
            text=self.placeholder,
            color=self.placeholder_color,
            origin=(-0.48, 0),
            z=-0.01,
            scale=1.1,
        )

        self._focused = False
        self._text = ""

    # ---------------------------------------------------------
    # Focus Handling
    # ---------------------------------------------------------

    def on_mouse_enter(self):
        if not self._focused:
            self.glow.enabled = True
            self.glow.animate_color(color.rgba(255, 255, 200, 60), duration=0.15)

    def on_mouse_exit(self):
        if not self._focused:
            self.glow.animate_color(color.rgba(255, 255, 200, 0), duration=0.15)
            invoke(setattr, self.glow, "enabled", False, delay=0.15)

    def on_click(self):
        """
        Focus the input field.
        """
        self._focused = True
        self.glow.enabled = True
        self.glow.animate_color(color.rgba(255, 255, 200, 120), duration=0.15)

        if self._text == "":
            self.text_entity.text = ""

    # ---------------------------------------------------------
    # Typing Logic
    # ---------------------------------------------------------

    def input(self, key):
        if not self._focused:
            return

        # Submit on Enter
        if key == "enter":
            self._focused = False
            self.glow.animate_color(color.rgba(255, 255, 200, 0), duration=0.2)
            invoke(setattr, self.glow, "enabled", False, delay=0.2)

            if self.on_submit:
                self.on_submit(self._text)
            return

        # Backspace
        if key == "backspace":
            self._text = self._text[:-1]
            self._update_text()
            return

        if key == "space":
            key = " "

        # Ignore special keys
        if len(key) != 1:
            return

        # Character limit
        if len(self._text) >= self.max_chars:
            return

        # Add character
        self._text += key
        self._update_text()

    # ---------------------------------------------------------
    # Internal Helpers
    # ---------------------------------------------------------

    def _update_text(self):
        if self._text == "":
            self.text_entity.text = self.placeholder
            self.text_entity.color = self.placeholder_color
        else:
            self.text_entity.text = self._text
            self.text_entity.color = self.text_color

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def get_text(self) -> str:
        return self._text

    def clear(self):
        self._text = ""
        self._update_text()
