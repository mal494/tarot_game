# main.py

import ursina # type: ignore

from scenes.scene_manager import SceneManager, switch_scene


def main():
    # ---------------------------------------------------------
    # Initialize Ursina
    # ---------------------------------------------------------
    app = ursina.Ursina(
        title="Arcana Path",
        borderless=False,
        fullscreen=False,
        vsync=True
    )

    ursina.window.ursina.color = ursina.color.rgb(15, 10, 25)
    ursina.window.exit_button.visible = False

    # ---------------------------------------------------------
    # Initialize Scene Manager
    # ---------------------------------------------------------
    SceneManager.instance()

    # ---------------------------------------------------------
    # Start at Menu Scene
    # ---------------------------------------------------------
    switch_scene("menu")

    # ---------------------------------------------------------
    # Run Game
    # ---------------------------------------------------------
    app.run()


if __name__ == "__main__":
    main()
