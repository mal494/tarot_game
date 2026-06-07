from ursina import Entity, Text, camera, color, destroy, invoke

from ai.async_runner import AsyncRunner
from ai.interpreter import AIInterpreter
from components.ui_button import UIButton
from components.ui_panel import UIPanel
from core.game_state import GameState
from fx.particle_fx import FloatingParticles
from scenes.scene_manager import switch_scene


class InterpretationScene(Entity):
    """
    Displays an offline interpretation for the current reading and saves it to
    the journal.
    """

    def __init__(self):
        super().__init__()
        self.ui_root = Entity(parent=camera.ui)
        self._interpretation_task = None
        GameState().set_last_scene("interpretation")

        self.particles = FloatingParticles(parent=self, count=35, area=(6, 4), z=1)

        self.title = Text(
            "Interpretation",
            parent=self.ui_root,
            y=0.42,
            scale=2,
            origin=(0, 0),
            color=color.rgba(255, 230, 255, 240),
        )

        self.panel = UIPanel(
            parent=self.ui_root,
            width=1.25,
            height=0.78,
            position=(0, -0.02),
            slide_from="bottom",
            show_close=False,
            dim_background=False,
        )

        self.body = Text(
            "Reading the pattern...",
            parent=self.panel,
            x=-0.56,
            y=0.27,
            scale=0.85,
            origin=(-0.5, 0.5),
            wordwrap=58,
        )

        self.menu_btn = UIButton(
            "Menu",
            on_click=lambda: switch_scene("menu"),
            position=(-0.25, -0.43),
            width=0.28,
            parent=self.ui_root,
        )
        self.journal_btn = UIButton(
            "Journal",
            on_click=lambda: switch_scene("journal"),
            position=(0.25, -0.43),
            width=0.28,
            parent=self.ui_root,
        )

        invoke(self._interpret, delay=0.1)

    def _interpret(self):
        self._interpretation_task = AsyncRunner.instance().run(
            AIInterpreter().interpret_current_reading(),
            callback=self._show_interpretation,
        )

    def _show_interpretation(self, interpretation):
        if not interpretation:
            self.body.text = "The interpretation could not be completed. Please return to the menu and try again."
            return
        self.body.text = interpretation["full_text"]

    def unload(self):
        if self._interpretation_task:
            AsyncRunner.instance().cancel(self._interpretation_task)
        destroy(self.ui_root)
        destroy(self)
