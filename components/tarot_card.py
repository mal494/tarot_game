# components/tarot_card.py

import math

from ursina import AmbientLight as AmbientLight, Animation as Animation, Animator as Animator, Audio as Audio, BitMask32 as BitMask32, Bounds as Bounds, BoxCollider as BoxCollider, BoxShape as BoxShape, BulletBoxShape as BulletBoxShape, BulletCapsuleShape as BulletCapsuleShape, BulletDebugNode as BulletDebugNode, BulletPlaneShape as BulletPlaneShape, BulletRigidBodyNode as BulletRigidBodyNode, BulletSphereShape as BulletSphereShape, BulletTriangleMesh as BulletTriangleMesh, BulletTriangleMeshShape as BulletTriangleMeshShape, BulletWorld as BulletWorld, Button as Button, ButtonGroup as ButtonGroup, ButtonList as ButtonList, Capsule as Capsule, CapsuleCollider as CapsuleCollider, CapsuleShape as CapsuleShape, CheckBox as CheckBox, Circle as Circle, Collider as Collider, CollisionBox as CollisionBox, CollisionCapsule as CollisionCapsule, CollisionNode as CollisionNode, CollisionPolygon as CollisionPolygon, CollisionSphere as CollisionSphere, Color as Color, Cone as Cone, ContentTypes as ContentTypes, Cube as Cube, Cursor as Cursor, Cylinder as Cylinder, Default as Default, DirectionalLight as DirectionalLight, Draggable as Draggable, EditorCamera as EditorCamera, Empty as Empty, Entity as Entity, FrameAnimation3d as FrameAnimation3d, Func as Func, Grid as Grid, InputField as InputField, Keys as Keys, LVector3f as LVector3f, Light as Light, LoopingList as LoopingList, Mat3 as Mat3, Mat4 as Mat4, Mesh as Mesh, MeshCollider as MeshCollider, MeshModes as MeshModes, MeshShape as MeshShape, NodePath as NodePath, PandaAmbientLight as PandaAmbientLight, PandaDirectionalLight as PandaDirectionalLight, PandaPointLight as PandaPointLight, PandaSpotLight as PandaSpotLight, Panel as Panel, Path as Path, PhysicsBody as PhysicsBody, Pipe as Pipe, Plane as Plane, PlaneShape as PlaneShape, PointLight as PointLight, PostInitCaller as PostInitCaller, Quad as Quad, Quat as Quat, RigidBody as RigidBody, Scrollable as Scrollable, Sequence as Sequence, Shader as Shader, Sky as Sky, Slider as Slider, SmoothFollow as SmoothFollow, Space as Space, SphereCollider as SphereCollider, SphereShape as SphereShape, SpotLight as SpotLight, Sprite as Sprite, SpriteSheetAnimation as SpriteSheetAnimation, Terrain as Terrain, Text as Text, TextField as TextField, Texture as Texture, ThinSlider as ThinSlider, Tooltip as Tooltip, TransformState as TransformState, Ursina as Ursina, Vec2 as Vec2, Vec3 as Vec3, Vec4 as Vec4, Wait as Wait, WindowPanel as WindowPanel, XUp as XUp, YUp as YUp, ZUp as ZUp, acos as acos, after as after, app as app, application as application, bar as bar, between_color as between_color, boxcast as boxcast, camel_to_snake as camel_to_snake, camera as camera, capsule as capsule, ceil as ceil, chunk_list as chunk_list, clamp as clamp, color as color, copy as copy, cos as cos, cube as cube, curve as curve, debugNP as debugNP, debugNode as debugNode, dedent as dedent, deepcopy as deepcopy, destroy as destroy, distance as distance, distance_2d as distance_2d, distance_xz as distance_xz, dont_cast_shadow as dont_cast_shadow, duplicate as duplicate, e as e, e1 as e1, e2 as e2, enumerate_2d as enumerate_2d, every as every, find_sequence as find_sequence, flatten_completely as flatten_completely, flatten_list as flatten_list, floor as floor, generate_properties_for_class as generate_properties_for_class, grid_layout as grid_layout, ground as ground, held_keys as held_keys, hsv as hsv, import_all_classes as import_all_classes, inf as inf, input as input, input_handler as input_handler, internal_sum as internal_sum, inverselerp as inverselerp, invoke as invoke, lerp as lerp, lerp_angle as lerp_angle, light as light, lit_with_shadows_shader as lit_with_shadows_shader, load_blender_scene as load_blender_scene, load_model as load_model, load_texture as load_texture, m as m, make_gradient as make_gradient, mouse as mouse, multireplace as multireplace, os as os, p as p, pi as pi, platform as platform, platform_body as platform_body, print_info as print_info, print_on_screen as print_on_screen, print_warning as print_warning, printvar as printvar, random as random, raycast as raycast, re as re, rgb as rgb, rotate_around_point_2d as rotate_around_point_2d, round_to_closest as round_to_closest, sample_gradient as sample_gradient, scene as scene, sin as sin, size_list as size_list, slerp as slerp, snake_to_camel as snake_to_camel, sphere as sphere, sqrt as sqrt, sum as sum, sys as sys, terraincast as terraincast, time as time, traceback as traceback, unlit_entity as unlit_entity, window as window, world as world, world_position_to_screen_position as world_position_to_screen_position


from core.game_state import GameState


class TarotCard(Entity):
    """
    A fully interactive tarot card prefab for Ursina.
    - Handles front/back textures
    - Flip animation
    - Hover glow
    - Click interaction callback
    """

    def __init__(
        self,
        front_texture: str,
        back_texture: str = "assets/textures/card_back.png",
        orientation: str = "upright",
        on_reveal=None,
        scale=(0.7, 1),
        **kwargs
    ):
        super().__init__(
            model="quad",
            texture=back_texture,
            scale=scale,
            collider="box",
            **kwargs
        )

        # Textures
        self.front_texture = front_texture
        self.back_texture = back_texture

        # Orientation (upright or reversed)
        self.orientation = orientation
        self.revealed = False

        # Optional callback when card finishes flipping
        self.on_reveal = on_reveal

        # Hover FX
        self._hover_glow = None
        self._create_hover_glow()

        # Floating animation toggle
        self.float_enabled = False
        self._float_phase = 0

    # ---------------------------------------------------------
    # Hover Glow
    # ---------------------------------------------------------

    def _create_hover_glow(self):
        """
        Creates a soft glow behind the card when hovered.
        """
        self._hover_glow = Entity(
            parent=self,
            model="quad",
            texture="assets/textures/glow.png",
            color=color.rgba(255, 255, 200, 0),
            scale=(1.2, 1.6),
            z=0.01,
            enabled=False,
        )

    def on_mouse_enter(self):
        if not self.revealed and self._hover_glow:
            self._hover_glow.enabled = True
            self._hover_glow.animate_color(
                color.rgba(255, 255, 200, 120), duration=0.2
            )

    def on_mouse_exit(self):
        if self._hover_glow and self._hover_glow.enabled:
            self._hover_glow.animate_color(
                color.rgba(255, 255, 200, 0), duration=0.2
            )
            invoke(setattr, self._hover_glow, "enabled", False, delay=0.2)

    def on_click(self):
        self.flip()

    # ---------------------------------------------------------
    # Flip Animation
    # ---------------------------------------------------------

    def flip(self):
        """
        Smooth 180 degree flip animation.
        Texture swaps at the midpoint.
        """
        if self.revealed:
            return

        half_flip = GameState().scaled_duration(0.2)

        # First half of flip
        self.animate_rotation_y(90, duration=half_flip)

        # Swap texture at midpoint
        invoke(self._swap_to_front, delay=half_flip)

        # Second half of flip
        invoke(self._finish_flip, delay=half_flip)

    def _swap_to_front(self):
        """
        Swap to front texture and apply reversed rotation if needed.
        """
        self.texture = self.front_texture

        if self.orientation == "reversed":
            self.rotation_z = 180
        else:
            self.rotation_z = 0

    def _finish_flip(self):
        """
        Complete the flip and trigger callback.
        """
        self.animate_rotation_y(180, duration=GameState().scaled_duration(0.2))
        self.revealed = True

        if self.on_reveal:
            self.on_reveal(self)

    # ---------------------------------------------------------
    # Floating Animation (Optional)
    # ---------------------------------------------------------

    def enable_float(self, enabled=True):
        self.float_enabled = enabled

    def update(self):
        """
        Called every frame by Ursina.
        Handles floating animation if enabled.
        """
        if self.float_enabled:
            self._float_phase += time.dt # type: ignore
            self.y += 0.003 * math.sin(self._float_phase * 2)
