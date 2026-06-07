# components/tarot_card.py

import math

from ursina import Entity, color, invoke, time

from core.game_state import GameState


class TarotCard(Entity):
    """
    A fully interactive tarot card prefab for Ursina.
    - Handles front/back textures
    - Flip animation
    - Hover glow
    - Click interaction callback
    """

    def __init__(
        self,
        front_texture: str,
        back_texture: str = "assets/textures/card_back.png",
        orientation: str = "upright",
        on_reveal=None,
        scale=(0.7, 1),
        **kwargs
    ):
        super().__init__(
            model="quad",
            texture=back_texture,
            scale=scale,
            collider="box",
            **kwargs
        )

        # Textures
        self.front_texture = front_texture
        self.back_texture = back_texture

        # Orientation (upright or reversed)
        self.orientation = orientation
        self.revealed = False

        # Optional callback when card finishes flipping
        self.on_reveal = on_reveal

        # Hover FX
        self._hover_glow = None
        self._create_hover_glow()

        # Floating animation toggle
        self.float_enabled = False
        self._float_phase = 0

    # ---------------------------------------------------------
    # Hover Glow
    # ---------------------------------------------------------

    def _create_hover_glow(self):
        """
        Creates a soft glow behind the card when hovered.
        """
        self._hover_glow = Entity(
            parent=self,
            model="quad",
            texture="assets/textures/glow.png",
            color=color.rgba(255, 255, 200, 0),
            scale=(1.2, 1.6),
            z=0.01,
            enabled=False,
        )

    def on_mouse_enter(self):
        if not self.revealed and self._hover_glow:
            self._hover_glow.enabled = True
            self._hover_glow.animate_color(
                color.rgba(255, 255, 200, 120), duration=0.2
            )

    def on_mouse_exit(self):
        if self._hover_glow and self._hover_glow.enabled:
            self._hover_glow.animate_color(
                color.rgba(255, 255, 200, 0), duration=0.2
            )
            invoke(setattr, self._hover_glow, "enabled", False, delay=0.2)

    def on_click(self):
        self.flip()

    # ---------------------------------------------------------
    # Flip Animation
    # ---------------------------------------------------------

    def flip(self):
        """
        Smooth 180 degree flip animation.
        Texture swaps at the midpoint.
        """
        if self.revealed:
            return

        half_flip = GameState().scaled_duration(0.2)

        # First half of flip
        self.animate_rotation_y(90, duration=half_flip)

        # Swap texture at midpoint
        invoke(self._swap_to_front, delay=half_flip)

        # Second half of flip
        invoke(self._finish_flip, delay=half_flip)

    def _swap_to_front(self):
        """
        Swap to front texture and apply reversed rotation if needed.
        """
        self.texture = self.front_texture

        if self.orientation == "reversed":
            self.rotation_z = 180
        else:
            self.rotation_z = 0

    def _finish_flip(self):
        """
        Complete the flip and trigger callback.
        """
        self.animate_rotation_y(180, duration=GameState().scaled_duration(0.2))
        self.revealed = True

        if self.on_reveal:
            self.on_reveal(self)

    # ---------------------------------------------------------
    # Floating Animation (Optional)
    # ---------------------------------------------------------

    def enable_float(self, enabled=True):
        self.float_enabled = enabled

    def update(self):
        """
        Called every frame by Ursina.
        Handles floating animation if enabled.
        """
        if self.float_enabled:
            self._float_phase += time.dt
            self.y += 0.003 * math.sin(self._float_phase * 2)
