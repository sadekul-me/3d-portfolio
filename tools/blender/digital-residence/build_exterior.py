# Digital Residence — exterior builder
# Blender 5.2 LTS, 1 unit = 1 meter. Run via tools/blender/digital-residence/run.ps1
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
BLEND_DIR = REPO_ROOT / "assets-source" / "blender" / "digital-residence"
RENDER_DIR = BLEND_DIR / "renders"
GLB_PATH = REPO_ROOT / "public" / "assets" / "world" / "exterior" / "digital-residence-exterior.glb"
BLEND_PATH = BLEND_DIR / "DigitalResidence_Exterior.blend"
STATS_PATH = BLEND_DIR / "build-stats.json"

EXPORTABLE: list[bpy.types.Object] = []
QA_ONLY: list[bpy.types.Object] = []


def ensure_dirs() -> None:
    for path in (BLEND_DIR / "scripts", BLEND_DIR / "textures", BLEND_DIR / "references", RENDER_DIR, GLB_PATH.parent):
        path.mkdir(parents=True, exist_ok=True)


def reset_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.frame_start = 1
    scene.frame_end = 90
    scene.frame_current = 1
    scene.render.fps = 30
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.film_transparent = False
    world = bpy.data.worlds.new("WORLD_Dusk")
    scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    bg = nodes.new("ShaderNodeBackground")
    bg.inputs[0].default_value = (0.022, 0.030, 0.048, 1.0)
    bg.inputs[1].default_value = 0.62
    out = nodes.new("ShaderNodeOutputWorld")
    links.new(bg.outputs[0], out.inputs[0])


def collection(name: str) -> bpy.types.Collection:
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def select_only(obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def set_socket(node: bpy.types.Node, names: tuple[str, ...], value) -> None:
    for name in names:
        socket = node.inputs.get(name)
        if socket is None:
            continue
        socket.default_value = value
        return


def make_material(
    name: str,
    *,
    color: tuple[float, float, float],
    metallic: float = 0.0,
    roughness: float = 0.5,
    transmission: float = 0.0,
    alpha: float = 1.0,
    emission: tuple[float, float, float] | None = None,
    emission_strength: float = 0.0,
    ior: float = 1.45,
) -> bpy.types.Material:
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    principled = nt.nodes.new("ShaderNodeBsdfPrincipled")
    principled.location = (0, 0)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (280, 0)
    nt.links.new(principled.outputs[0], out.inputs[0])
    rgba = (color[0], color[1], color[2], 1.0)
    set_socket(principled, ("Base Color",), rgba)
    set_socket(principled, ("Metallic",), metallic)
    set_socket(principled, ("Roughness",), roughness)
    set_socket(principled, ("IOR",), ior)
    set_socket(principled, ("Alpha",), alpha)
    set_socket(principled, ("Transmission Weight", "Transmission"), transmission)
    if emission is not None:
        set_socket(principled, ("Emission Color", "Emission"), (*emission, 1.0))
        set_socket(principled, ("Emission Strength",), emission_strength)
    if alpha < 1.0 or transmission > 0.0:
        mat.blend_method = "BLEND"
        if hasattr(mat, "shadow_method"):
            mat.shadow_method = "HASHED"
        if hasattr(mat, "use_screen_refraction"):
            mat.use_screen_refraction = True
    return mat


def materials() -> dict[str, bpy.types.Material]:
    return {
        "concrete": make_material("MAT_Concrete_Obsidian", color=(0.028, 0.030, 0.033), roughness=0.58),
        "stone": make_material("MAT_Stone_Plaza", color=(0.045, 0.046, 0.048), roughness=0.72),
        "stone_warm": make_material("MAT_Stone_Warm", color=(0.07, 0.06, 0.052), roughness=0.48),
        "metal": make_material("MAT_Metal_Titanium", color=(0.42, 0.44, 0.47), metallic=1.0, roughness=0.22),
        "graphite": make_material("MAT_Metal_Graphite", color=(0.08, 0.085, 0.09), metallic=0.92, roughness=0.32),
        "glass": make_material(
            "MAT_Glass_Tinted",
            color=(0.04, 0.055, 0.07),
            roughness=0.045,
            transmission=0.92,
            alpha=0.18,
            ior=1.45,
        ),
        "glass_warm": make_material(
            "MAT_Glass_WarmInterior",
            color=(0.12, 0.08, 0.05),
            roughness=0.08,
            transmission=0.55,
            alpha=0.35,
            emission=(1.0, 0.72, 0.42),
            emission_strength=0.45,
        ),
        "led_warm": make_material(
            "MAT_LED_Warm",
            color=(1.0, 0.74, 0.45),
            roughness=0.2,
            emission=(1.0, 0.68, 0.38),
            emission_strength=7.2,
        ),
        "led_cool": make_material(
            "MAT_LED_Cool",
            color=(0.45, 0.78, 0.95),
            roughness=0.18,
            emission=(0.42, 0.76, 0.98),
            emission_strength=5.5,
        ),
        "water": make_material(
            "MAT_Water",
            color=(0.03, 0.05, 0.06),
            roughness=0.02,
            transmission=0.85,
            alpha=0.55,
            metallic=0.08,
            ior=1.33,
        ),
        "hedge": make_material("MAT_Landscape_Hedge", color=(0.03, 0.05, 0.035), roughness=0.9),
        "canopy": make_material("MAT_Landscape_Canopy", color=(0.025, 0.04, 0.03), roughness=0.82),
        "trunk": make_material("MAT_Landscape_Trunk", color=(0.04, 0.03, 0.025), roughness=0.78),
        "interior": make_material(
            "MAT_Interior_Glow",
            color=(0.22, 0.15, 0.08),
            roughness=0.55,
            emission=(1.0, 0.72, 0.42),
            emission_strength=4.8,
        ),
        "rack": make_material("MAT_Tech_Rack", color=(0.04, 0.045, 0.05), metallic=0.4, roughness=0.38),
        "collision": make_material("MAT_CollisionProxy", color=(0.8, 0.1, 0.8), roughness=1.0),
    }


def link(obj: bpy.types.Object, col: bpy.types.Collection, exportable: bool = True) -> bpy.types.Object:
    if obj.name not in col.objects:
        col.objects.link(obj)
    try:
        bpy.context.scene.collection.objects.unlink(obj)
    except RuntimeError:
        pass
    if exportable:
        EXPORTABLE.append(obj)
    else:
        QA_ONLY.append(obj)
    return obj


def make_box(
    name: str,
    size: tuple[float, float, float],
    origin: tuple[float, float, float],
    mat: bpy.types.Material | None,
    col: bpy.types.Collection,
    *,
    bevel: bool = False,
    bevel_width: float = 0.035,
    exportable: bool = True,
    origin_at_base: bool = True,
) -> bpy.types.Object:
    loc_z = origin[2] + size[2] / 2.0 if origin_at_base else origin[2]
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin[0], origin[1], loc_z))
    obj = bpy.context.active_object
    obj.name = name
    obj.data.name = name
    obj.scale = size
    select_only(obj)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat is not None:
        obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new(name="Bevel", type="BEVEL")
        mod.width = bevel_width
        mod.segments = 2
        mod.limit_method = "ANGLE"
        mod.angle_limit = math.radians(40)
        select_only(obj)
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return link(obj, col, exportable=exportable)


def make_empty(name: str, location: tuple[float, float, float], col: bpy.types.Collection) -> bpy.types.Object:
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = "PLAIN_AXES"
    empty.empty_display_size = 0.6
    empty.location = location
    col.objects.link(empty)
    EXPORTABLE.append(empty)
    return empty


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def build_site(mats: dict[str, bpy.types.Material]) -> None:
    env = collection("ENV")
    fx = collection("FX")
    make_box("ENV_Site_Ground", (96.0, 78.0, 0.35), (0.0, 0.0, -0.35), mats["stone"], env, bevel=True, bevel_width=0.02)
    make_box("ENV_Plaza_Inner", (58.0, 46.0, 0.12), (1.5, 2.0, 0.0), mats["stone_warm"], env, bevel=True, bevel_width=0.015)
    make_box("ENV_Approach_Path", (7.2, 22.0, 0.08), (1.2, -18.0, 0.12), mats["stone_warm"], env)
    make_box("ENV_Pool_Basin", (24.0, 8.2, 0.55), (-6.5, -12.5, -0.15), mats["graphite"], env, bevel=True, bevel_width=0.04)
    water = make_box("FX_Water_ReflectingPool", (22.6, 7.0, 0.04), (-6.5, -12.5, 0.22), mats["water"], fx, bevel=False)
    water.data.name = "FX_Water_ReflectingPool"
    make_box("ENV_Pool_Coping", (24.4, 0.35, 0.12), (-6.5, -16.5, 0.22), mats["metal"], env)
    make_box("ENV_Pool_Coping_N", (24.4, 0.35, 0.12), (-6.5, -8.5, 0.22), mats["metal"], env)


def build_stairs_and_podium(mats: dict[str, bpy.types.Material]) -> None:
    env = collection("ENV")
    make_box("ENV_Entrance_Platform", (22.0, 11.0, 1.5), (0.0, -1.2, 0.0), mats["concrete"], env, bevel=True, bevel_width=0.05)
    make_box("ENV_Terrace_Front", (18.0, 3.2, 0.18), (0.0, -7.4, 1.5), mats["stone_warm"], env, bevel=True, bevel_width=0.02)
    for i in range(10):
        make_box(
            f"ENV_Stairs_Tread_{i:02d}",
            (16.0, 0.38, 0.15),
            (0.0, -8.0 - i * 0.38, i * 0.15),
            mats["stone_warm"],
            env,
            bevel=True,
            bevel_width=0.012,
        )
    make_box("ENV_Stair_Cheek_L", (0.45, 4.2, 1.65), (-8.2, -9.7, 0.0), mats["metal"], env, bevel=True)
    make_box("ENV_Stair_Cheek_R", (0.45, 4.2, 1.65), (8.2, -9.7, 0.0), mats["metal"], env, bevel=True)


def build_masses(mats: dict[str, bpy.types.Material]) -> None:
    env = collection("ENV")
    make_box("ENV_Volume_Base", (38.0, 16.4, 4.4), (0.8, 6.4, 1.5), mats["concrete"], env, bevel=True, bevel_width=0.07)
    make_box("ENV_Volume_WestWing", (13.5, 15.0, 6.4), (-17.4, 7.2, 1.5), mats["concrete"], env, bevel=True, bevel_width=0.06)
    make_box("ENV_Volume_EastGlass", (11.2, 13.2, 10.8), (18.2, 6.0, 1.5), mats["graphite"], env, bevel=True, bevel_width=0.05)
    make_box("ENV_Volume_Cantilever", (26.5, 14.8, 3.2), (5.4, 0.2, 8.55), mats["graphite"], env, bevel=True, bevel_width=0.08)
    make_box("ENV_Volume_Core", (5.4, 6.2, 12.4), (0.2, 10.4, 1.5), mats["concrete"], env, bevel=True, bevel_width=0.05)
    make_box("ENV_Roof_Main", (40.0, 18.0, 0.32), (0.8, 6.4, 5.9), mats["graphite"], env, bevel=True, bevel_width=0.04)
    make_box("ENV_Roof_Cantilever", (27.6, 15.6, 0.28), (5.4, 0.2, 11.75), mats["metal"], env, bevel=True, bevel_width=0.03)
    make_box("ENV_Roof_East", (12.0, 14.0, 0.28), (18.2, 6.0, 12.3), mats["metal"], env, bevel=True, bevel_width=0.03)
    make_box("ENV_Canopy_Entrance", (12.5, 4.6, 0.14), (0.0, -5.4, 4.55), mats["metal"], env, bevel=True, bevel_width=0.02)


def build_structure(mats: dict[str, bpy.types.Material]) -> None:
    env = collection("ENV")
    for i, x in enumerate((-7.5, -3.8, 0.0, 3.8, 7.5)):
        make_box(f"ENV_Column_Cantilever_{i+1:02d}", (0.38, 0.38, 7.0), (x, -3.6, 1.5), mats["metal"], env, bevel=True, bevel_width=0.02)
    make_box("ENV_Frame_East_L", (0.22, 13.4, 10.8), (12.75, 6.0, 1.5), mats["metal"], env)
    make_box("ENV_Frame_East_R", (0.22, 13.4, 10.8), (23.65, 6.0, 1.5), mats["metal"], env)
    make_box("ENV_Frame_East_Top", (11.2, 0.22, 0.22), (18.2, -0.5, 12.1), mats["metal"], env)
    for i in range(8):
        x = -23.6 + i * 1.55
        make_box(f"ENV_Fin_West_{i+1:02d}", (0.14, 3.2, 5.8), (x, -0.2, 2.0), mats["graphite"], env)
    for i in range(9):
        x = -6.5 + i * 2.6
        make_box(f"ENV_RoofLouver_{i+1:02d}", (0.18, 14.6, 0.42), (x, 0.2, 12.2), mats["metal"], env)


def build_glazing(mats: dict[str, bpy.types.Material]) -> None:
    env = collection("ENV")
    make_box("ENV_Glass_EastCurtain_S", (10.4, 0.08, 10.2), (18.2, -0.55, 1.7), mats["glass"], env)
    make_box("ENV_Glass_EastCurtain_E", (0.08, 12.4, 10.2), (23.7, 6.0, 1.7), mats["glass"], env)
    make_box("ENV_Glass_Cantilever_S", (25.4, 0.08, 2.95), (5.4, -7.15, 8.65), mats["glass"], env)
    make_box("ENV_Glass_Lobby_S", (8.4, 0.08, 3.5), (0.0, -1.85, 1.6), mats["glass"], env)
    make_box("ENV_Glass_WestRibbon_01", (10.8, 0.07, 1.1), (-17.4, -0.25, 3.2), mats["glass"], env)
    make_box("ENV_Glass_WestRibbon_02", (10.8, 0.07, 1.1), (-17.4, -0.25, 5.6), mats["glass"], env)
    make_box("ENV_Glass_CoreSlot", (0.12, 4.8, 10.6), (2.95, 10.4, 1.8), mats["glass"], env)
    for i in range(7):
        x = 13.5 + i * 1.55
        make_box(f"ENV_Mullion_East_{i+1:02d}", (0.07, 0.12, 10.2), (x, -0.52, 1.7), mats["metal"], env)


def build_entrance(mats: dict[str, bpy.types.Material]) -> tuple[bpy.types.Object, bpy.types.Object]:
    env = collection("ENV")
    prop = collection("PROP")
    make_box("ENV_Portal_Lintel", (9.2, 0.7, 0.35), (0.0, -1.95, 4.85), mats["metal"], env, bevel=True, bevel_width=0.02)
    make_box("ENV_Portal_Jamb_L", (0.4, 0.7, 3.4), (-4.4, -1.95, 1.55), mats["metal"], env)
    make_box("ENV_Portal_Jamb_R", (0.4, 0.7, 3.4), (4.4, -1.95, 1.55), mats["metal"], env)
    make_box("LIGHT_Entrance_LED_01", (8.6, 0.04, 0.04), (0.0, -2.28, 4.72), mats["led_warm"], env)
    make_box("LIGHT_Canopy_Cove_01", (11.8, 0.04, 0.04), (0.0, -5.4, 4.48), mats["led_warm"], env)
    make_box("LIGHT_Cantilever_Cove_S", (25.6, 0.05, 0.05), (5.4, -7.1, 8.52), mats["led_warm"], env)
    make_box("LIGHT_EastCrown_01", (10.6, 0.05, 0.05), (18.2, -0.5, 12.15), mats["led_cool"], env)
    make_box("LIGHT_CoreBlade_01", (0.06, 0.08, 10.2), (2.92, 10.4, 1.9), mats["led_cool"], env)

    left = make_box("PROP_Door_Main_L", (2.05, 0.12, 3.25), (-2.1, -1.98, 1.55), mats["graphite"], prop, bevel=True, bevel_width=0.01)
    right = make_box("PROP_Door_Main_R", (2.05, 0.12, 3.25), (2.1, -1.98, 1.55), mats["graphite"], prop, bevel=True, bevel_width=0.01)
    # Hinge origins at the outer jambs.
    select_only(left)
    bpy.context.scene.cursor.location = (-3.125, -1.98, 1.55)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    select_only(right)
    bpy.context.scene.cursor.location = (3.125, -1.98, 1.55)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")

    left.rotation_euler = (0.0, 0.0, 0.0)
    right.rotation_euler = (0.0, 0.0, 0.0)
    left.keyframe_insert(data_path="rotation_euler", frame=1)
    right.keyframe_insert(data_path="rotation_euler", frame=1)
    left.rotation_euler[2] = math.radians(82)
    right.rotation_euler[2] = math.radians(-82)
    left.keyframe_insert(data_path="rotation_euler", frame=70)
    right.keyframe_insert(data_path="rotation_euler", frame=70)
    left.rotation_euler[2] = 0.0
    right.rotation_euler[2] = 0.0
    return left, right


def build_gate(mats: dict[str, bpy.types.Material]) -> None:
    prop = collection("PROP")
    left = make_box("PROP_Gate_L", (3.4, 0.16, 2.4), (-3.6, -28.5, 0.12), mats["metal"], prop, bevel=True, bevel_width=0.015)
    right = make_box("PROP_Gate_R", (3.4, 0.16, 2.4), (5.0, -28.5, 0.12), mats["metal"], prop, bevel=True, bevel_width=0.015)
    make_box("ENV_Gate_Post_L", (0.35, 0.35, 2.7), (-5.5, -28.5, 0.12), mats["graphite"], collection("ENV"), bevel=True)
    make_box("ENV_Gate_Post_R", (0.35, 0.35, 2.7), (6.9, -28.5, 0.12), mats["graphite"], collection("ENV"), bevel=True)
    left.keyframe_insert(data_path="location", frame=1)
    right.keyframe_insert(data_path="location", frame=1)
    left.location.x = -6.7
    right.location.x = 8.1
    left.keyframe_insert(data_path="location", frame=80)
    right.keyframe_insert(data_path="location", frame=80)
    left.location.x = -3.6
    right.location.x = 5.0


def build_facade_revision(mats: dict[str, bpy.types.Material]) -> None:
    env = collection("ENV")
    groove = mats["graphite"]
    # South facade panelization on the main bar.
    for i in range(15):
        x = -17.8 + i * 2.45
        make_box(f"ENV_FacadeJoint_Base_{i+1:02d}", (0.045, 0.06, 4.15), (x, -1.78, 1.58), groove, env)
    make_box("ENV_FacadeReveal_Base", (36.8, 0.05, 0.06), (0.8, -1.79, 3.55), mats["led_warm"], env)
    # Cantilever soffit grid — aligned to the extended floating slab.
    for i in range(9):
        x = -7.2 + i * 3.15
        make_box(f"ENV_SoffitRib_{i+1:02d}", (0.08, 13.6, 0.07), (x, 0.1, 8.52), mats["metal"], env)
    for i in range(7):
        y = -6.6 + i * 2.2
        make_box(f"ENV_SoffitCross_{i+1:02d}", (25.2, 0.06, 0.06), (5.4, y, 8.51), groove, env)
    # West punched windows.
    for i, z in enumerate((2.7, 5.1)):
        for j in range(4):
            x = -21.4 + j * 2.55
            make_box(f"ENV_Glass_WestPunch_{i+1}{j+1}", (1.7, 0.08, 1.15), (x, -0.28, z), mats["glass"], env)
    # Terrace glass railing.
    make_box("ENV_Railing_Front", (17.4, 0.05, 0.95), (0.0, -8.95, 1.68), mats["glass"], env)
    make_box("ENV_Railing_Cap", (17.6, 0.08, 0.05), (0.0, -8.95, 2.62), mats["metal"], env)
    # Plaza pavement joints.
    for i in range(6):
        make_box(f"ENV_PlazaJoint_{i+1:02d}", (52.0, 0.04, 0.03), (1.5, -8.0 + i * 5.5, 0.125), groove, env)
    # Interior ceiling washes so glass reads as volume.
    make_box("ENV_Interior_LobbyCeiling", (7.6, 8.0, 0.06), (0.0, 3.2, 4.7), mats["interior"], env)
    make_box("ENV_Interior_EastCeiling", (9.6, 11.0, 0.06), (18.2, 6.0, 11.6), mats["interior"], env)
    make_box("ENV_Interior_CantileverCeiling", (24.0, 12.8, 0.05), (5.4, 0.4, 11.45), mats["interior"], env)
    # Cantilever mullions.
    for i in range(9):
        x = -6.8 + i * 3.05
        make_box(f"ENV_Mullion_Cantilever_{i+1:02d}", (0.07, 0.1, 2.9), (x, -7.12, 8.68), mats["metal"], env)
    # Parapets.
    make_box("ENV_Parapet_East", (12.2, 0.18, 0.55), (18.2, -0.95, 12.55), mats["metal"], env)
    make_box("ENV_Parapet_Cantilever", (27.8, 0.18, 0.45), (5.4, -7.5, 12.0), mats["metal"], env)
    # Approach water-edge LEDs.
    for i, x in enumerate((-16.8, -10.2, -3.4)):
        make_box(f"LIGHT_PoolEdge_{i+1:02d}", (0.9, 0.06, 0.03), (x, -16.45, 0.28), mats["led_cool"], env)


def build_interior_hints(mats: dict[str, bpy.types.Material]) -> None:
    env = collection("ENV")
    make_box("ENV_Interior_LobbyGlow", (7.6, 8.0, 0.08), (0.0, 3.2, 1.58), mats["interior"], env)
    make_box("ENV_Interior_EastFloor", (9.6, 11.0, 0.08), (18.2, 6.0, 1.58), mats["interior"], env)
    make_box("ENV_Interior_CantileverFloor", (24.0, 12.8, 0.06), (5.4, 0.4, 8.62), mats["interior"], env)
    for i in range(6):
        make_box(
            f"PROP_ServerHint_{i+1:02d}",
            (0.55, 0.9, 1.8),
            (16.2 + (i % 3) * 1.4, 3.5 + (i // 3) * 2.4, 1.7),
            mats["rack"],
            collection("PROP"),
            bevel=True,
            bevel_width=0.01,
        )
        make_box(
            f"LIGHT_RackEdge_{i+1:02d}",
            (0.58, 0.03, 1.7),
            (16.2 + (i % 3) * 1.4, 3.05 + (i // 3) * 2.4, 1.75),
            mats["led_cool"],
            collection("ENV"),
        )


def build_signage(mats: dict[str, bpy.types.Material]) -> None:
    prop = collection("PROP")
    make_box("PROP_Residence_Sign", (4.8, 0.18, 1.35), (-10.8, -7.15, 1.55), mats["metal"], prop, bevel=True, bevel_width=0.02)
    make_box("PROP_Residence_Sign_Panel", (4.2, 0.04, 0.85), (-10.8, -7.28, 1.72), mats["graphite"], prop)
    make_box("LIGHT_Sign_Reveal_01", (4.3, 0.03, 0.03), (-10.8, -7.32, 2.55), mats["led_warm"], collection("ENV"))


def build_landscape(mats: dict[str, bpy.types.Material]) -> None:
    env = collection("ENV")
    make_box("PROP_Planter_L", (3.6, 8.5, 0.7), (-13.5, -16.0, 0.12), mats["concrete"], env, bevel=True, bevel_width=0.03)
    make_box("PROP_Planter_R", (3.2, 6.0, 0.7), (12.8, -14.5, 0.12), mats["concrete"], env, bevel=True, bevel_width=0.03)
    make_box("PROP_Hedge_L", (3.0, 7.8, 1.1), (-13.5, -16.0, 0.82), mats["hedge"], env)
    make_box("PROP_Hedge_R", (2.6, 5.3, 1.0), (12.8, -14.5, 0.82), mats["hedge"], env)
    make_box("PROP_Planter_East", (8.0, 2.2, 0.55), (18.5, -8.4, 0.12), mats["concrete"], env, bevel=True)
    make_box("PROP_Hedge_East", (7.4, 1.7, 0.9), (18.5, -8.4, 0.67), mats["hedge"], env)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=2.4, location=(-13.5, -18.8, 2.02))
    trunk = bpy.context.active_object
    trunk.name = "PROP_Tree_Trunk_01"
    trunk.data.name = "MESH_Tree_Trunk"
    trunk.data.materials.append(mats["trunk"])
    link(trunk, env)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.35, location=(-13.5, -18.8, 3.7))
    canopy = bpy.context.active_object
    canopy.name = "PROP_Tree_Canopy_01"
    canopy.data.name = "MESH_Tree_Canopy"
    canopy.scale = (1.15, 1.0, 0.75)
    select_only(canopy)
    bpy.ops.object.transform_apply(scale=True)
    canopy.data.materials.append(mats["canopy"])
    link(canopy, env)
    offsets = [(14.6, -17.2), (22.4, -11.5), (-20.5, -10.2), (10.2, -22.4)]
    for i, (x, y) in enumerate(offsets, start=2):
        t = trunk.copy()
        t.data = trunk.data
        t.name = f"PROP_Tree_Trunk_{i:02d}"
        t.location = (x, y, 2.02)
        env.objects.link(t)
        EXPORTABLE.append(t)
        c = canopy.copy()
        c.data = canopy.data
        c.name = f"PROP_Tree_Canopy_{i:02d}"
        c.location = (x, y, 3.7)
        env.objects.link(c)
        EXPORTABLE.append(c)

    for i, x in enumerate((-4.2, -1.4, 1.8, 4.6)):
        make_box(f"PROP_Bollard_{i+1:02d}", (0.16, 0.16, 0.7), (x, -24.5, 0.12), mats["metal"], env, bevel=True, bevel_width=0.01)
        make_box(f"LIGHT_Bollard_{i+1:02d}", (0.12, 0.12, 0.04), (x, -24.5, 0.78), mats["led_warm"], env)


def build_identity_and_drama(mats: dict[str, bpy.types.Material]) -> None:
    env = collection("ENV")
    # West identity blade — vertical silhouette so the house is not a stacked bar.
    make_box("ENV_Blade_Identity", (0.42, 12.0, 14.2), (-25.2, 3.8, 0.12), mats["graphite"], env, bevel=True, bevel_width=0.04)
    make_box("ENV_Blade_Plinth", (3.4, 12.6, 0.32), (-25.2, 3.8, 0.12), mats["metal"], env, bevel=True, bevel_width=0.02)
    make_box("LIGHT_Blade_Slit_01", (0.05, 0.08, 11.6), (-24.98, -2.05, 1.5), mats["led_cool"], env)
    make_box("ENV_Blade_Cap", (0.55, 12.2, 0.16), (-25.2, 3.8, 14.32), mats["metal"], env)

    # Floating east terrace — layered volume over the east glass wing.
    make_box("ENV_Terrace_EastFloat", (8.6, 7.4, 0.22), (18.4, -3.15, 6.35), mats["graphite"], env, bevel=True, bevel_width=0.03)
    make_box("ENV_Terrace_EastRail", (8.4, 0.05, 0.88), (18.4, -6.8, 6.57), mats["glass"], env)
    make_box("ENV_Terrace_EastCap", (8.5, 0.08, 0.04), (18.4, -6.8, 7.44), mats["metal"], env)
    make_box("LIGHT_Terrace_Cove_01", (8.2, 0.04, 0.04), (18.4, -3.15, 6.28), mats["led_warm"], env)
    make_box("ENV_Terrace_Fin_01", (0.12, 0.12, 6.2), (14.2, -6.6, 0.12), mats["metal"], env)
    make_box("ENV_Terrace_Fin_02", (0.12, 0.12, 6.2), (22.6, -6.6, 0.12), mats["metal"], env)

    # Roof monitor / clerestory — readable roof profile from elevation.
    make_box("ENV_Roof_Monitor", (9.2, 3.4, 1.2), (2.2, 8.4, 12.05), mats["graphite"], env, bevel=True, bevel_width=0.03)
    make_box("ENV_Glass_Monitor", (8.8, 0.08, 0.9), (2.2, 6.75, 12.2), mats["glass_warm"], env)
    make_box("LIGHT_Monitor_Cove_01", (8.6, 0.04, 0.04), (2.2, 6.82, 12.08), mats["led_warm"], env)

    # Entrance canopy edge fin — reads as engineered, not a flat lid.
    make_box("ENV_Canopy_EdgeFin", (12.8, 0.08, 0.22), (0.0, -7.7, 4.48), mats["metal"], env, bevel=True, bevel_width=0.01)


def build_collision() -> None:
    col = collection("COL")
    mat = bpy.data.materials["MAT_CollisionProxy"]
    proxies = [
        ("COL_Exterior_Ground", (96.0, 78.0, 0.3), (0.0, 0.0, -0.15)),
        ("COL_Entrance_Platform", (22.0, 11.0, 1.5), (0.0, -1.2, 0.0)),
        ("COL_Stairs", (16.2, 4.2, 1.6), (0.0, -9.8, 0.0)),
        ("COL_Door", (8.6, 0.4, 3.3), (0.0, -1.98, 1.55)),
        ("COL_Entrance_Wall_L", (7.0, 2.0, 4.4), (-8.0, 0.4, 1.5)),
        ("COL_Entrance_Wall_R", (7.0, 2.0, 4.4), (8.0, 0.4, 1.5)),
        ("COL_Building_Base", (38.0, 16.4, 4.4), (0.8, 6.4, 1.5)),
        ("COL_Building_West", (13.5, 15.0, 6.4), (-17.4, 7.2, 1.5)),
        ("COL_Building_East", (11.2, 13.2, 10.8), (18.2, 6.0, 1.5)),
        ("COL_Pool", (24.0, 8.2, 0.8), (-6.5, -12.5, -0.15)),
        ("COL_Identity_Blade", (0.6, 12.2, 14.4), (-25.2, 3.8, 0.12)),
        ("COL_Terrace_East", (8.6, 7.4, 0.4), (18.4, -3.2, 6.2)),
    ]
    for name, size, origin in proxies:
        obj = make_box(name, size, origin, mat, col, bevel=False)
        obj.hide_render = True
        obj.display_type = "WIRE"


def build_anchors() -> None:
    ui = collection("UI")
    make_empty("UI_Entrance_Trigger", (0.0, -8.5, 1.7), ui)
    make_empty("UI_Identity_Sign", (-10.8, -7.4, 2.2), ui)
    make_empty("UI_Direction_AILab", (18.2, -4.0, 2.2), ui)
    make_empty("UI_Direction_Engineering", (-17.4, -2.5, 2.2), ui)
    make_empty("UI_Direction_CommandCenter", (0.2, 12.5, 2.4), ui)
    make_empty("UI_Building_Entry", (0.0, -2.4, 2.4), ui)
    make_empty("UI_Camera_Hero", (0.0, -36.0, 6.4), ui)
    make_empty("UI_Camera_Entrance", (0.0, -16.5, 2.3), ui)
    make_empty("ENV_Exterior_Root", (0.0, 0.0, 0.0), collection("ENV"))


def parent_to_root() -> None:
    root = bpy.data.objects.get("ENV_Exterior_Root")
    if root is None:
        return
    for obj in list(EXPORTABLE):
        if obj != root and obj.parent is None:
            obj.parent = root
            obj.matrix_parent_inverse = root.matrix_world.inverted()


def build_qa_cameras_and_lights() -> None:
    qa = collection("QA")
    specs = [
        ("CAM_Hero_Front", (1.8, -62.0, 12.4), (1.2, 3.5, 5.2)),
        ("CAM_Entrance_Approach", (0.5, -21.5, 2.55), (0.0, -1.8, 3.9)),
        ("CAM_ThreeQuarter", (44.0, -38.0, 16.5), (2.0, 4.5, 5.4)),
        ("CAM_Elevated", (24.0, -34.0, 38.0), (1.5, 4.0, 3.2)),
        ("CAM_Detail_Material", (8.4, -12.2, 2.7), (2.2, -4.2, 3.6)),
    ]
    for name, loc, target in specs:
        cam_data = bpy.data.cameras.new(name)
        if "Elevated" in name:
            cam_data.lens = 28
        elif "Hero" in name or "Three" in name:
            cam_data.lens = 32
        else:
            cam_data.lens = 40
        cam_data.dof.use_dof = False
        cam = bpy.data.objects.new(name, cam_data)
        cam.location = loc
        look_at(cam, target)
        qa.objects.link(cam)
        QA_ONLY.append(cam)

    def add_light(name: str, type_: str, loc: tuple[float, float, float], energy: float, color, size: float = 4.0):
        data = bpy.data.lights.new(name, type_)
        data.energy = energy
        data.color = color
        if type_ == "AREA":
            data.size = size
        light = bpy.data.objects.new(name, data)
        light.location = loc
        qa.objects.link(light)
        QA_ONLY.append(light)
        return light

    moon = add_light("LIGHT_QA_Moon", "SUN", (-18.0, -12.0, 28.0), 7.5, (0.62, 0.72, 0.88))
    moon.rotation_euler = (math.radians(48), math.radians(-14), math.radians(22))
    add_light("LIGHT_QA_Fill", "AREA", (0.0, -28.0, 16.0), 900.0, (1.0, 0.88, 0.76), 14.0)
    add_light("LIGHT_QA_Entrance", "AREA", (0.0, -9.0, 5.4), 420.0, (1.0, 0.74, 0.5), 6.0)
    add_light("LIGHT_QA_East", "AREA", (28.0, -4.0, 9.0), 280.0, (0.7, 0.85, 1.0), 7.0)
    add_light("LIGHT_QA_Rim", "AREA", (-22.0, 18.0, 16.0), 260.0, (0.55, 0.66, 0.82), 10.0)


def configure_eevee(scene: bpy.types.Scene) -> None:
    for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue
    try:
        scene.view_settings.view_transform = "Filmic"
    except TypeError:
        pass
    if hasattr(scene.view_settings, "look"):
        try:
            scene.view_settings.look = "Medium High Contrast"
        except TypeError:
            pass
    eevee = getattr(scene, "eevee", None)
    if eevee is None:
        return
    for attr, value in (
        ("taa_render_samples", 64),
        ("use_shadows", True),
        ("use_raytracing", True),
        ("use_bloom", True),
        ("bloom_intensity", 0.12),
        ("bloom_radius", 6.5),
    ):
        if hasattr(eevee, attr):
            setattr(eevee, attr, value)


def configure_compositor(scene: bpy.types.Scene) -> None:
    # Blender 5.2 moved compositor graphs off Scene.node_tree.
    # QA stills rely on EEVEE exposure and emissive materials instead.
    return


def collect_stats() -> dict:
    meshes = [obj for obj in EXPORTABLE if obj.type == "MESH"]
    tris = 0
    for obj in meshes:
        mesh = obj.data
        mesh.calc_loop_triangles()
        tris += len(mesh.loop_triangles)
    return {
        "blender": bpy.app.version_string,
        "exportableObjects": len(EXPORTABLE),
        "meshObjects": len(meshes),
        "triangleCount": tris,
        "materialCount": len(bpy.data.materials),
        "lightCount": len([obj for obj in bpy.data.objects if obj.type == "LIGHT"]),
        "animationObjects": [obj.name for obj in EXPORTABLE if obj.animation_data and obj.animation_data.action],
        "glb": str(GLB_PATH),
        "blend": str(BLEND_PATH),
    }


def export_glb() -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in EXPORTABLE:
        obj.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=str(GLB_PATH),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_animations=True,
        export_lights=False,
        export_cameras=False,
        export_extras=True,
        export_yup=True,
        export_texcoords=True,
        export_normals=True,
        export_materials="EXPORT",
    )


def render_qa() -> list[str]:
    scene = bpy.context.scene
    configure_eevee(scene)
    configure_compositor(scene)
    scene.render.image_settings.file_format = "PNG"
    rendered: list[str] = []
    for cam in QA_ONLY:
        if cam.type != "CAMERA":
            continue
        scene.camera = cam
        out = RENDER_DIR / f"{cam.name}.png"
        scene.render.filepath = str(out)
        bpy.ops.render.render(write_still=True)
        rendered.append(str(out))
    return rendered


def rename_actions() -> None:
    if bpy.data.actions:
        if "PROP_Door_Main_LAction" in bpy.data.actions:
            bpy.data.actions["PROP_Door_Main_LAction"].name = "DoorOpen"
        # Keep unique clip names readable after glTF merge.
        for action in bpy.data.actions:
            if "Door" in action.name and "Open" not in action.name:
                action.name = "DoorOpen_" + action.name.replace(" ", "")
            if "Gate" in action.name:
                action.name = "GateOpen_" + action.name.replace(" ", "")


def main() -> None:
    ensure_dirs()
    reset_scene()
    mats = materials()
    build_site(mats)
    build_stairs_and_podium(mats)
    build_masses(mats)
    build_structure(mats)
    build_glazing(mats)
    build_entrance(mats)
    build_gate(mats)
    build_interior_hints(mats)
    build_signage(mats)
    build_landscape(mats)
    build_facade_revision(mats)
    build_identity_and_drama(mats)
    build_collision()
    build_anchors()
    parent_to_root()
    build_qa_cameras_and_lights()
    rename_actions()
    bpy.ops.object.select_all(action="DESELECT")
    BLEND_PATH.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    export_glb()
    stats = collect_stats()
    if GLB_PATH.exists():
        stats["glbBytes"] = GLB_PATH.stat().st_size
    rendered = render_qa()
    stats["renders"] = rendered
    STATS_PATH.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    bpy.ops.wm.save_mainfile()
    print("BUILD_STATS", json.dumps(stats))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("BUILD_FAILED", exc, file=sys.stderr)
        raise
