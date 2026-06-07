from ursina import Entity, camera, color, curve, destroy, invoke

from components.ui_button import UIButton
from core.game_state import GameState


class UIPanel(Entity):
    """
    Theme-aware UI panel with optional backdrop dimming and close button.
    """

    def __init__(
        self,
        width=0.9,
        height=0.7,
        position=(0, 0),
        slide_from="bottom",
        show_close=True,
        dim_background=True,
        on_close=None,
        **kwargs
    ):
        parent = kwargs.pop("parent", camera.ui)
        super().__init__(
            parent=parent,
            model="quad",
            scale=(width, height),
            collider="box",
            z=-0.5,
            **kwargs
        )

        self.target_position = position
        self.slide_from = slide_from
        self.on_close = on_close

        theme = GameState().settings.theme
        self.color = {
            "mystic": color.rgba(40, 30, 70, 235),
            "light": color.rgba(240, 240, 255, 235),
            "dark": color.rgba(20, 20, 35, 235),
        }.get(theme, color.rgba(40, 30, 70, 235))

        self.backdrop = None
        if dim_background:
            self.backdrop = Entity(
                parent=parent,
                model="quad",
                color=color.rgba(0, 0, 0, 0),
                scale=(2, 2),
                z=-0.6,
            )

        if show_close:
            self.close_btn = UIButton(
                "X",
                on_click=self.close,
                width=0.06,
                height=0.06,
                position=(width / 2 - 0.05, height / 2 - 0.05),
                parent=self,
            )

        self._set_start_position()
        invoke(self.slide_in, delay=0.05)

    def _set_start_position(self):
        target_x, target_y = self.target_position
        self.x = target_x
        self.y = target_y

        if self.slide_from == "bottom":
            self.y = -1.2
        elif self.slide_from == "top":
            self.y = 1.2
        elif self.slide_from == "left":
            self.x = -1.5
        elif self.slide_from == "right":
            self.x = 1.5

    def slide_in(self):
        if self.backdrop:
            self.backdrop.animate_color(color.rgba(0, 0, 0, 150), duration=0.3)

        target_x, target_y = self.target_position
        if self.slide_from in ("bottom", "top"):
            self.animate_y(target_y, duration=0.35, curve=curve.out_cubic)
        else:
            self.animate_x(target_x, duration=0.35, curve=curve.out_cubic)

    def slide_out(self):
        if self.backdrop:
            self.backdrop.animate_color(color.rgba(0, 0, 0, 0), duration=0.25)

        if self.slide_from == "bottom":
            self.animate_y(-1.2, duration=0.3)
        elif self.slide_from == "top":
            self.animate_y(1.2, duration=0.3)
        elif self.slide_from == "left":
            self.animate_x(-1.5, duration=0.3)
        elif self.slide_from == "right":
            self.animate_x(1.5, duration=0.3)

        invoke(self._destroy_panel, delay=0.32)

    def close(self):
        if self.on_close:
            self.on_close()
        self.slide_out()

    def _destroy_panel(self):
        if self.backdrop:
            destroy(self.backdrop)
        destroy(self)
