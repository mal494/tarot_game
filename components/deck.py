# components/deck.py

import random
from typing import Callable, List, Optional

from ursina import Entity, color, curve, invoke

from components.tarot_card import TarotCard
from core.game_state import GameState


class Deck(Entity):
    """
    A visual tarot deck prefab.
    Handles:
    - stacked card visuals
    - shuffle animation
    - dealing cards to positions
    """

    def __init__(
        self,
        back_texture: str = "assets/textures/card_back.png",
        card_count: int = 78,
        scale=(0.7, 1),
        **kwargs
    ):
        super().__init__(
            model=None,
            **kwargs
        )

        self.back_texture = back_texture
        self.card_count = card_count
        self.scale = scale

        # Visual stack of cards
        self.stack_entities: List[Entity] = []
        self._build_stack()

        # Shuffle animation state
        self._shuffling = False
        self._shuffle_phase = 0

    # ---------------------------------------------------------
    # Build Deck Stack
    # ---------------------------------------------------------

    def _build_stack(self):
        """
        Creates a visual stack of card backs.
        """
        for i in range(self.card_count):
            card = Entity(
                parent=self,
                model="quad",
                texture=self.back_texture,
                scale=self.scale,
                z=i * 0.002,  # slight offset so stack is visible
                color=color.white,
            )
            self.stack_entities.append(card)

    # ---------------------------------------------------------
    # Shuffle Animation
    # ---------------------------------------------------------

    def start_shuffle(self, duration: float = 1.2):
        """
        Begins a visual shuffle animation.
        """
        if self._shuffling:
            return

        self._shuffling = True
        self._shuffle_phase = 0

        # Animate jitter + rotation
        for card in self.stack_entities:
            card.animate_x(card.x + (random.random() - 0.5) * 0.2, duration=duration, curve=curve.in_out_sine)
            card.animate_y(card.y + (random.random() - 0.5) * 0.2, duration=duration, curve=curve.in_out_sine)
            card.animate_rotation_z((random.random() - 0.5) * 20, duration=duration)

        # End shuffle
        invoke(self._end_shuffle, delay=duration)

    def _end_shuffle(self):
        self._shuffling = False

        # Reset positions
        reset_duration = GameState().scaled_duration(0.4)
        for card in self.stack_entities:
            card.animate_position((0, 0, card.z), duration=reset_duration)
            card.animate_rotation_z(0, duration=reset_duration)

    # ---------------------------------------------------------
    # Deal Cards
    # ---------------------------------------------------------

    def deal_cards(
        self,
        card_data: List[dict],
        positions: List[tuple],
        on_complete: Optional[Callable] = None,
    ) -> List[TarotCard]:
        """
        Deals TarotCard entities to given positions.
        Returns the list of spawned TarotCard objects.
        """
        dealt_cards: List[TarotCard] = []
        deal_duration = GameState().scaled_duration(0.6)
        deal_stagger = GameState().scaled_duration(0.15)

        for i, data in enumerate(card_data):
            # Create card entity
            card = TarotCard(
                parent=self.parent,
                front_texture=data["image_path"],
                orientation=data["orientation"],
                position=self.position,
                scale=self.scale,
            )
            dealt_cards.append(card)

            # Animate to spread position
            card.animate_position(
                positions[i],
                duration=deal_duration,
                delay=i * deal_stagger,
                curve=curve.out_cubic,
            )

        # Trigger callback when last card finishes
        if on_complete:
            invoke(on_complete, delay=deal_duration + len(card_data) * deal_stagger)

        return dealt_cards

    # ---------------------------------------------------------
    # Optional Cut Animation
    # ---------------------------------------------------------

    def cut(self, offset: float = 0.3, duration: float = 0.4):
        """
        Simple deck cut animation.
        """
        duration = GameState().scaled_duration(duration)
        half = len(self.stack_entities) // 2

        top_half = self.stack_entities[:half]
        bottom_half = self.stack_entities[half:]

        # Move top half up
        for card in top_half:
            card.animate_y(card.y + offset, duration=duration)

        # Move bottom half down
        for card in bottom_half:
            card.animate_y(card.y - offset, duration=duration)

        # Re-stack
        invoke(self._restack, delay=duration)

    def _restack(self):
        """
        Restores deck to original stacked layout.
        """
        restack_duration = GameState().scaled_duration(0.3)
        for i, card in enumerate(self.stack_entities):
            card.animate_position((0, 0, i * 0.002), duration=restack_duration)
            card.animate_rotation_z(0, duration=restack_duration)
            card.z = i * 0.002
