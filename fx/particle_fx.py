import math
import random

from ursina import Entity, color, curve, destroy, time


class FloatingParticles(Entity):
    """
    Ambient particles that drift upward and wrap around the configured area.
    """

    def __init__(
        self,
        count=40,
        area=(6, 4),
        texture="assets/textures/sparkle.png",
        particle_color=color.rgba(255, 255, 255, 120),
        speed=0.3,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.particles = []
        self.area = area
        self.speed = speed

        for _ in range(count):
            particle = Entity(
                parent=self,
                model="quad",
                texture=texture,
                scale=random.uniform(0.03, 0.08),
                color=particle_color,
                position=(
                    random.uniform(-area[0], area[0]),
                    random.uniform(-area[1], area[1]),
                    random.uniform(0.1, 0.3),
                ),
                billboard=True,
            )
            self.particles.append(particle)

    def update(self):
        for particle in self.particles:
            particle.y += time.dt * self.speed * random.uniform(0.5, 1.2)
            if particle.y > self.area[1]:
                particle.y = -self.area[1]
                particle.x = random.uniform(-self.area[0], self.area[0])
                particle.scale = random.uniform(0.03, 0.08)


class SparkleBurst(Entity):
    """
    Short-lived sparkle flash used for reveals and ritual moments.
    """

    def __init__(
        self,
        position=(0, 0, -0.1),
        texture="assets/textures/sparkle.png",
        sparkle_color=color.white,
        duration=0.4,
        **kwargs
    ):
        super().__init__(
            model="quad",
            texture=texture,
            color=sparkle_color,
            scale=0.1,
            position=position,
            billboard=True,
            **kwargs
        )
        self.animate_scale(0.6, duration=duration * 0.5, curve=curve.out_expo)
        self.animate_color(color.rgba(255, 255, 255, 0), duration=duration)
        destroy(self, delay=duration)


class AuraGlow(Entity):
    """
    Simple pulsing glow that can be parented behind a target entity.
    """

    def __init__(
        self,
        target,
        texture="assets/textures/glow.png",
        base_scale=1.4,
        pulse_amount=0.15,
        pulse_speed=2.0,
        aura_color=color.rgba(255, 220, 180, 120),
        **kwargs
    ):
        super().__init__(
            parent=target,
            model="quad",
            texture=texture,
            color=aura_color,
            scale=target.scale * base_scale,
            z=0.01,
            billboard=True,
            **kwargs
        )
        self.target = target
        self.base_scale = base_scale
        self.pulse_amount = pulse_amount
        self.pulse_speed = pulse_speed
        self._phase = random.random() * math.tau

    def update(self):
        self._phase += time.dt * self.pulse_speed
        self.scale = self.target.scale * (self.base_scale + math.sin(self._phase) * self.pulse_amount)
