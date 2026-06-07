# fx/aura_effect.py

import math
import random

from ursina import Entity, color, curve, invoke, time


class AuraEffect(Entity):
    """
    Shader-based aura glow effect.
    Attach to any entity (cards, buttons, icons, etc.)

    Features:
    - Soft radial glow
    - Pulsing intensity
    - Optional color shifting
    - Energy surge animation
    """

    def __init__(
        self,
        target: Entity,
        base_color=color.rgba(255, 200, 120, 180),
        pulse_speed=1.5,
        pulse_strength=0.25,
        color_shift=False,
        shift_speed=0.4,
        scale_mult=1.6,
        **kwargs
    ):
        super().__init__(
            parent=target,
            model="quad",
            texture="assets/textures/glow.png",
            color=base_color,
            z=0.01,
            scale=target.scale * scale_mult,
            billboard=True,
            **kwargs
        )

        self.target = target
        self.base_color = base_color
        self.pulse_speed = pulse_speed
        self.pulse_strength = pulse_strength
        self.color_shift = color_shift
        self.shift_speed = shift_speed

        self._t = random.random() * 10

    # ---------------------------------------------------------
    # Update Loop
    # ---------------------------------------------------------

    def update(self):
        self._t += time.dt * self.pulse_speed # pyright: ignore[reportAttributeAccessIssue]

        # Pulsing scale
        pulse = math.sin(self._t) * self.pulse_strength
        self.scale = self.target.scale * (1.6 + pulse)

        # Optional color shifting
        if self.color_shift:
            r = 0.5 + 0.5 * math.sin(self._t * self.shift_speed)
            g = 0.5 + 0.5 * math.sin(self._t * self.shift_speed + 2)
            b = 0.5 + 0.5 * math.sin(self._t * self.shift_speed + 4)
            self.color = color.rgba(
                int(200 + 55 * r),
                int(150 + 55 * g),
                int(100 + 55 * b),
                self.base_color.a
            )

    # ---------------------------------------------------------
    # Energy Surge Animation
    # ---------------------------------------------------------

    def surge(self, intensity=1.8, duration=0.25):
        """
        A quick burst of energy — great for card flips or reveals.
        """
        self.animate_scale(
            self.scale * intensity,
            duration=duration * 0.5,
            curve=curve.out_expo
        )
        invoke(
            self.animate_scale,
            self.target.scale * 1.6,
            delay=duration * 0.5,
            duration=duration * 0.5,
            curve=curve.in_expo
        )
