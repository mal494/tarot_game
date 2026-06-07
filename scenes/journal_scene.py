# scenes/journal_scene.py

from ursina import Entity, Text, camera, color, destroy
from core.game_state import GameState
from core.utils import clamp
from journal.journal_manager import JournalManager, JournalCorruptError
from components.ui_button import UIButton
from components.ui_panel import UIPanel
from fx.particle_fx import FloatingParticles
from scenes.scene_manager import switch_scene


class JournalScene(Entity):
    """
    Displays all saved tarot readings in a scrollable list.
    Allows:
    - Viewing a reading
    - Deleting a reading
    - Returning to menu
    """

    def __init__(self):
        super().__init__()
        self.ui_root = Entity(parent=camera.ui)

        GameState().set_last_scene("journal")

        # ---------------------------------------------------------
        # Background Atmosphere
        # ---------------------------------------------------------
        self.particles = FloatingParticles(
            parent=self,
            count=40,
            area=(6, 4),
            z=1
        )

        # ---------------------------------------------------------
        # Title
        # ---------------------------------------------------------
        self.title = Text(
            "Tarot Journal",
            parent=self.ui_root,
            y=0.4,
            scale=2,
            origin=(0, 0),
            color=color.rgba(255, 230, 255, 240)
        )

        # ---------------------------------------------------------
        # Journal Manager
        # ---------------------------------------------------------
        self.manager = JournalManager("assets/data/journal.json")
        self.load_error = None
        try:
            self.entries = self.manager.load_entries()
        except JournalCorruptError as exc:
            self.entries = []
            self.load_error = str(exc)

        # ---------------------------------------------------------
        # Scrollable List
        # ---------------------------------------------------------
        self.scroll_parent = Entity(parent=self.ui_root, y=0.15)
        self.scroll_y = 0

        self.entry_buttons = []
        if self.load_error:
            Text(
                self.load_error,
                parent=self.ui_root,
                y=0.28,
                scale=0.85,
                origin=(0, 0),
                color=color.rgba(255, 180, 180, 240),
                wordwrap=52,
            )
        else:
            self._build_entry_list()

        # Scroll wheel support
        self.scroll_speed = 0.05

        # ---------------------------------------------------------
        # Back Button
        # ---------------------------------------------------------
        self.back_btn = UIButton(
            "Back",
            on_click=lambda: switch_scene("menu"),
            position=(0, -0.4),
            parent=self.ui_root,
        )

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
    # Build Scrollable List
    # ---------------------------------------------------------

    def _build_entry_list(self):
        y = 0

        for entry in self.entries:
            btn = UIButton(
                f"{entry['date']} — {entry['intention']}",
                on_click=lambda e=entry: self._open_entry(e),
                width=0.9,
                height=0.08,
                position=(0, y),
                parent=self.scroll_parent,
            )
            self.entry_buttons.append(btn)
            y -= 0.12

    # ---------------------------------------------------------
    # Scroll Handling
    # ---------------------------------------------------------

    def input(self, key):
        if key == "scroll up":
            self.scroll_y += self.scroll_speed
        elif key == "scroll down":
            self.scroll_y -= self.scroll_speed

        self.scroll_parent.y = clamp(self.scroll_y, -1.2, 0.3)

    # ---------------------------------------------------------
    # Entry Viewer Panel
    # ---------------------------------------------------------

    def _open_entry(self, entry):
        """
        Opens a UIPanel showing full reading details.
        """

        panel = UIPanel(
            parent=self.ui_root,
            width=0.9,
            height=0.75,
            slide_from="bottom",
            show_close=True,
            dim_background=True
        )

        # Title
        Text(
            f"Reading from {entry['date']}",
            parent=panel,
            y=0.32,
            scale=1.3,
            origin=(0, 0)
        )

        # Intention
        Text(
            f"Intention: {entry['intention']}",
            parent=panel,
            y=0.20,
            scale=1,
            origin=(-0.45, 0)
        )

        # Cards
        y_cards = 0.05
        for c in entry["cards"]:
            Text(
                f"- {c['name']} ({c['orientation']})",
                parent=panel,
                y=y_cards,
                origin=(-0.45, 0)
            )
            y_cards -= 0.07

        # Interpretation
        Text(
            "Interpretation:",
            parent=panel,
            y=-0.15,
            origin=(-0.45, 0),
            scale=1.1
        )

        Text(
            entry["interpretation"],
            parent=panel,
            y=-0.28,
            origin=(-0.45, 1),
            scale=0.9,
            wordwrap=40
        )

        # Delete button
        UIButton(
            "Delete Entry",
            on_click=lambda e=entry, p=panel: self._delete_entry(e, p),
            parent=panel,
            position=(0, -0.35),
            width=0.4,
            height=0.08
        )

    # ---------------------------------------------------------
    # Delete Entry
    # ---------------------------------------------------------

    def _delete_entry(self, entry, panel):
        self.manager.delete_entry(entry["id"])
        destroy(panel)

        # Refresh scene
        switch_scene("journal")

    # ---------------------------------------------------------
    # Cleanup
    # ---------------------------------------------------------

    def unload(self):
        destroy(self.ui_root)
        destroy(self)

