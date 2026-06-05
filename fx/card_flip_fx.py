# fx/card_flip_fx.py

from pathlib import Path

from ursina import *
from core.game_state import GameState
from fx.aura_effect import AuraEffect
from fx.particle_fx import SparkleBurst


class CardFlipFX:
    """
    Handles the visual flip animation for tarot cards.
    - Smooth 3D flip
    - Optional aura surge
    - Optional sparkle burst
    - Works with any Entity that has a 'front' and 'back' texture
    """

    def __init__(
        self,
        card_entity: Entity,
        flip_duration=0.45,
        surge=True,
        sparkles=True,
        sound_path="assets/sounds/card_flip.wav"
    ):
        self.card = card_entity
        self.flip_duration = flip_duration
        self.surge_enabled = surge
        self.sparkles_enabled = sparkles
        self.sound_path = sound_path
        self.original_scale_x = self.card.scale_x

        # Optional aura
        self.aura = AuraEffect(
            target=self.card,
            base_color=color.rgba(255, 220, 180, 120),
            pulse_speed=1.2,
            pulse_strength=0.15,
            color_shift=False,
            scale_mult=1.8
        )
        self.aura.enabled = False

    # ---------------------------------------------------------
    # Public Flip API
    # ---------------------------------------------------------

    def flip(self, to_front=True, on_complete=None):
        """
        Plays the flip animation.
        - to_front=True: reveal card front
        - to_front=False: flip back to card back
        """

        # Play sound
        if self.sound_path and Path(self.sound_path).exists():
            Audio(self.sound_path, autoplay=True, volume=GameState().settings.volume)

        # Enable aura during flip
        self.aura.enabled = True

        # First half: shrink to edge
        self.card.animate_scale_x(
            0.01,
            duration=self.flip_duration * 0.5,
            curve=curve.in_out_cubic
        )

        # Swap texture at midpoint
        invoke(
            self._swap_texture,
            to_front,
            delay=self.flip_duration * 0.5
        )

        # Second half: expand back out
        invoke(
            self._expand_after_flip,
            to_front,
            on_complete,
            delay=self.flip_duration * 0.5
        )

    # ---------------------------------------------------------
    # Internal Helpers
    # ---------------------------------------------------------

    def _swap_texture(self, to_front):
        """
        Swap the card's texture at the midpoint of the flip.
        """
        if to_front:
            self.card.texture = self.card.front_texture
        else:
            self.card.texture = self.card.back_texture

    def _expand_after_flip(self, to_front, on_complete):
        """
        Expands the card back to full width and triggers FX.
        """
        self.card.animate_scale_x(
            self.original_scale_x,
            duration=self.flip_duration * 0.5,
            curve=curve.out_back
        )

        # FX: aura surge
        if self.surge_enabled:
            self.aura.surge()

        # FX: sparkles
        if self.sparkles_enabled and to_front:
            SparkleBurst(position=self.card.position)

        # Disable aura after a moment
        invoke(
            setattr,
            self.aura,
            "enabled",
            False,
            delay=0.6
        )

        # Callback
        if on_complete:
            invoke(on_complete, delay=self.flip_duration * 0.9)
