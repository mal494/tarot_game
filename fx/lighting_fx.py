# fx/lighting_fx.py

from ursina import *
import math


class LightingFX(Entity):
    """
    Global mystical lighting controller for Arcana Path.

    Features:
    - Ambient mystical tint
    - Pulsing ritual light
    - Spotlight highlight for cards or UI
    - Cinematic dimming / brightening
    - Flash effects
    """

    def __init__(
        self,
        ambient_color=color.rgba(40, 25, 60, 180),
        pulse_color=color.rgba(255, 200, 160, 80),
        pulse_speed=1.2,
        **kwargs
    ):
        super().__init__(**kwargs)

        # ---------------------------------------------------------
        # Ambient overlay (scene tint)
        # ---------------------------------------------------------
        self.ambient = Entity(
            parent=camera.ui,
            model="quad",
            color=ambient_color,
            scale=(2, 2),
            z=8
        )

        # ---------------------------------------------------------
        # Pulsing ritual light
        # ---------------------------------------------------------
        self.pulse = Entity(
            parent=camera.ui,
            model="quad",
            texture="assets/textures/glow.png",
            color=pulse_color,
            scale=0.6,
            z=7
        )

        # ---------------------------------------------------------
        # Spotlight for highlighting cards or UI
        # ---------------------------------------------------------
        self.spotlight = Entity(
            parent=camera.ui,
            model="quad",
            texture="assets/textures/spotlight.png",
            color=color.rgba(255, 255, 255, 0),
            scale=0.8,
            z=6
        )

        self.pulse_speed = pulse_speed
        self._t = 0

    # ---------------------------------------------------------
    # Update Loop
    # ---------------------------------------------------------

    def update(self):
        self._t += time.dt * self.pulse_speed # pyright: ignore[reportAttributeAccessIssue]

        # Breathing pulse
        pulse = (math.sin(self._t) + 1) * 0.5
        self.pulse.scale = 0.6 + pulse * 0.25 # pyright: ignore[reportAttributeAccessIssue]
        self.pulse.color = color.rgba(
            255,
            200,
            160,
            int(60 + pulse * 80)
        )

    # ---------------------------------------------------------
    # Spotlight Control
    # ---------------------------------------------------------

    def highlight(self, world_pos, intensity=1.0):
        """
        Moves the spotlight to a world position and fades it in.
        """
        screen_pos = camera.world_to_screen_point(world_pos) # pyright: ignore[reportAttributeAccessIssue]
        self.spotlight.position = (screen_pos[0], screen_pos[1], 6)

        self.spotlight.animate_color(
            color.rgba(255, 255, 255, int(180 * intensity)),
            duration=0.25,
            curve=curve.out_expo
        )

    def clear_highlight(self):
        self.spotlight.animate_color(
            color.rgba(255, 255, 255, 0),
            duration=0.3,
            curve=curve.in_expo
        )

    # ---------------------------------------------------------
    # Cinematic Dimming
    # ---------------------------------------------------------

    def dim(self, amount=0.6, duration=0.4):
        """
        Darkens the scene for dramatic effect.
        """
        self.ambient.animate_color(
            color.rgba(20, 10, 30, int(255 * amount)),
            duration=duration,
            curve=curve.linear
        )

    def brighten(self, duration=0.4):
        """
        Restores ambient lighting.
        """
        self.ambient.animate_color(
            color.rgba(40, 25, 60, 180),
            duration=duration,
            curve=curve.linear
        )

    # ---------------------------------------------------------
    # Flash Effect
    # ---------------------------------------------------------

    def flash(self, intensity=1.0, duration=0.25):
        """
        A bright flash of light — great for:
        - Card flips
        - Interpretation reveal
        - Scene transitions
        """
        flash = Entity(
            parent=camera.ui,
            model="quad", # pyright: ignore[reportAttributeAccessIssue]
            color=color.rgba(255, 255, 255, 0),
            scale=(2, 2),
            z=9
        )

        flash.animate_color(
            color.rgba(255, 255, 255, int(200 * intensity)),
            duration=duration * 0.4,
            curve=curve.out_expo
        )
        invoke(
            flash.animate_color,
            color.rgba(255, 255, 255, 0),
            delay=duration * 0.4,
            duration=duration * 0.6,
            curve=curve.in_expo
        )
        invoke(destroy, flash, delay=duration)
