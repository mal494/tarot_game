# scenes/scene_manager.py

from importlib import import_module

from ursina import * # type: ignore

class SceneManager:
    """
    Centralized scene controller for Arcana Path.
    Handles:
    - Scene creation
    - Scene switching
    - Fade transitions
    - Cleanup of old scenes
    """

    _instance = None

    @staticmethod
    def instance():
        if SceneManager._instance is None:
            SceneManager()
        return SceneManager._instance

    def __init__(self):
        if SceneManager._instance is not None:
            return

        SceneManager._instance = self

        # Set up the scene registry.
        self.scene_factories = {
            "menu": ("scenes.menu_scene", "MenuScene"),
            "reading": ("scenes.reading_scene", "ReadingScene"),
            "journal": ("scenes.journal_scene", "JournalScene"),
            "settings": ("scenes.settings_scene", "SettingsScene"),
            "interpretation": ("scenes.interpretation_scene", "InterpretationScene"),
        }

        self.current_scene = None
        self.fade_overlay = None

    def switch(self, scene_name: str):
        """
        Switch to a new scene with fade transition.
        """
        if scene_name not in self.scene_factories:
            print(f"[SceneManager] Unknown scene: {scene_name}")
            return

        # Fade-out
        self._fade_out(lambda: self._load_scene(scene_name))

    def _load_scene(self, scene_name: str):
        """
        Destroys old scene and loads new one.
        """
        # Unload old scene
        if self.current_scene:
            if hasattr(self.current_scene, "unload"):
                self.current_scene.unload()
            else:
                destroy(self.current_scene)

        # Create new scene
        module_name, class_name = self.scene_factories[scene_name]
        scene_class = getattr(import_module(module_name), class_name)
        self.current_scene = scene_class()

        # Fade-in
        self._fade_in()

    def _fade_overlay_entity(self):
        """
        Creates the fade overlay if it doesn't exist.
        """
        if not self.fade_overlay:
            self.fade_overlay = Entity(
                parent=camera.ui,
                model="quad",
                color=color.rgba(0, 0, 0, 0),
                scale=(2, 2),
                z=10
            )

    def _fade_out(self, callback):
        """
        Fade screen to black, then call callback.
        """
        self._fade_overlay_entity()
        if self.fade_overlay is None:
            return
        self.fade_overlay.animate_color(
            color.rgba(0, 0, 0, 255),
            duration=0.4,
            curve=curve.linear
        )
        invoke(callback, delay=0.42)

    def _fade_in(self):
        """
        Fade screen from black to transparent.
        """
        self._fade_overlay_entity()
        if self.fade_overlay is None:
            return
        self.fade_overlay.animate_color(
            color.rgba(0, 0, 0, 0),
            duration=0.4,
            curve=curve.linear
        )

# ---------------------------------------------------------
# Global Helper
# ---------------------------------------------------------

def switch_scene(name: str):
    """
    Global function used by all scenes.
    """
    instance = SceneManager.instance()
    if instance:
        instance.switch(name)
