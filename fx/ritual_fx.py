# fx/ritual_fx.py

from ursina import *
import math
import random

from fx.particle_fx import FloatingParticles, SparkleBurst
from fx.aura_effect import AuraEffect


class RitualFX(Entity):
    """
    High-level ritual effects for Arcana Path.
    Combines:
    - Ambient pulses
    - Glyph rings
    - Light flares
    - Sparkle bursts
    - Aura surges
    - Cinematic timing

    Use for:
    - Beginning a reading
    - Card draw moments
    - Interpretation reveal
    - Scene transitions
    """

    def __init__(self, parent=camera.ui, **kwargs):
        super().__init__(parent=parent, **kwargs)

        # ---------------------------------------------------------
        # Ambient rotating glyph ring
        # ---------------------------------------------------------
        self.glyph = Entity(
            parent=self,
            model="circle",
            texture="assets/textures/glyph_ring.png",
            scale=0.9,
            color=color.rgba(255, 255, 255, 40),
            z=0.1
        )

        # ---------------------------------------------------------
        # Central pulse light
        # ---------------------------------------------------------
        self.pulse_light = Entity(
            parent=self,
            model="quad",
            texture="assets/textures/glow.png",
            scale=0.3,
            color=color.rgba(255, 220, 180, 0),
            z=0.05
        )

        # ---------------------------------------------------------
        # Floating ambient particles
        # ---------------------------------------------------------
        self.particles = FloatingParticles(
            parent=self,
            count=25,
            area=(0.8, 0.5),
            speed=0.4,
            z=0.2
        )

        self._t = random.random() * 10

    # ---------------------------------------------------------
    # Update Loop
    # ---------------------------------------------------------

    def update(self):
        self._t += time.dt # pyright: ignore[reportAttributeAccessIssue]

        # Rotate glyph ring
        self.glyph.rotation_z += time.dt * 8 # pyright: ignore[reportAttributeAccessIssue]

        # Breathing pulse
        pulse = (math.sin(self._t * 2) + 1) * 0.5
        self.pulse_light.color = color.rgba(
            255,
            220,
            180,
            int(80 + pulse * 80)
        )
        self.pulse_light.scale = 0.3 + pulse * 0.15

    # ---------------------------------------------------------
    # Ritual Actions
    # ---------------------------------------------------------

    def burst(self, intensity=1.4):
        """
        A quick magical burst — great for:
        - Card draw
        - Spread reveal
        - Shuffle completion
        """
        SparkleBurst(position=self.world_position)

        self.pulse_light.animate_scale(
            0.6 * intensity,
            duration=0.15,
            curve=curve.out_expo
        )
        invoke(
            self.pulse_light.animate_scale,
            0.3,
            delay=0.15,
            duration=0.2,
            curve=curve.in_expo
        )

    def surge(self, target: Entity, intensity=1.8):
        """
        Creates a surge of energy around a specific entity.
        Perfect for:
        - Card flips
        - Interpretation reveal
        """
        aura = AuraEffect(
            target=target,
            base_color=color.rgba(255, 200, 120, 140),
            pulse_speed=2.0,
            pulse_strength=0.25,
            scale_mult=2.0
        )
        aura.surge(intensity=intensity)
        invoke(destroy, aura, delay=0.8)

    def flash(self, duration=0.25):
        """
        A full-screen flash of light.
        Great for:
        - Scene transitions
        - Major revelations
        """
        flash = Entity(
            parent=camera.ui,
            model="quad",
            color=color.rgba(255, 255, 255, 0),
            scale=(2, 2),
            z=5
        )

        flash.animate_color(
            color.rgba(255, 255, 255, 180),
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

    def ritual_start(self):
        """
        A cinematic sequence for beginning a reading.
        """
        self.flash(duration=0.4)
        invoke(self.burst, delay=0.15)

    def interpretation_reveal(self, target):
        """
        A layered effect for revealing the AI interpretation panel.
        """
        self.flash(duration=0.3)
        self.surge(target, intensity=2.2)
        invoke(self.burst, delay=0.1)
