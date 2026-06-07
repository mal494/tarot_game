# scenes/reading_scene.py

from ursina import Entity, Text, camera, color, destroy, invoke
from core.game_state import GameState
from core.tarot_engine import TarotEngine, SpreadType
from core.card_data_loader import CardDataLoader
from components.text_input import UITextInput
from components.ui_button import UIButton
from components.deck import Deck
from components.tarot_card import TarotCard
from fx.particle_fx import FloatingParticles, SparkleBurst
from scenes.scene_manager import switch_scene


class ReadingScene(Entity):
    """
    The main tarot ritual scene:
    - Intention input
    - Shuffle animation
    - Spread selection
    - Card dealing
    - Card flipping
    - Transition to interpretation
    """

    def __init__(self):
        super().__init__()
        self.ui_root = Entity(parent=camera.ui)

        GameState().set_last_scene("reading")

        # ---------------------------------------------------------
        # Background Atmosphere
        # ---------------------------------------------------------
        self.particles = FloatingParticles(
            parent=self,
            count=45,
            area=(6, 4),
            z=1
        )

        # ---------------------------------------------------------
        # Load Tarot Data + Engine
        # ---------------------------------------------------------
        loader = CardDataLoader("assets/data/tarot_cards.json")
        cards = loader.load_cards()
        self.engine = TarotEngine(cards)

        # ---------------------------------------------------------
        # Step 1: Intention Input
        # ---------------------------------------------------------
        self.intention_label = Text(
            "What is your intention for this reading?",
            parent=self.ui_root,
            y=0.35,
            scale=1.3,
            origin=(0, 0),
            color=color.rgba(255, 230, 255, 240)
        )

        self.intention_input = UITextInput(
            placeholder="I seek clarity about...",
            position=(0, 0.15),
            parent=self.ui_root,
        )

        self.begin_btn = UIButton(
            "Begin Ritual",
            on_click=self.begin_ritual,
            position=(0, -0.05),
            parent=self.ui_root,
        )

        # Deck + spread UI (hidden until ritual begins)
        self.deck = None
        self.spread_buttons = []

        # Cards dealt
        self.dealt_cards = []

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
    # Step 1: Begin Ritual
    # ---------------------------------------------------------

    def begin_ritual(self):
        intention = self.intention_input.get_text().strip()
        if not intention:
            return  # ignore empty input

        GameState().start_new_reading(intention, None)

        # Remove input UI
        destroy(self.intention_label)
        destroy(self.intention_input)
        destroy(self.begin_btn)

        # Spawn deck
        self.deck = Deck(
            parent=self,
            position=(0, -0.1),
            scale=(0.7, 1)
        )

        # Spread selection UI
        self._show_spread_selection()

    # ---------------------------------------------------------
    # Step 2: Spread Selection
    # ---------------------------------------------------------

    def _show_spread_selection(self):
        y = 0.25

        def add_button(label, spread_type):
            nonlocal y
            btn = UIButton(
                label,
                on_click=lambda: self.select_spread(spread_type),
                position=(0, y),
                parent=self.ui_root,
            )
            self.spread_buttons.append(btn)
            y -= 0.15

        add_button("Single Card", SpreadType.SINGLE)
        add_button("Three Card Spread", SpreadType.THREE)

    def select_spread(self, spread_type):
        GameState().current_reading.spread_type = spread_type

        # Remove spread buttons
        for b in self.spread_buttons:
            destroy(b)

        # Shuffle animation
        shuffle_duration = GameState().scaled_duration(1.2)
        if not self.deck:
            return

        self.deck.start_shuffle(duration=shuffle_duration)

        # After shuffle, deal cards
        invoke(self._deal_cards, delay=GameState().scaled_duration(1.3))

    # ---------------------------------------------------------
    # Step 3: Deal Cards
    # ---------------------------------------------------------

    def _deal_cards(self):
        spread_type = GameState().current_reading.spread_type

        if spread_type == SpreadType.SINGLE:
            drawn = self.engine.draw_single()
            positions = [(0, 0.2, 0)]
        else:
            drawn = self.engine.draw_three()
            positions = [(-0.4, 0.2, 0), (0, 0.2, 0), (0.4, 0.2, 0)]

        # Save to GameState
        GameState().set_drawn_cards([d.to_dict() for d in drawn])

        # Deal cards visually
        if self.deck:
            self.dealt_cards = self.deck.deal_cards(
                card_data=[d.to_dict() for d in drawn],
                positions=positions,
                on_complete=self._enable_card_flips
            )

    # ---------------------------------------------------------
    # Step 4: Flip Cards
    # ---------------------------------------------------------

    def _enable_card_flips(self):
        for card in self.dealt_cards:
            card.on_reveal = self._on_card_revealed

    def _on_card_revealed(self, card: TarotCard):
        # Sparkle FX
        SparkleBurst(position=card.position)

        # Check if all cards revealed
        if all(c.revealed for c in self.dealt_cards):
            invoke(self._show_continue_button, delay=GameState().scaled_duration(0.4))

    # ---------------------------------------------------------
    # Step 5: Continue to Interpretation
    # ---------------------------------------------------------

    def _show_continue_button(self):
        self.continue_btn = UIButton(
            "Continue to Interpretation",
            on_click=self._go_to_interpretation,
            position=(0, -0.35),
            parent=self.ui_root,
        )

    def _go_to_interpretation(self):
        switch_scene("interpretation")

    # ---------------------------------------------------------
    # Cleanup
    # ---------------------------------------------------------

    def unload(self):
        destroy(self.ui_root)
        destroy(self)
