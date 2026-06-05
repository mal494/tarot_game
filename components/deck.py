# components/deck.py

from typing import List, Callable, Optional
from ursina import AmbientLight as AmbientLight, Animation as Animation, Animator as Animator, Audio as Audio, BitMask32 as BitMask32, Bounds as Bounds, BoxCollider as BoxCollider, BoxShape as BoxShape, BulletBoxShape as BulletBoxShape, BulletCapsuleShape as BulletCapsuleShape, BulletDebugNode as BulletDebugNode, BulletPlaneShape as BulletPlaneShape, BulletRigidBodyNode as BulletRigidBodyNode, BulletSphereShape as BulletSphereShape, BulletTriangleMesh as BulletTriangleMesh, BulletTriangleMeshShape as BulletTriangleMeshShape, BulletWorld as BulletWorld, Button as Button, ButtonGroup as ButtonGroup, ButtonList as ButtonList, Capsule as Capsule, CapsuleCollider as CapsuleCollider, CapsuleShape as CapsuleShape, CheckBox as CheckBox, Circle as Circle, Collider as Collider, CollisionBox as CollisionBox, CollisionCapsule as CollisionCapsule, CollisionNode as CollisionNode, CollisionPolygon as CollisionPolygon, CollisionSphere as CollisionSphere, Color as Color, Cone as Cone, ContentTypes as ContentTypes, Cube as Cube, Cursor as Cursor, Cylinder as Cylinder, Default as Default, DirectionalLight as DirectionalLight, Draggable as Draggable, EditorCamera as EditorCamera, Empty as Empty, Entity as Entity, FrameAnimation3d as FrameAnimation3d, Func as Func, Grid as Grid, InputField as InputField, Keys as Keys, LVector3f as LVector3f, Light as Light, LoopingList as LoopingList, Mat3 as Mat3, Mat4 as Mat4, Mesh as Mesh, MeshCollider as MeshCollider, MeshModes as MeshModes, MeshShape as MeshShape, NodePath as NodePath, PandaAmbientLight as PandaAmbientLight, PandaDirectionalLight as PandaDirectionalLight, PandaPointLight as PandaPointLight, PandaSpotLight as PandaSpotLight, Panel as Panel, Path as Path, PhysicsBody as PhysicsBody, Pipe as Pipe, Plane as Plane, PlaneShape as PlaneShape, PointLight as PointLight, PostInitCaller as PostInitCaller, Quad as Quad, Quat as Quat, RigidBody as RigidBody, Scrollable as Scrollable, Sequence as Sequence, Shader as Shader, Sky as Sky, Slider as Slider, SmoothFollow as SmoothFollow, Space as Space, SphereCollider as SphereCollider, SphereShape as SphereShape, SpotLight as SpotLight, Sprite as Sprite, SpriteSheetAnimation as SpriteSheetAnimation, Terrain as Terrain, Text as Text, TextField as TextField, Texture as Texture, ThinSlider as ThinSlider, Tooltip as Tooltip, TransformState as TransformState, Ursina as Ursina, Vec2 as Vec2, Vec3 as Vec3, Vec4 as Vec4, Wait as Wait, WindowPanel as WindowPanel, XUp as XUp, YUp as YUp, ZUp as ZUp, acos as acos, after as after, app as app, application as application, bar as bar, between_color as between_color, boxcast as boxcast, camel_to_snake as camel_to_snake, camera as camera, capsule as capsule, ceil as ceil, chunk_list as chunk_list, clamp as clamp, color as color, copy as copy, cos as cos, cube as cube, curve as curve, debugNP as debugNP, debugNode as debugNode, dedent as dedent, deepcopy as deepcopy, destroy as destroy, distance as distance, distance_2d as distance_2d, distance_xz as distance_xz, dont_cast_shadow as dont_cast_shadow, duplicate as duplicate, e as e, e1 as e1, e2 as e2, enumerate_2d as enumerate_2d, every as every, find_sequence as find_sequence, flatten_completely as flatten_completely, flatten_list as flatten_list, floor as floor, generate_properties_for_class as generate_properties_for_class, grid_layout as grid_layout, ground as ground, held_keys as held_keys, hsv as hsv, import_all_classes as import_all_classes, inf as inf, input as input, input_handler as input_handler, internal_sum as internal_sum, inverselerp as inverselerp, invoke as invoke, lerp as lerp, lerp_angle as lerp_angle, light as light, lit_with_shadows_shader as lit_with_shadows_shader, load_blender_scene as load_blender_scene, load_model as load_model, load_texture as load_texture, m as m, make_gradient as make_gradient, math as math, mouse as mouse, multireplace as multireplace, os as os, p as p, pi as pi, platform as platform, platform_body as platform_body, print_info as print_info, print_on_screen as print_on_screen, print_warning as print_warning, printvar as printvar, random as random, raycast as raycast, re as re, rgb as rgb, rotate_around_point_2d as rotate_around_point_2d, round_to_closest as round_to_closest, sample_gradient as sample_gradient, scene as scene, sin as sin, size_list as size_list, slerp as slerp, snake_to_camel as snake_to_camel, sphere as sphere, sqrt as sqrt, sum as sum, sys as sys, terraincast as terraincast, time as time, traceback as traceback, unlit_entity as unlit_entity, update as update, window as window, world as world, world_position_to_screen_position as world_position_to_screen_position

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
