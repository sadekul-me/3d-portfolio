# Digital Residence — premium exterior builder
# Blender 5.2 LTS, 1 unit = 1 meter.
from __future__ import annotations

import array
import json
import math
import os
import random
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
BLEND_DIR = REPO_ROOT / "assets-source" / "blender" / "digital-residence"
TEXTURE_DIR = BLEND_DIR / "textures"
GENERATED_DIR = SCRIPT_DIR / "textures" / "generated"
RENDER_DIR = BLEND_DIR / "renders"
GLB_PATH = REPO_ROOT / "public" / "assets" / "world" / "exterior" / "digital-residence-exterior.glb"
BLEND_PATH = BLEND_DIR / "DigitalResidence_Exterior.blend"
STATS_PATH = BLEND_DIR / "build-stats.json"

EXPORTABLE: list[bpy.types.Object] = []
QA_ONLY: list[bpy.types.Object] = []
COLLECTIONS: dict[str, bpy.types.Collection] = {}

COLLECTION_ORDER = [
    "00_GUIDES",
    "01_ARCHITECTURE",
    "02_FACADE",
    "03_GLASS",
    "04_GROUND",
    "05_BOUNDARY",
    "06_GATE",
    "07_LANDSCAPE",
    "08_WATER",
    "09_PROPS",
    "10_LIGHTS",
    "11_COLLISION",
    "12_UI_ANCHORS",
    "13_CAMERAS",
    "14_ANIMATION",
    "90_EXPORT",
    "99_DEBUG",
]


def ensure_dirs() -> None:
    for path in (BLEND_DIR / "scripts", TEXTURE_DIR, BLEND_DIR / "references", RENDER_DIR, GLB_PATH.parent):
        path.mkdir(parents=True, exist_ok=True)


def col(name: str) -> bpy.types.Collection:
    existing = COLLECTIONS.get(name)
    if existing is not None:
        return existing
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    COLLECTIONS[name] = collection
    return collection


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


def hash_noise(x: float, y: float, seed: float) -> float:
    n = math.sin(x * 127.1 + y * 311.7 + seed * 74.7) * 43758.5453
    return n - math.floor(n)


def fbm(x: float, y: float, seed: float) -> float:
    value = 0.0
    amp = 0.5
    freq = 1.0
    for _ in range(4):
        value += amp * hash_noise(x * freq, y * freq, seed)
        freq *= 2.05
        amp *= 0.5
    return value


def load_png_image(name: str, filename: str) -> bpy.types.Image | None:
    path = GENERATED_DIR / filename
    if not path.exists():
        return None
    img = bpy.data.images.load(str(path))
    img.name = name
    if hasattr(img, "alpha_mode"):
        img.alpha_mode = "CHANNEL_PACKED"
    img.pack()
    return img


def make_image(name: str, size: int, painter) -> bpy.types.Image:
    path = TEXTURE_DIR / f"{name}.png"
    img = bpy.data.images.new(name, width=size, height=size, alpha=True)
    pixels = array.array("f", [0.0]) * (size * size * 4)
    for y in range(size):
        v = y / (size - 1)
        for x in range(size):
            u = x / (size - 1)
            sample = painter(u, v, x, y)
            r, g, b = sample[0], sample[1], sample[2]
            a = sample[3] if len(sample) > 3 else 1.0
            i = (y * size + x) * 4
            pixels[i] = r
            pixels[i + 1] = g
            pixels[i + 2] = b
            pixels[i + 3] = a
    img.pixels.foreach_set(pixels)
    img.filepath_raw = str(path)
    img.file_format = "PNG"
    img.save()
    img.pack()
    return img


def paint_stone(u: float, v: float, x: int, y: int) -> tuple[float, float, float]:
    n = fbm(u * 9.0, v * 9.0, 2.2)
    mortar = 1.0 if ((x % 88) < 2 or (y % 48) < 2) else 0.0
    vein = 0.035 * fbm(u * 22.0, v * 4.0, 6.1)
    pit = 0.03 * hash_noise(x * 0.51, y * 0.47, 4.4)
    base = 0.20 + n * 0.10 + vein - pit
    if mortar:
        base *= 0.62
    return (base * 1.04, base * 1.01, base * 0.96)


def paint_concrete(u: float, v: float, x: int, y: int) -> tuple[float, float, float]:
    n = fbm(u * 6.0, v * 6.0, 8.1)
    speckle = 0.025 * hash_noise(x * 0.37, y * 0.41, 3.0)
    g = 0.24 + n * 0.08 + speckle
    return (g * 0.96, g * 0.99, g * 1.05)


def paint_paving(u: float, v: float, x: int, y: int) -> tuple[float, float, float]:
    n = fbm(u * 5.0, v * 5.0, 4.4)
    joint = 1.0 if ((x % 108) < 3 or (y % 108) < 3) else 0.0
    g = 0.26 + n * 0.07
    if joint:
        g *= 0.55
    return (g * 1.02, g * 1.00, g * 0.96)


def paint_wood(u: float, v: float, x: int, y: int) -> tuple[float, float, float]:
    grain = 0.5 + 0.5 * math.sin((u * 28.0 + fbm(u * 4.0, v * 18.0, 1.7) * 1.8) * math.pi)
    warm = 0.28 + grain * 0.16
    return (warm, warm * 0.62, warm * 0.32)


def paint_metal(u: float, v: float, x: int, y: int) -> tuple[float, float, float]:
    n = fbm(u * 22.0, v * 3.0, 11.0)
    g = 0.22 + n * 0.10
    return (g * 1.15, g * 0.82, g * 0.55)


def paint_bronze(u: float, v: float, x: int, y: int) -> tuple[float, float, float]:
    n = fbm(u * 18.0, v * 4.0, 7.2)
    r = 0.34 + n * 0.08
    return (r, r * 0.74, r * 0.50)


def paint_foliage(u: float, v: float, x: int, y: int) -> tuple[float, float, float]:
    n = fbm(u * 14.0, v * 14.0, 6.6)
    g = 0.16 + n * 0.10
    return (g * 0.55, g, g * 0.42)


def _leaf_color(u: float, v: float) -> tuple[float, float, float]:
    n = fbm(u * 26.0, v * 30.0, 5.5)
    vein = 0.5 + 0.5 * math.sin((u * 42.0 + v * 14.0 + n * 2.4) * math.pi)
    speckle = 0.04 * hash_noise(u * 90.0, v * 90.0, 2.2)
    shade = 0.18 + n * 0.18 + vein * 0.04 + speckle
    shade *= 0.78 + v * 0.34
    return (shade * 0.38, shade * 1.12, shade * 0.22)


def paint_canopy(u: float, v: float, x: int, y: int) -> tuple[float, float, float, float]:
    clusters = (
        (0.50, 0.50, 0.38),
        (0.30, 0.36, 0.20),
        (0.72, 0.38, 0.20),
        (0.34, 0.70, 0.18),
        (0.68, 0.72, 0.18),
        (0.50, 0.24, 0.16),
        (0.18, 0.54, 0.14),
        (0.84, 0.56, 0.14),
        (0.46, 0.86, 0.12),
    )
    best_a = 0.0
    best_c = (0.02, 0.05, 0.02)
    for cx, cy, rad in clusters:
        dx = (u - cx) / max(rad, 0.05)
        dy = (v - cy) / (rad * 1.18)
        radius = math.hypot(dx, dy)
        n = fbm(u * 16.0, v * 16.0, cx * 9.0 + cy)
        if radius > 1.02 - n * 0.10:
            continue
        chew = hash_noise(u * 42.0, v * 42.0, cy * 4.0)
        if chew > 0.78 and radius > 0.48:
            continue
        color = _leaf_color(u + cx, v + cy)
        alpha = 1.0 if radius < 0.72 else max(0.0, (1.0 - radius) / 0.30)
        if alpha > best_a:
            best_a = alpha
            best_c = color
    if best_a < 0.10:
        return (0.02, 0.04, 0.02, 0.0)
    return (best_c[0], best_c[1], best_c[2], best_a)


def paint_hedge(u: float, v: float, x: int, y: int) -> tuple[float, float, float, float]:
    n = fbm(u * 7.0, v * 7.0, 1.4)
    top = 0.90 + n * 0.05 + 0.03 * math.sin(u * 18.0)
    if u < 0.03 + n * 0.02 or u > 0.97 - n * 0.02 or v < 0.03 or v > top:
        return (0.02, 0.04, 0.02, 0.0)
    if v > top - 0.10:
        chew = hash_noise(u * 28.0, v * 28.0, 4.7)
        if chew > 0.55 + (top - v) * 3.0:
            return (0.02, 0.04, 0.02, 0.0)
    color = _leaf_color(u * 1.15, v * 0.9)
    alpha = 1.0 if v < top - 0.05 else max(0.0, (top - v) / 0.05)
    return (color[0], color[1], color[2], alpha)


def paint_grass(u: float, v: float, x: int, y: int) -> tuple[float, float, float, float]:
    n = fbm(u * 9.0, v * 22.0, 3.3)
    blade = abs(math.sin((u * 28.0 + n * 2.0) * math.pi))
    if v < 0.04 or v > 0.96 or u < 0.06 or u > 0.94:
        return (0.02, 0.04, 0.01, 0.0)
    if blade < 0.18 and v > 0.12:
        return (0.02, 0.04, 0.01, 0.0)
    shade = 0.12 + n * 0.12 + blade * 0.06
    shade *= 0.7 + v * 0.4
    return (shade * 0.42, shade * 1.05, shade * 0.28, 1.0 if blade > 0.28 else blade / 0.28)


def paint_bark(u: float, v: float, x: int, y: int) -> tuple[float, float, float]:
    n = fbm(u * 18.0, v * 6.0, 9.9)
    g = 0.22 + n * 0.10
    return (g * 1.12, g * 0.78, g * 0.50)


def textured_material(
    name: str,
    image: bpy.types.Image,
    *,
    metallic: float = 0.0,
    roughness: float = 0.55,
    scale: float = 4.0,
    emission: tuple[float, float, float] | None = None,
    emission_strength: float = 0.0,
    transmission: float = 0.0,
    alpha: float = 1.0,
    color: tuple[float, float, float] | None = None,
    ior: float = 1.45,
    use_alpha: bool = False,
    bump_strength: float = 0.0,
) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    principled = nt.nodes.new("ShaderNodeBsdfPrincipled")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (420, 0)
    nt.links.new(principled.outputs[0], out.inputs[0])
    if image is not None:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = image
        tex.location = (-420, 80)
        mapping = nt.nodes.new("ShaderNodeMapping")
        mapping.inputs["Scale"].default_value = (scale, scale, scale)
        mapping.location = (-640, 80)
        coord = nt.nodes.new("ShaderNodeTexCoord")
        coord.location = (-860, 80)
        nt.links.new(coord.outputs["UV"], mapping.inputs["Vector"])
        nt.links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
        nt.links.new(tex.outputs["Color"], principled.inputs["Base Color"])
        if use_alpha:
            nt.links.new(tex.outputs["Alpha"], principled.inputs["Alpha"])
        if bump_strength > 0.0:
            bump = nt.nodes.new("ShaderNodeBump")
            bump.location = (-80, -80)
            bump.inputs["Strength"].default_value = bump_strength
            nt.links.new(tex.outputs["Color"], bump.inputs["Height"])
            nt.links.new(bump.outputs["Normal"], principled.inputs["Normal"])
    elif color is not None:
        set_socket(principled, ("Base Color",), (*color, 1.0))
    set_socket(principled, ("Metallic",), metallic)
    set_socket(principled, ("Roughness",), roughness)
    set_socket(principled, ("IOR",), ior)
    set_socket(principled, ("Alpha",), alpha)
    set_socket(principled, ("Transmission Weight", "Transmission"), transmission)
    if emission is not None:
        set_socket(principled, ("Emission Color", "Emission"), (*emission, 1.0))
        set_socket(principled, ("Emission Strength",), emission_strength)
    if use_alpha:
        try:
            mat.blend_method = "CLIP"
        except TypeError:
            mat.blend_method = "HASHED"
        if hasattr(mat, "alpha_threshold"):
            mat.alpha_threshold = 0.28
        mat.use_backface_culling = False
    elif alpha < 1.0 or transmission > 0.0:
        mat.blend_method = "BLEND"
        if hasattr(mat, "shadow_method"):
            mat.shadow_method = "HASHED"
        if hasattr(mat, "use_screen_refraction"):
            mat.use_screen_refraction = True
    return mat


def untextured_material(
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
    return textured_material(
        name,
        None,
        metallic=metallic,
        roughness=roughness,
        transmission=transmission,
        alpha=alpha,
        emission=emission,
        emission_strength=emission_strength,
        color=color,
        ior=ior,
    )


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
    scene.view_settings.exposure = 1.05
    try:
        scene.view_settings.view_transform = "AgX"
        scene.view_settings.look = "AgX - Medium Contrast"
    except TypeError:
        try:
            scene.view_settings.view_transform = "Filmic"
            scene.view_settings.look = "Medium Contrast"
        except TypeError:
            pass
    world = bpy.data.worlds.new("WORLD_Dusk")
    scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    texcoord = nodes.new("ShaderNodeTexCoord")
    texcoord.location = (-720, 0)
    sep = nodes.new("ShaderNodeSeparateXYZ")
    sep.location = (-500, 0)
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.location = (-280, 0)
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0.22, 0.18, 0.16, 1.0)
    mid = ramp.color_ramp.elements.new(0.34)
    mid.color = (0.10, 0.14, 0.24, 1.0)
    ramp.color_ramp.elements[-1].position = 1.0
    ramp.color_ramp.elements[-1].color = (0.035, 0.055, 0.10, 1.0)
    bg = nodes.new("ShaderNodeBackground")
    bg.location = (40, 0)
    bg.inputs[1].default_value = 1.55
    out = nodes.new("ShaderNodeOutputWorld")
    out.location = (280, 0)
    links.new(texcoord.outputs["Generated"], sep.inputs[0])
    links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bg.inputs["Color"])
    links.new(bg.outputs[0], out.inputs[0])
    for name in COLLECTION_ORDER:
        col(name)


def materials() -> dict[str, bpy.types.Material]:
    stone_img = make_image("TEX_Stone_Black", 512, paint_stone)
    concrete_img = make_image("TEX_Concrete_Graphite", 512, paint_concrete)
    paving_img = make_image("TEX_Paving", 512, paint_paving)
    wood_img = make_image("TEX_Wood_Warm", 512, paint_wood)
    metal_img = make_image("TEX_Metal_Brushed", 512, paint_metal)
    foliage_img = make_image("TEX_Plant_Foliage", 512, paint_foliage)
    canopy_img = load_png_image("TEX_Plant_Canopy", "foliage-cluster-side-a.png") or make_image(
        "TEX_Plant_Canopy", 512, paint_canopy
    )
    canopy_b_img = load_png_image("TEX_Plant_Canopy_B", "foliage-cluster-side-b.png") or canopy_img
    palm_img = load_png_image("TEX_Plant_Palm", "foliage-cluster-palm.png") or canopy_img
    palm_far_img = load_png_image("TEX_Plant_Palm_Distant", "tree-palm-distant.png") or palm_img
    foam_img = load_png_image("TEX_Water_Foam", "water-foam-shore.png")
    rock_img = load_png_image("TEX_Rock_Basalt", "rock-basalt-albedo.png") or make_image(
        "TEX_Rock_Basalt", 512, paint_stone
    )
    bark_img = make_image("TEX_Plant_Trunk", 512, paint_bark)
    hedge_img = make_image("TEX_Plant_Hedge", 512, paint_hedge)
    bronze_img = make_image("TEX_Metal_Bronze", 512, paint_bronze)
    grass_img = make_image("TEX_Plant_Grass", 512, paint_grass)
    mats = {
        "stone": textured_material(
            "MAT_Stone_Black", stone_img, roughness=0.62, scale=2.4, bump_strength=0.22
        ),
        "concrete": textured_material(
            "MAT_Concrete_Graphite", concrete_img, roughness=0.54, scale=2.1, bump_strength=0.12
        ),
        "concrete_warm": textured_material(
            "MAT_Concrete_Warm", concrete_img, roughness=0.50, scale=1.9, bump_strength=0.10
        ),
        "paving": textured_material(
            "MAT_Paving", paving_img, roughness=0.16, scale=2.2, bump_strength=0.08
        ),
        "wood": textured_material(
            "MAT_Wood_Warm", wood_img, roughness=0.40, scale=1.5, bump_strength=0.14
        ),
        "metal": textured_material(
            "MAT_Metal_Brushed", metal_img, metallic=0.72, roughness=0.26, scale=6.0, bump_strength=0.05
        ),
        "bronze": textured_material(
            "MAT_Metal_Bronze", bronze_img, metallic=0.82, roughness=0.32, scale=4.2, bump_strength=0.06
        ),
        "metal_dark": untextured_material("MAT_Metal_Dark", color=(0.10, 0.105, 0.11), metallic=0.28, roughness=0.40),
        "glass": untextured_material(
            "MAT_Glass_Smoked",
            color=(0.14, 0.16, 0.18),
            roughness=0.04,
            transmission=0.0,
            alpha=0.16,
        ),
        "glass_clear": untextured_material(
            "MAT_Glass_Clear",
            color=(0.18, 0.20, 0.22),
            roughness=0.03,
            transmission=0.0,
            alpha=0.09,
        ),
        "led_warm": untextured_material(
            "MAT_LED_Warm",
            color=(1.0, 0.78, 0.42),
            roughness=0.18,
            emission=(1.0, 0.72, 0.38),
            emission_strength=12.0,
        ),
        "led_cool": untextured_material(
            "MAT_LED_Cool",
            color=(0.40, 0.78, 0.92),
            roughness=0.2,
            emission=(0.32, 0.70, 0.92),
            emission_strength=1.6,
        ),
        "interior": untextured_material(
            "MAT_Interior_Warm",
            color=(0.90, 0.62, 0.36),
            roughness=0.38,
            emission=(1.0, 0.76, 0.44),
            emission_strength=11.0,
        ),
        "interior_wall": untextured_material("MAT_Interior_Wall", color=(0.42, 0.36, 0.30), roughness=0.62),
        "sign": untextured_material(
            "MAT_Sign_Champagne",
            color=(0.68, 0.54, 0.36),
            metallic=0.88,
            roughness=0.28,
            emission=(0.92, 0.72, 0.38),
            emission_strength=0.95,
        ),
        "sign_back": untextured_material(
            "MAT_Sign_Backlight",
            color=(0.22, 0.14, 0.07),
            roughness=0.58,
            emission=(1.0, 0.68, 0.32),
            emission_strength=2.8,
        ),
        "sign_zone": untextured_material(
            "MAT_Sign_Zone",
            color=(0.86, 0.88, 0.90),
            metallic=0.42,
            roughness=0.32,
            emission=(0.92, 0.94, 0.96),
            emission_strength=0.85,
        ),
        "water": untextured_material(
            "MAT_Water",
            color=(0.08, 0.10, 0.11),
            roughness=0.03,
            transmission=0.0,
            alpha=0.38,
            metallic=0.08,
            ior=1.33,
        ),
        "rock": textured_material(
            "MAT_Rock_Basalt", rock_img, roughness=0.84, scale=1.45, bump_strength=0.32
        ),
        "foliage": textured_material("MAT_Plant_Foliage", foliage_img, roughness=0.8, scale=3.5),
        "canopy": textured_material(
            "MAT_Plant_Canopy",
            canopy_img,
            roughness=0.78,
            scale=1.0,
            use_alpha=True,
        ),
        "canopy_b": textured_material(
            "MAT_Plant_Canopy_B",
            canopy_b_img,
            roughness=0.78,
            scale=1.0,
            use_alpha=True,
        ),
        "palm": textured_material(
            "MAT_Plant_Palm",
            palm_img,
            roughness=0.76,
            scale=1.0,
            use_alpha=True,
        ),
        "palm_far": textured_material(
            "MAT_Plant_Palm_Distant",
            palm_far_img,
            roughness=0.74,
            scale=1.0,
            use_alpha=True,
        ),
        "hedge": textured_material(
            "MAT_Plant_Hedge",
            hedge_img,
            roughness=0.76,
            scale=1.0,
            use_alpha=True,
        ),
        "trunk": textured_material(
            "MAT_Plant_Trunk", bark_img, roughness=0.78, scale=1.8, bump_strength=0.26
        ),
        "grass": textured_material("MAT_Plant_Grass", grass_img, roughness=0.72, scale=1.0, use_alpha=True),
        "foam": textured_material(
            "MAT_Water_Foam",
            foam_img or canopy_img,
            roughness=0.42,
            scale=1.0,
            use_alpha=True,
        ),
        "rack": untextured_material("MAT_Tech_Rack", color=(0.14, 0.13, 0.12), metallic=0.22, roughness=0.42),
        "collision": untextured_material("MAT_CollisionProxy", color=(0.8, 0.1, 0.8), roughness=1.0),
    }
    return mats


def link(obj: bpy.types.Object, collection: bpy.types.Collection, exportable: bool = True) -> bpy.types.Object:
    if obj.name not in collection.objects:
        collection.objects.link(obj)
    try:
        bpy.context.scene.collection.objects.unlink(obj)
    except RuntimeError:
        pass
    if exportable:
        EXPORTABLE.append(obj)
    else:
        QA_ONLY.append(obj)
    return obj


def unwrap_cube(obj: bpy.types.Object, cube_size: float = 4.0) -> None:
    select_only(obj)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.cube_project(cube_size=cube_size, correct_aspect=True, clip_to_bounds=False, scale_to_bounds=False)
    bpy.ops.object.mode_set(mode="OBJECT")


def make_box(
    name: str,
    size: tuple[float, float, float],
    origin: tuple[float, float, float],
    mat: bpy.types.Material | None,
    collection: bpy.types.Collection,
    *,
    bevel: bool = False,
    bevel_width: float = 0.03,
    exportable: bool = True,
    origin_at_base: bool = True,
    unwrap: bool = True,
) -> bpy.types.Object:
    loc_z = origin[2] + size[2] / 2.0 if origin_at_base else origin[2]
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin[0], origin[1], loc_z))
    obj = bpy.context.active_object
    obj.name = name
    obj.data.name = name
    obj.scale = size
    select_only(obj)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new(name="Bevel", type="BEVEL")
        mod.width = bevel_width
        mod.segments = 2
        mod.limit_method = "ANGLE"
        mod.angle_limit = math.radians(40)
        select_only(obj)
        bpy.ops.object.modifier_apply(modifier=mod.name)
    if mat is not None:
        obj.data.materials.append(mat)
    if unwrap:
        unwrap_cube(obj, cube_size=max(size) * 0.65)
    return link(obj, collection, exportable=exportable)


def join_objects(name: str, objects: list[bpy.types.Object], collection: bpy.types.Collection) -> bpy.types.Object:
    kept = [obj for obj in objects if obj is not None]
    if not kept:
        raise ValueError(name)
    if len(kept) == 1:
        kept[0].name = name
        kept[0].data.name = name
        return kept[0]
    bpy.ops.object.select_all(action="DESELECT")
    for obj in kept:
        obj.select_set(True)
        if obj in EXPORTABLE:
            EXPORTABLE.remove(obj)
    bpy.context.view_layer.objects.active = kept[0]
    bpy.ops.object.join()
    obj = bpy.context.active_object
    obj.name = name
    obj.data.name = name
    if obj not in EXPORTABLE:
        EXPORTABLE.append(obj)
    return obj


def make_empty(name: str, location: tuple[float, float, float], collection: bpy.types.Collection) -> bpy.types.Object:
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = "PLAIN_AXES"
    empty.empty_display_size = 0.6
    empty.location = location
    collection.objects.link(empty)
    EXPORTABLE.append(empty)
    return empty


_SIGN_FONT = None


def sign_font():
    global _SIGN_FONT
    if _SIGN_FONT is not None:
        return _SIGN_FONT
    for candidate in (
        Path(r"C:\Windows\Fonts\segoeuib.ttf"),
        Path(r"C:\Windows\Fonts\calibrib.ttf"),
        Path(r"C:\Windows\Fonts\arialbd.ttf"),
        Path(r"C:\Windows\Fonts\arial.ttf"),
    ):
        if candidate.exists():
            _SIGN_FONT = bpy.data.fonts.load(str(candidate))
            return _SIGN_FONT
    return None


def face_basis(normal: Vector) -> Matrix:
    n = Vector(normal).normalized()
    up = Vector((0.0, 0.0, 1.0))
    x_axis = up.cross(n)
    if x_axis.length < 0.08:
        x_axis = Vector((0.0, 1.0, 0.0)).cross(n)
    x_axis.normalize()
    y_axis = n.cross(x_axis).normalized()
    return Matrix(
        (
            (x_axis.x, y_axis.x, n.x, 0.0),
            (x_axis.y, y_axis.y, n.y, 0.0),
            (x_axis.z, y_axis.z, n.z, 0.0),
            (0.0, 0.0, 0.0, 1.0),
        )
    )


def make_face_lettering(
    name: str,
    body: str,
    *,
    face_point: tuple[float, float, float],
    normal: tuple[float, float, float],
    size: float,
    extrude: float,
    mat: bpy.types.Material,
    collection: bpy.types.Collection,
    offset: float = 0.018,
    space: float = 0.90,
    bevel_depth: float | None = None,
) -> bpy.types.Object:
    bpy.ops.object.text_add(location=(0.0, 0.0, 0.0))
    obj = bpy.context.active_object
    curve = obj.data
    curve.body = body
    curve.size = size
    curve.extrude = extrude
    curve.bevel_depth = bevel_depth if bevel_depth is not None else min(0.0018, max(0.0006, extrude * 0.28))
    curve.space_character = space
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    font = sign_font()
    if font is not None:
        curve.font = font
    select_only(obj)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.active_object
    obj.name = name
    obj.data.name = name
    n = Vector(normal).normalized()
    origin = Vector(face_point) + n * offset
    basis = face_basis(n)
    basis.translation = origin
    obj.matrix_world = basis
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.location = origin
    if mat is not None:
        obj.data.materials.clear()
        obj.data.materials.append(mat)
    return link(obj, collection)


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def build_ground(mats: dict[str, bpy.types.Material]) -> None:
    ground = col("04_GROUND")
    make_box(
        "ENV_Site_Ground",
        (38.0, 28.0, 0.45),
        (0.0, 1.2, -0.45),
        mats["stone"],
        ground,
        bevel=True,
        bevel_width=0.08,
    )
    make_box("ENV_Plaza_Wet", (36.0, 30.0, 0.08), (1.0, -2.0, 0.0), mats["paving"], ground, bevel=True, bevel_width=0.012)
    make_box("ENV_Approach_Path", (9.2, 22.0, 0.07), (0.0, -14.8, 0.08), mats["paving"], ground)
    joints = []
    for i in range(9):
        joints.append(
            make_box(
                f"ENV_PavingJoint_{i:02d}",
                (34.0, 0.05, 0.025),
                (1.0, -16.0 + i * 4.0, 0.09),
                mats["metal_dark"],
                ground,
                exportable=False,
                unwrap=False,
            )
        )
    join_objects("ENV_Paving_Joints", joints, ground)
    build_island_terrain(mats)


def make_rock(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    mat: bpy.types.Material,
    collection: bpy.types.Collection,
    rng: random.Random,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.name = name
    obj.scale = scale
    obj.rotation_euler = (
        rng.uniform(-0.45, 0.45),
        rng.uniform(-0.35, 0.35),
        rng.uniform(0.0, math.tau),
    )
    select_only(obj)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    mesh = obj.data
    for vert in mesh.vertices:
        n = hash_noise(vert.co.x * 1.7 + 2.1, vert.co.y * 1.4, 3.3)
        direction = vert.co.copy()
        if direction.length > 0.001:
            direction.normalize()
            vert.co += direction * (n - 0.48) * (0.22 * max(scale))
    mesh.update()
    if mat is not None:
        obj.data.materials.append(mat)
    unwrap_cube(obj, cube_size=max(scale) * 0.55)
    return link(obj, collection)


def island_noise(x: float, z: float) -> float:
    return (
        0.46 * math.sin(x * 0.19 + z * 0.16)
        + 0.28 * math.sin(x * 0.47 - z * 0.39)
        + 0.16 * math.sin(x * 0.93 + z * 0.71)
        + 0.08 * math.sin(x * 1.85 - z * 1.42)
        + 0.04 * math.sin(x * 3.1 + z * 2.4)
    )


def island_height_field(x: float, y: float) -> float:
    """Blender XY ground → Z height. Matches runtime islandHeight.ts (Three Z = -Blender Y)."""
    tx, tz = x, -y
    n = island_noise(tx, tz)
    nx = (tx + 3.2) / 21.4
    nz_south = max(0.0, tz - 6.8) / 10.6
    nz_north = max(0.0, -tz - 8.0) / 13.5
    u = math.sqrt(nx * nx * 0.92 + max(nz_south, nz_north * 0.72) ** 2) + 0.08 * island_noise(tx * 0.22, tz * 0.2)
    gorge = math.exp(-((tx + 11.5) ** 2) / 5.4) * math.exp(-((tz - 11.8) ** 2) / 36.0) * (1.0 if tz > 6.5 else 0.15)
    path = math.exp(-(tx * tx) / 16.0) * max(0.0, min(1.0, (tz - 6.2) / 16.0))
    west = math.exp(-((tx + 28.2) ** 2) / 28.0) * math.exp(-(tz * tz) / 40.0)
    if u < 0.92:
        z = 0.04 + n * 0.03
    elif u < 1.18:
        t = (u - 0.92) / 0.26
        z = 0.04 - t * 0.62 + n * 0.07
    elif u < 1.48:
        t = (u - 1.18) / 0.30
        z = -0.58 - t * 0.72 + n * 0.11
    elif u < 1.82:
        t = (u - 1.48) / 0.34
        z = -1.30 - t * 0.28 + n * 0.09
    elif u < 2.12:
        t = (u - 1.82) / 0.30
        z = -1.58 - t * 0.42 + n * 0.07
    else:
        z = -2.12 + n * 0.04
    return z - path * 0.38 - gorge * 1.35 + west * 0.22


def build_island_terrain(mats: dict[str, bpy.types.Material]) -> None:
    ground = col("04_GROUND")
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=120, y_subdivisions=104, size=1.0, location=(0.0, -2.0, 0.0))
    terrain = bpy.context.active_object
    terrain.name = "ENV_Island_Terrain"
    terrain.data.name = "ENV_Island_Terrain"
    terrain.scale = (72.0, 64.0, 1.0)
    select_only(terrain)
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=True)
    for vert in terrain.data.vertices:
        vert.co.z = island_height_field(vert.co.x, vert.co.y)
    terrain.data.update()
    terrain.data.materials.append(mats["rock"])
    unwrap_cube(terrain, cube_size=8.0)
    link(terrain, ground)
    make_box("ENV_Terrace_Retain_W", (9.4, 0.38, 0.95), (-11.2, -8.9, -0.28), mats["stone"], ground, bevel=True)
    make_box("ENV_Terrace_Retain_E", (8.8, 0.36, 0.88), (9.6, -8.7, -0.22), mats["stone"], ground, bevel=True)
    make_box("ENV_Entrance_Bridge", (8.2, 6.4, 0.28), (0.0, -9.6, -0.18), mats["paving"], ground, bevel=True)
    make_box("ENV_Waterfall_Channel", (6.6, 0.55, 1.85), (-11.6, -9.4, 0.15), mats["stone"], ground, bevel=True)
    rng = random.Random(17)
    rocks: list[bpy.types.Object] = []
    for i in range(18):
        theta = (i / 18.0) * 1.35 * math.pi - 0.22
        radius = 20.4 + rng.uniform(0.0, 5.2)
        x = math.cos(theta) * radius * 0.92 - 2.4
        y = -(14.5 + math.sin(theta) * 8.4 + rng.uniform(0.0, 2.4))
        z = island_height_field(x, y) - 0.12
        rocks.append(
            make_rock(
                f"ENV_Shore_Break_{i:02d}",
                (x, y, z),
                (rng.uniform(0.35, 1.15), rng.uniform(0.28, 0.9), rng.uniform(0.32, 1.05)),
                mats["rock"],
                ground,
                rng,
            )
        )
    join_objects("ENV_Shore_Breakup", rocks, ground)


def build_portfolio_bays(mats: dict[str, bpy.types.Material]) -> None:
    facade = col("02_FACADE")
    props = col("09_PROPS")
    zones = [
        ("ENV_Bay_Engineering", "PROP_Zone_02", "02", "ENGINEERING WING", (2.95, 0.28, 1.85), (-16.8, -7.15, 6.8)),
        ("ENV_Bay_AILab", "PROP_Zone_03", "03", "AI LAB", (2.85, 0.28, 1.78), (16.6, -6.4, 9.4)),
        ("ENV_Bay_Projects", "PROP_Zone_04", "04", "PROJECTS GALLERY", (2.65, 0.26, 1.55), (8.8, -7.55, 6.35)),
        ("ENV_Bay_Architecture", "PROP_Zone_05", "05", "ARCHITECTURE CORE", (2.65, 0.26, 1.52), (-8.4, -7.45, 5.15)),
        ("ENV_Bay_Command", "PROP_Zone_06", "06", "COMMAND CENTER", (3.1, 0.26, 1.62), (2.4, -4.2, 12.35)),
    ]
    for name, zone_id, number, title, size, loc in zones:
        make_box(name, size, loc, mats["bronze"], facade, bevel=True, bevel_width=0.03)
        make_box(
            name + "_Recess",
            (size[0] - 0.22, 0.08, size[2] - 0.28),
            (loc[0], loc[1] - 0.12, loc[2] + 0.14),
            mats["metal_dark"],
            facade,
        )
        front_y = loc[1] - size[1] * 0.5
        make_face_lettering(
            zone_id + "_No",
            number,
            face_point=(loc[0], front_y, loc[2] + size[2] - 0.10),
            normal=(0.0, -1.0, 0.0),
            size=0.22,
            extrude=0.008,
            mat=mats["sign_zone"],
            collection=props,
            offset=0.018,
            space=0.92,
            bevel_depth=0.0012,
        )
        make_face_lettering(
            zone_id + "_Title",
            title,
            face_point=(loc[0], front_y, loc[2] + 0.10),
            normal=(0.0, -1.0, 0.0),
            size=0.11,
            extrude=0.005,
            mat=mats["sign_zone"],
            collection=props,
            offset=0.018,
            space=0.94,
            bevel_depth=0.0008,
        )


def build_stairs(mats: dict[str, bpy.types.Material]) -> None:
    arch = col("01_ARCHITECTURE")
    lights = col("10_LIGHTS")
    make_box("ENV_Entrance_Platform", (22.4, 11.2, 1.55), (0.0, -0.4, 0.0), mats["stone"], arch, bevel=True, bevel_width=0.06)
    make_box("ENV_Terrace_Front", (18.4, 3.2, 0.18), (0.0, -6.7, 1.55), mats["paving"], arch, bevel=True)
    treads = []
    tread_lights = []
    for i in range(11):
        treads.append(
            make_box(
                f"ENV_Stairs_Tread_{i:02d}",
                (16.6, 0.40, 0.14),
                (0.0, -7.45 - i * 0.40, i * 0.14),
                mats["stone"],
                arch,
                bevel=True,
                bevel_width=0.01,
                exportable=False,
            )
        )
        tread_lights.append(
            make_box(
                f"LIGHT_Stair_{i:02d}",
                (15.2, 0.03, 0.02),
                (0.0, -7.32 - i * 0.40, 0.13 + i * 0.14),
                mats["led_warm"],
                lights,
                exportable=False,
                unwrap=False,
            )
        )
    join_objects("ENV_Entrance_Steps", treads, arch)
    join_objects("LIGHT_Stair_Wash", tread_lights, lights)
    make_box("ENV_Stair_Cheek_L", (0.46, 4.6, 1.7), (-8.45, -9.4, 0.0), mats["bronze"], arch, bevel=True)
    make_box("ENV_Stair_Cheek_R", (0.46, 4.6, 1.7), (8.45, -9.4, 0.0), mats["bronze"], arch, bevel=True)


def build_masses(mats: dict[str, bpy.types.Material]) -> None:
    arch = col("01_ARCHITECTURE")
    facade = col("02_FACADE")
    # Level 1 — double-height lobby bar, set back from the portico.
    make_box("ENV_Residence_Main", (38.4, 13.6, 5.6), (0.5, 9.6, 1.55), mats["concrete"], arch, bevel=True, bevel_width=0.08)
    make_box("ENV_Lobby_Wall_L", (0.48, 8.2, 5.5), (-5.15, 3.4, 1.55), mats["stone"], arch, bevel=True)
    make_box("ENV_Lobby_Wall_R", (0.48, 8.2, 5.5), (5.15, 3.4, 1.55), mats["stone"], arch, bevel=True)
    make_box("ENV_Volume_WestWing", (14.6, 15.6, 8.9), (-18.4, 8.5, 1.55), mats["stone"], arch, bevel=True, bevel_width=0.07)
    make_box("ENV_Volume_WestTower", (5.6, 6.4, 16.6), (-22.4, 11.2, 1.55), mats["stone"], arch, bevel=True, bevel_width=0.06)
    make_box("ENV_Volume_EastGlass", (10.4, 11.6, 16.4), (19.4, 7.9, 1.55), mats["concrete"], arch, bevel=True, bevel_width=0.05)
    make_box("ENV_Volume_Core", (5.8, 6.6, 16.8), (0.2, 11.4, 1.55), mats["stone"], arch, bevel=True)
    # Level 2 — deeper south cantilever over the portico.
    make_box("ENV_Volume_Cantilever", (32.0, 15.2, 3.9), (5.1, 0.2, 7.35), mats["concrete"], arch, bevel=True, bevel_width=0.08)
    make_box("ENV_Balcony_L2", (22.4, 3.4, 0.16), (0.2, -8.15, 7.35), mats["paving"], arch, bevel=True)
    make_box("ENV_Volume_WestUpper", (11.2, 10.8, 3.8), (-17.6, 6.9, 10.45), mats["stone"], arch, bevel=True, bevel_width=0.05)
    # Level 3 — penthouse brought south so the third storey reads in the hero.
    make_box("ENV_Volume_Penthouse", (20.4, 11.2, 3.6), (3.4, 1.8, 11.3), mats["stone"], arch, bevel=True, bevel_width=0.06)
    make_box("ENV_Balcony_L3", (18.4, 2.8, 0.16), (2.6, -4.9, 11.3), mats["paving"], arch, bevel=True)
    make_box("ENV_Volume_WestLantern", (6.6, 6.8, 4.6), (-18.4, 7.0, 14.25), mats["stone"], arch, bevel=True, bevel_width=0.05)
    make_box("ENV_Roof_Terrace", (22.4, 12.2, 0.16), (3.8, 2.2, 14.9), mats["paving"], arch, bevel=True)
    make_box("ENV_Roof_Main", (40.0, 18.4, 0.32), (0.5, 7.4, 7.15), mats["concrete"], arch, bevel=True)
    make_box("ENV_Roof_Cantilever", (33.6, 17.4, 0.28), (5.1, -0.8, 11.25), mats["bronze"], arch, bevel=True)
    make_box("ENV_Roof_East", (13.0, 14.2, 0.28), (19.4, 6.5, 17.95), mats["bronze"], arch, bevel=True)
    make_box("ENV_Roof_Penthouse", (21.2, 11.8, 0.24), (3.4, 1.8, 14.9), mats["bronze"], arch, bevel=True)
    make_box("ENV_Roof_WestLantern", (7.0, 7.2, 0.22), (-18.4, 7.0, 18.85), mats["bronze"], arch, bevel=True)
    make_box("ENV_Canopy_Entrance", (17.2, 8.2, 0.18), (0.0, -6.8, 5.55), mats["bronze"], arch, bevel=True)
    make_box("ENV_Canopy_Soffit", (16.6, 7.8, 0.05), (0.0, -6.8, 5.44), mats["wood"], facade)
    make_box("ENV_Parapet_Cantilever", (33.8, 0.22, 0.55), (5.1, -9.45, 11.52), mats["bronze"], arch)
    make_box("ENV_Parapet_East", (13.2, 0.22, 0.62), (19.4, -0.55, 18.23), mats["bronze"], arch)
    make_box("ENV_Parapet_Penthouse", (21.4, 0.18, 0.42), (3.4, -4.05, 15.14), mats["bronze"], arch)
    make_box("ENV_Roof_Monitor", (7.4, 3.6, 1.55), (3.4, 4.8, 15.14), mats["concrete"], arch, bevel=True)
    make_box("ENV_Reveal_L1L2", (31.4, 14.8, 0.08), (5.1, 0.2, 7.22), mats["bronze"], facade)
    make_box("ENV_Reveal_L2L3", (20.0, 10.8, 0.08), (3.4, 1.8, 11.18), mats["bronze"], facade)


def build_structure(mats: dict[str, bpy.types.Material]) -> None:
    facade = col("02_FACADE")
    lights = col("10_LIGHTS")
    columns = []
    bases = []
    for i, x in enumerate((-8.0, -4.0, 0.0, 4.0, 8.0)):
        bases.append(
            make_box(
                f"ENV_ColumnBase_{i+1:02d}",
                (0.58, 0.58, 0.28),
                (x, -4.15, 1.55),
                mats["bronze"],
                facade,
                bevel=True,
                bevel_width=0.03,
                exportable=False,
            )
        )
        columns.append(
            make_box(
                f"ENV_Column_{i+1:02d}",
                (0.38, 0.38, 5.52),
                (x, -4.15, 1.83),
                mats["metal_dark"],
                facade,
                bevel=True,
                bevel_width=0.02,
                exportable=False,
            )
        )
    join_objects("ENV_Portico_ColumnBases", bases, facade)
    join_objects("ENV_Portico_Columns", columns, facade)
    make_box("ENV_Frame_East_L", (0.22, 13.4, 16.4), (13.2, 6.4, 1.55), mats["bronze"], facade)
    make_box("ENV_Frame_East_R", (0.22, 13.4, 16.4), (25.6, 6.4, 1.55), mats["bronze"], facade)
    make_box("ENV_Frame_Lobby_Head", (10.2, 0.18, 0.22), (0.0, -0.92, 7.05), mats["bronze"], facade)
    make_box("ENV_Frame_Lobby_Sill", (10.2, 0.18, 0.12), (0.0, -0.92, 1.52), mats["bronze"], facade)
    make_box("ENV_Frame_L2_Head", (31.2, 0.16, 0.18), (5.1, -7.35, 11.18), mats["bronze"], facade)
    make_box("ENV_Frame_L3_Head", (19.0, 0.14, 0.16), (2.6, -6.25, 14.85), mats["bronze"], facade)
    fins = []
    for i in range(10):
        fins.append(
            make_box(
                f"ENV_Fin_West_{i+1:02d}",
                (0.12, 3.8, 8.4),
                (-24.8 + i * 1.42, -0.35, 1.9),
                mats["bronze"],
                facade,
                exportable=False,
                unwrap=False,
            )
        )
    join_objects("ENV_West_Fins", fins, facade)
    balcony_fins = []
    for i in range(9):
        balcony_fins.append(
            make_box(
                f"ENV_Fin_Balcony_{i+1:02d}",
                (0.08, 0.08, 1.05),
                (-8.0 + i * 2.0, -9.7, 7.5),
                mats["bronze"],
                facade,
                exportable=False,
                unwrap=False,
            )
        )
    join_objects("ENV_Balcony_Fins", balcony_fins, facade)
    louvers = []
    for i in range(11):
        louvers.append(
            make_box(
                f"ENV_RoofLouver_{i+1:02d}",
                (0.14, 15.6, 0.36),
                (-8.8 + i * 2.4, 0.2, 14.72),
                mats["bronze"],
                facade,
                exportable=False,
                unwrap=False,
            )
        )
    join_objects("ENV_Roof_Louvers", louvers, facade)
    soffits = []
    for i in range(8):
        soffits.append(
            make_box(
                f"ENV_SoffitReveal_{i+1:02d}",
                (0.05, 12.2, 0.03),
                (-8.4 + i * 3.7, 0.2, 7.28),
                mats["bronze"],
                facade,
                exportable=False,
                unwrap=False,
            )
        )
    join_objects("ENV_Cantilever_SoffitReveals", soffits, facade)
    joints = []
    for i in range(10):
        joints.append(
            make_box(
                f"ENV_FacadeJoint_{i+1:02d}",
                (0.045, 0.06, 5.4),
                (-10.2 + i * 2.25, -1.15, 1.55),
                mats["bronze"],
                facade,
                exportable=False,
                unwrap=False,
            )
        )
    join_objects("ENV_Facade_Reveals", joints, facade)
    make_box("LIGHT_FacadeWash_L", (0.06, 0.04, 4.8), (-16.8, 0.55, 2.1), mats["led_warm"], lights, unwrap=False)
    make_box("LIGHT_FacadeWash_R", (0.06, 0.04, 4.8), (12.4, 0.55, 2.1), mats["led_warm"], lights, unwrap=False)


def build_glazing(mats: dict[str, bpy.types.Material]) -> None:
    glass = col("03_GLASS")
    facade = col("02_FACADE")
    make_box("ENV_Glass_Lobby", (9.4, 0.07, 5.35), (0.0, -0.88, 1.58), mats["glass_clear"], glass)
    make_box("ENV_Glass_EastCurtain_S", (11.4, 0.07, 15.6), (19.4, 0.05, 1.7), mats["glass"], glass)
    make_box("ENV_Glass_EastCurtain_E", (0.07, 13.0, 15.6), (25.65, 6.4, 1.7), mats["glass"], glass)
    make_box("ENV_Glass_Cantilever_S", (30.4, 0.07, 3.5), (5.1, -7.35, 7.5), mats["glass"], glass)
    make_box("ENV_Glass_Penthouse_S", (18.8, 0.07, 3.25), (3.4, -3.75, 11.4), mats["glass_clear"], glass)
    make_box("ENV_Glass_Monitor", (7.0, 0.07, 1.28), (3.4, 3.05, 15.3), mats["glass_clear"], glass)
    make_box("ENV_Glass_WestRibbon_01", (11.2, 0.07, 1.25), (-18.4, 0.55, 3.55), mats["glass"], glass)
    make_box("ENV_Glass_WestRibbon_02", (11.2, 0.07, 1.25), (-18.4, 0.55, 6.35), mats["glass"], glass)
    make_box("ENV_Glass_WestRibbon_03", (9.4, 0.07, 1.15), (-17.6, 1.45, 11.4), mats["glass"], glass)
    make_box("ENV_Glass_WestLantern", (5.8, 0.07, 3.4), (-18.4, 3.55, 14.4), mats["glass_clear"], glass)
    punches = []
    for i, z in enumerate((2.9, 5.55, 8.15)):
        for j in range(4):
            punches.append(
                make_box(
                    f"ENV_Glass_WestPunch_{i}{j}",
                    (1.7, 0.07, 1.18),
                    (-22.8 + j * 2.55, 0.52, z),
                    mats["glass"],
                    glass,
                    exportable=False,
                    unwrap=False,
                )
            )
    join_objects("ENV_Glass_WestPunches", punches, glass)
    mullions = []
    for i in range(8):
        mullions.append(
            make_box(
                f"ENV_Mullion_East_{i+1:02d}",
                (0.07, 0.12, 15.6),
                (14.2 + i * 1.48, 0.12, 1.7),
                mats["bronze"],
                facade,
                exportable=False,
                unwrap=False,
            )
        )
    join_objects("ENV_Mullions_East", mullions, facade)
    lobby_mullions = []
    for i in range(5):
        lobby_mullions.append(
            make_box(
                f"ENV_Mullion_Lobby_{i+1:02d}",
                (0.07, 0.12, 5.35),
                (-3.6 + i * 1.8, -0.82, 1.58),
                mats["bronze"],
                facade,
                exportable=False,
                unwrap=False,
            )
        )
    join_objects("ENV_Mullions_Lobby", lobby_mullions, facade)
    make_box("ENV_Transom_Lobby", (9.3, 0.12, 0.08), (0.0, -0.82, 6.85), mats["bronze"], facade, unwrap=False)
    make_box("ENV_Railing_Front", (18.0, 0.05, 0.95), (0.2, -8.1, 1.72), mats["glass_clear"], glass)
    make_box("ENV_Railing_Cap", (18.2, 0.08, 0.04), (0.2, -8.1, 2.67), mats["bronze"], facade)
    make_box("ENV_Railing_L2", (21.8, 0.05, 0.92), (0.2, -9.8, 7.5), mats["glass_clear"], glass)
    make_box("ENV_Railing_L2_Cap", (22.0, 0.08, 0.04), (0.2, -9.8, 8.42), mats["bronze"], facade)
    make_box("ENV_Railing_L3", (18.2, 0.05, 0.88), (2.6, -6.25, 11.45), mats["glass_clear"], glass)
    make_box("ENV_Railing_L3_Cap", (18.4, 0.08, 0.04), (2.6, -6.25, 12.33), mats["bronze"], facade)


def build_interior_depth(mats: dict[str, bpy.types.Material]) -> None:
    props = col("09_PROPS")
    lights = col("10_LIGHTS")
    make_box("ENV_Interior_LobbyCeiling", (9.0, 7.2, 0.06), (0.0, 2.0, 6.95), mats["interior"], lights)
    make_box("LIGHT_Lobby_Fill", (8.2, 5.8, 0.04), (0.0, 1.8, 6.72), mats["interior"], lights, unwrap=False)
    make_box("ENV_Interior_LobbyFloor", (9.0, 7.2, 0.08), (0.0, 2.0, 1.56), mats["wood"], props)
    make_box("ENV_Interior_LobbyBack", (8.8, 0.12, 5.1), (0.0, 5.4, 1.58), mats["interior_wall"], props)
    make_box("ENV_Interior_Lobby_Wall_L", (0.10, 6.4, 5.0), (-4.4, 2.2, 1.58), mats["interior_wall"], props)
    make_box("ENV_Interior_Lobby_Wall_R", (0.10, 6.4, 5.0), (4.4, 2.2, 1.58), mats["interior_wall"], props)
    make_box("PROP_Lobby_Screen", (3.4, 0.08, 1.7), (0.0, 5.28, 3.1), mats["rack"], props)
    make_box("PROP_Lobby_Bench", (2.8, 0.75, 0.45), (-2.2, 2.5, 1.58), mats["wood"], props, bevel=True)
    make_box("PROP_Lobby_Console", (1.9, 0.5, 0.9), (2.5, 4.0, 1.58), mats["bronze"], props, bevel=True)
    make_box("LIGHT_Lobby_Cove", (8.4, 0.04, 0.04), (0.0, 2.0, 6.86), mats["led_warm"], lights)
    make_box("ENV_Interior_L2Ceiling", (28.8, 11.2, 0.06), (5.1, 0.4, 10.95), mats["interior"], lights)
    make_box("LIGHT_L2_Fill", (24.0, 8.0, 0.04), (5.1, 0.2, 10.72), mats["interior"], lights, unwrap=False)
    make_box("ENV_Interior_L2Floor", (28.8, 11.2, 0.08), (5.1, 0.4, 7.4), mats["wood"], props)
    make_box("PROP_L2_Lounge", (3.6, 1.2, 0.7), (6.8, -1.6, 7.48), mats["wood"], props, bevel=True)
    make_box("ENV_Interior_PenthouseCeiling", (19.2, 10.0, 0.05), (3.4, 1.6, 14.75), mats["interior"], lights)
    make_box("LIGHT_Penthouse_Fill", (16.0, 7.2, 0.04), (3.4, 1.4, 14.52), mats["interior"], lights, unwrap=False)
    make_box("ENV_Interior_PenthouseFloor", (19.2, 10.0, 0.06), (3.4, 1.6, 11.35), mats["wood"], props)
    make_box("ENV_Interior_EastCeiling", (10.0, 9.0, 0.06), (19.4, 5.0, 17.6), mats["interior"], lights)
    make_box("LIGHT_East_Fill", (8.6, 7.0, 0.04), (19.4, 4.8, 17.38), mats["interior"], lights, unwrap=False)
    make_box("ENV_Interior_EastFloor", (10.0, 9.0, 0.08), (19.4, 5.0, 1.56), mats["interior_wall"], props)
    make_box("ENV_Interior_EastBack", (9.6, 0.12, 12.8), (19.4, 9.4, 1.7), mats["interior_wall"], props)
    make_box("ENV_Interior_EastSlab_L2", (9.8, 8.6, 0.12), (19.4, 5.2, 7.25), mats["wood"], props)
    make_box("ENV_Interior_EastSlab_L3", (9.8, 8.6, 0.12), (19.4, 5.2, 11.15), mats["wood"], props)
    make_box("PROP_Stair_Hint", (1.5, 3.6, 0.12), (1.9, 5.6, 3.2), mats["bronze"], props, bevel=True)
    racks = []
    edges = []
    for i in range(6):
        racks.append(
            make_box(
                f"PROP_ServerHint_{i+1:02d}",
                (0.52, 0.85, 1.85),
                (17.2 + (i % 3) * 1.4, 3.8 + (i // 3) * 2.3, 1.75),
                mats["rack"],
                props,
                bevel=True,
                exportable=False,
            )
        )
        edges.append(
            make_box(
                f"LIGHT_RackEdge_{i+1:02d}",
                (0.54, 0.03, 1.7),
                (17.2 + (i % 3) * 1.4, 3.35 + (i // 3) * 2.3, 1.8),
                mats["led_cool"],
                lights,
                exportable=False,
                unwrap=False,
            )
        )
    join_objects("PROP_ServerHints", racks, props)
    join_objects("LIGHT_Rack_Accents", edges, lights)


def build_entrance(mats: dict[str, bpy.types.Material]) -> None:
    arch = col("01_ARCHITECTURE")
    props = col("09_PROPS")
    lights = col("10_LIGHTS")
    anim = col("14_ANIMATION")
    make_box("ENV_Portal_Lintel", (10.6, 0.82, 0.38), (0.0, -0.62, 6.95), mats["bronze"], arch, bevel=True)
    make_box("ENV_Portal_Jamb_L", (0.42, 0.82, 5.2), (-5.0, -0.62, 1.58), mats["bronze"], arch)
    make_box("ENV_Portal_Jamb_R", (0.42, 0.82, 5.2), (5.0, -0.62, 1.58), mats["bronze"], arch)
    make_box("LIGHT_Entrance_Warm", (9.8, 0.05, 0.05), (0.0, -1.35, 6.82), mats["led_warm"], lights)
    make_box("LIGHT_Canopy_Cove", (16.4, 0.05, 0.05), (0.0, -6.8, 5.42), mats["led_warm"], lights)
    make_box("LIGHT_Cantilever_Cove", (31.4, 0.06, 0.05), (5.1, -7.2, 7.28), mats["led_warm"], lights)
    make_box("LIGHT_Penthouse_Cove", (19.2, 0.05, 0.04), (3.4, -3.7, 11.22), mats["led_warm"], lights)
    make_box("LIGHT_EastCrown", (11.6, 0.05, 0.05), (19.4, 0.1, 17.85), mats["led_warm"], lights)
    make_box("LIGHT_L3_Cove", (17.8, 0.05, 0.04), (2.6, -6.1, 14.82), mats["led_warm"], lights)
    make_box("LIGHT_WestLantern_Cove", (5.8, 0.04, 0.04), (-18.4, 3.6, 18.7), mats["led_warm"], lights)
    left = make_box("PROP_Door_Main_L", (2.35, 0.14, 4.85), (-2.4, -0.72, 1.58), mats["metal_dark"], anim, bevel=True, bevel_width=0.01)
    right = make_box("PROP_Door_Main_R", (2.35, 0.14, 4.85), (2.4, -0.72, 1.58), mats["metal_dark"], anim, bevel=True, bevel_width=0.01)
    select_only(left)
    bpy.context.scene.cursor.location = (-3.55, -0.72, 1.58)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    select_only(right)
    bpy.context.scene.cursor.location = (3.55, -0.72, 1.58)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    for door, angle in ((left, 82), (right, -82)):
        door.keyframe_insert(data_path="rotation_euler", frame=1)
        door.rotation_euler[2] = math.radians(angle)
        door.keyframe_insert(data_path="rotation_euler", frame=70)
        door.rotation_euler[2] = 0.0
    make_box("PROP_Door_Handle_L", (0.04, 0.09, 0.62), (-0.22, -0.82, 3.7), mats["bronze"], props, unwrap=False)
    make_box("PROP_Door_Handle_R", (0.04, 0.09, 0.62), (0.22, -0.82, 3.7), mats["bronze"], props, unwrap=False)


def build_boundary_and_gate(mats: dict[str, bpy.types.Material]) -> None:
    boundary = col("05_BOUNDARY")
    gate = col("06_GATE")
    lights = col("10_LIGHTS")
    anim = col("14_ANIMATION")
    y = -26.2
    make_box("ENV_Boundary_Front_L", (12.4, 0.62, 2.35), (-20.4, y, 0.08), mats["stone"], boundary, bevel=True, bevel_width=0.04)
    make_box("ENV_Boundary_Front_L2", (7.6, 0.62, 1.25), (-10.2, y, 0.08), mats["stone"], boundary, bevel=True)
    make_box("ENV_Boundary_Front_R", (11.2, 0.62, 2.35), (16.8, y, 0.08), mats["stone"], boundary, bevel=True, bevel_width=0.04)
    make_box("ENV_Boundary_Front_R2", (6.8, 0.62, 1.25), (7.6, y, 0.08), mats["stone"], boundary, bevel=True)
    make_box("ENV_Boundary_Cap_L", (12.6, 0.7, 0.1), (-20.4, y, 2.43), mats["bronze"], boundary)
    make_box("ENV_Boundary_Cap_L2", (7.8, 0.7, 0.1), (-10.2, y, 1.33), mats["bronze"], boundary)
    make_box("ENV_Boundary_Cap_R", (11.4, 0.7, 0.1), (16.8, y, 2.43), mats["bronze"], boundary)
    make_box("ENV_Boundary_Cap_R2", (7.0, 0.7, 0.1), (7.6, y, 1.33), mats["bronze"], boundary)
    screens = []
    for i in range(5):
        screens.append(
            make_box(
                f"ENV_Boundary_Screen_{i+1:02d}",
                (0.06, 0.08, 1.85),
                (-14.2 + i * 0.32, y, 0.18),
                mats["bronze"],
                boundary,
                exportable=False,
                unwrap=False,
            )
        )
    join_objects("ENV_Boundary_Screen", screens, boundary)
    make_box("ENV_Boundary_Return_L", (0.72, 18.4, 2.35), (-27.4, -17.0, 0.08), mats["stone"], boundary, bevel=True)
    make_box("ENV_Boundary_Return_R", (0.72, 14.4, 2.35), (25.6, -19.0, 0.08), mats["stone"], boundary, bevel=True)
    make_box("ENV_Boundary_Planter_L", (21.4, 0.92, 0.55), (-16.2, y + 0.92, 0.08), mats["concrete"], boundary, bevel=True)
    make_box("ENV_Boundary_Planter_R", (16.8, 0.92, 0.55), (14.4, y + 0.92, 0.08), mats["concrete"], boundary, bevel=True)
    make_box("ENV_Boundary_Niche_L", (4.6, 0.22, 1.05), (-16.8, y + 0.22, 0.55), mats["bronze"], boundary)
    make_box("ENV_Boundary_Niche_R", (4.2, 0.22, 1.05), (18.4, y + 0.22, 0.55), mats["bronze"], boundary)
    make_box("LIGHT_Boundary_Wash_L", (8.4, 0.04, 0.04), (-16.2, y - 0.22, 0.22), mats["led_warm"], lights, unwrap=False)
    make_box("LIGHT_Boundary_Wash_R", (8.4, 0.04, 0.04), (16.8, y - 0.22, 0.22), mats["led_warm"], lights, unwrap=False)
    make_box("PROP_Gate_Pillar_L", (1.42, 1.38, 4.15), (-4.25, y, 0.08), mats["stone"], gate, bevel=True, bevel_width=0.07)
    make_box("PROP_Gate_Pillar_R", (1.42, 1.38, 4.15), (4.25, y, 0.08), mats["stone"], gate, bevel=True, bevel_width=0.07)
    make_box("PROP_Gate_PillarCap_L", (1.52, 1.48, 0.12), (-4.25, y, 4.23), mats["bronze"], gate)
    make_box("PROP_Gate_PillarCap_R", (1.52, 1.48, 0.12), (4.25, y, 4.23), mats["bronze"], gate)
    make_box("PROP_Gate_Header", (7.1, 0.24, 0.16), (0.0, y, 3.05), mats["bronze"], gate, bevel=True, bevel_width=0.02)
    make_box("LIGHT_Gate_Pillar_L", (0.2, 0.2, 0.05), (-4.25, y - 0.62, 3.78), mats["led_warm"], lights)
    make_box("LIGHT_Gate_Pillar_R", (0.2, 0.2, 0.05), (4.25, y - 0.62, 3.78), mats["led_warm"], lights)
    make_box("PROP_Residence_Sign", (1.35, 0.10, 0.62), (5.55, y - 0.42, 1.72), mats["metal_dark"], gate, bevel=True)
    make_box("LIGHT_Sign_Reveal", (1.2, 0.02, 0.02), (5.55, y - 0.48, 2.22), mats["led_warm"], lights)
    make_face_lettering(
        "PROP_Gate_Name",
        "DIGITAL RESIDENCE",
        face_point=(0.0, y - 0.12, 3.28),
        normal=(0.0, -1.0, 0.0),
        size=0.26,
        extrude=0.01,
        mat=mats["sign"],
        collection=gate,
        offset=0.018,
        space=0.92,
        bevel_depth=0.0016,
    )
    make_face_lettering(
        "PROP_Gate_Status",
        "INITIALIZING DIGITAL RESIDENCE",
        face_point=(0.0, y - 0.12, 2.92),
        normal=(0.0, -1.0, 0.0),
        size=0.09,
        extrude=0.004,
        mat=mats["sign_zone"],
        collection=gate,
        offset=0.018,
        space=0.92,
        bevel_depth=0.0007,
    )
    left_fins = []
    right_fins = []
    for i in range(13):
        x = -3.42 + i * 0.23
        left_fins.append(
            make_box(
                f"PROP_Gate_Fin_L_{i:02d}",
                (0.05, 0.12, 2.72),
                (x, y, 0.22),
                mats["bronze"],
                anim,
                exportable=False,
                unwrap=False,
            )
        )
        right_fins.append(
            make_box(
                f"PROP_Gate_Fin_R_{i:02d}",
                (0.05, 0.12, 2.72),
                (0.44 + i * 0.23, y, 0.22),
                mats["bronze"],
                anim,
                exportable=False,
                unwrap=False,
            )
        )
    left = join_objects("PROP_Main_Gate_L", left_fins, anim)
    right = join_objects("PROP_Main_Gate_R", right_fins, anim)
    left.keyframe_insert(data_path="location", frame=1)
    right.keyframe_insert(data_path="location", frame=1)
    left.location.x -= 2.5
    right.location.x += 2.5
    left.keyframe_insert(data_path="location", frame=80)
    right.keyframe_insert(data_path="location", frame=80)
    left.location.x += 2.5
    right.location.x -= 2.5
    sconces = []
    for i, x in enumerate((-25.2, -20.6, -16.0, -11.2, 10.4, 15.2, 20.0, 24.6)):
        sconces.append(
            make_box(
                f"LIGHT_Boundary_Sconce_{i+1:02d}",
                (0.08, 0.06, 0.48),
                (x, y - 0.28, 1.35),
                mats["led_warm"],
                lights,
                exportable=False,
                unwrap=False,
            )
        )
    join_objects("LIGHT_Boundary_Sconces", sconces, lights)


def boolean_difference(target: bpy.types.Object, cutter: bpy.types.Object) -> None:
    select_only(target)
    mod = target.modifiers.new(name="BooleanRecess", type="BOOLEAN")
    mod.operation = "DIFFERENCE"
    if hasattr(mod, "solver"):
        try:
            mod.solver = "FAST"
        except TypeError:
            pass
    mod.object = cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    if cutter in EXPORTABLE:
        EXPORTABLE.remove(cutter)
    if cutter in QA_ONLY:
        QA_ONLY.remove(cutter)
    bpy.data.objects.remove(cutter, do_unlink=True)


def make_si_mark(
    name: str,
    location: tuple[float, float, float],
    mat: bpy.types.Material,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.name = name
    obj.scale = (0.26, 0.016, 0.26)
    obj.rotation_euler = (0.0, math.radians(45.0), 0.0)
    select_only(obj)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    mod = obj.modifiers.new(name="Bevel", type="BEVEL")
    mod.width = 0.0035
    mod.segments = 2
    bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.data.materials.append(mat)
    return link(obj, collection)


def build_identity(mats: dict[str, bpy.types.Material]) -> None:
    arch = col("01_ARCHITECTURE")
    lights = col("10_LIGHTS")
    props = col("09_PROPS")
    mx, my, base = -28.4, 1.70, 0.08
    sx, sy, sz = 4.20, 1.18, 17.2
    south = my - sy * 0.5
    monolith = make_box(
        "PROP_Identity_Monolith",
        (sx, sy, sz),
        (mx, my, base),
        mats["stone"],
        arch,
        bevel=False,
        unwrap=True,
    )
    cutter = make_box(
        "TMP_Identity_Recess",
        (3.55, 0.024, 4.85),
        (mx, south + 0.008, 7.40),
        None,
        arch,
        bevel=False,
        unwrap=False,
        exportable=False,
    )
    boolean_difference(monolith, cutter)
    select_only(monolith)
    bevel = monolith.modifiers.new(name="MonolithBevel", type="BEVEL")
    bevel.width = 0.045
    bevel.segments = 2
    bevel.limit_method = "ANGLE"
    bevel.angle_limit = math.radians(40)
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    make_box("ENV_Monolith_Plinth", (sx + 0.55, sy + 0.45, 0.28), (mx, my, base), mats["bronze"], arch, bevel=True)
    make_box("LIGHT_Monolith_Reveal", (3.2, 0.02, 0.03), (mx, south - 0.04, 13.05), mats["led_warm"], lights)
    make_box("LIGHT_Monolith_Slit_L", (0.03, 0.02, 6.2), (mx - 1.72, south - 0.03, 6.7), mats["led_warm"], lights)
    make_box("LIGHT_Monolith_Slit_R", (0.03, 0.02, 6.2), (mx + 1.72, south - 0.03, 6.7), mats["led_warm"], lights)
    make_box("LIGHT_Monolith_Uplight", (1.5, 0.55, 0.05), (mx, south - 0.28, 0.38), mats["led_warm"], lights, unwrap=False)
    make_box("LIGHT_Monolith_Graze", (0.10, 0.62, 5.8), (mx - 1.95, south - 0.22, 7.0), mats["led_warm"], lights, unwrap=False)
    make_box("LIGHT_Monolith_NameWash", (2.6, 0.04, 0.03), (mx, south - 0.08, 10.85), mats["led_warm"], lights, unwrap=False)
    make_si_mark("PROP_Identity_Mark", (mx, south + 0.004, 11.85), mats["sign"], props)
    make_face_lettering(
        "PROP_Identity_Name_01",
        "SADEKUL",
        face_point=(mx, south, 10.55),
        normal=(0.0, -1.0, 0.0),
        size=0.66,
        extrude=0.006,
        mat=mats["sign"],
        collection=props,
        offset=-0.004,
        space=0.88,
        bevel_depth=0.0014,
    )
    make_face_lettering(
        "PROP_Identity_Name_02",
        "ISLAM",
        face_point=(mx, south, 9.72),
        normal=(0.0, -1.0, 0.0),
        size=0.66,
        extrude=0.006,
        mat=mats["sign"],
        collection=props,
        offset=-0.004,
        space=0.88,
        bevel_depth=0.0014,
    )
    make_box(
        "PROP_Identity_Halo_01",
        (2.55, 0.003, 0.08),
        (mx, south + 0.012, 10.55),
        mats["sign_back"],
        props,
        unwrap=False,
    )
    make_box(
        "PROP_Identity_Halo_02",
        (1.95, 0.003, 0.08),
        (mx, south + 0.012, 9.72),
        mats["sign_back"],
        props,
        unwrap=False,
    )
    make_box("PROP_Identity_Rule", (1.72, 0.008, 0.010), (mx, south + 0.006, 9.28), mats["bronze"], props)
    make_face_lettering(
        "PROP_Identity_Title_01",
        "SOFTWARE ENGINEER",
        face_point=(mx, south, 8.92),
        normal=(0.0, -1.0, 0.0),
        size=0.18,
        extrude=0.004,
        mat=mats["sign"],
        collection=props,
        offset=-0.006,
        space=0.96,
        bevel_depth=0.0007,
    )
    make_face_lettering(
        "PROP_Identity_Title_02",
        "AI SYSTEMS BUILDER",
        face_point=(mx, south, 8.52),
        normal=(0.0, -1.0, 0.0),
        size=0.19,
        extrude=0.004,
        mat=mats["sign"],
        collection=props,
        offset=-0.006,
        space=0.96,
        bevel_depth=0.0007,
    )
    make_box("PROP_Identity_Rule_02", (1.85, 0.008, 0.010), (mx, south + 0.006, 8.18), mats["bronze"], props)
    make_face_lettering(
        "PROP_Identity_Title_03",
        "DIGITAL RESIDENCE",
        face_point=(mx, south, 7.82),
        normal=(0.0, -1.0, 0.0),
        size=0.22,
        extrude=0.005,
        mat=mats["sign"],
        collection=props,
        offset=-0.006,
        space=0.94,
        bevel_depth=0.0008,
    )
    make_box(
        "PROP_Identity_Halo_03",
        (2.55, 0.003, 0.08),
        (mx, south + 0.012, 7.82),
        mats["sign_back"],
        props,
        unwrap=False,
    )


def build_water(mats: dict[str, bpy.types.Material]) -> None:
    water = col("08_WATER")
    lights = col("10_LIGHTS")
    make_box("ENV_Waterfall_Wall", (7.4, 0.55, 3.8), (-11.6, -8.35, 0.12), mats["stone"], water, bevel=True, bevel_width=0.04)
    make_box("FX_Waterfall_Sheet", (6.8, 0.04, 3.4), (-11.6, -8.62, 0.28), mats["water"], water)
    make_box("FX_Waterfall_Sheet_B", (6.4, 0.03, 3.15), (-11.6, -8.70, 0.22), mats["water"], water)
    make_box("FX_Waterfall_Sheet_C", (5.8, 0.025, 2.85), (-11.6, -8.78, 0.18), mats["water"], water)
    make_box("ENV_Water_Basin", (8.2, 3.6, 0.45), (-11.6, -10.6, -0.05), mats["stone"], water, bevel=True)
    make_box("FX_Water_ReflectingPool", (18.5, 5.4, 0.05), (-6.2, -12.4, 0.28), mats["water"], water)
    make_box("ENV_Pool_Coping_S", (19.0, 0.28, 0.12), (-6.2, -15.1, 0.28), mats["bronze"], water)
    make_box("ENV_Pool_Coping_N", (19.0, 0.28, 0.12), (-6.2, -9.7, 0.28), mats["bronze"], water)
    make_box("LIGHT_Waterfall_Base", (6.6, 0.08, 0.05), (-11.6, -8.7, 0.32), mats["led_warm"], lights)
    make_box("LIGHT_Waterfall_Mid", (5.8, 0.04, 0.03), (-11.6, -8.66, 1.85), mats["led_warm"], lights)
    make_box("LIGHT_Pool_Edge", (17.8, 0.05, 0.03), (-6.2, -15.05, 0.34), mats["led_warm"], lights)
    foam_cards = [
        make_alpha_card("FX_Waterfall_Foam_A", (-11.6, -9.15, 0.55), (3.4, 1.15), 0.0, mats["foam"], water, pitch=12.0),
        make_alpha_card("FX_Waterfall_Foam_B", (-11.4, -10.4, 0.42), (2.8, 0.85), 0.35, mats["foam"], water, pitch=8.0),
        make_alpha_card("FX_Shore_Foam_S", (0.0, -29.6, -0.85), (18.0, 3.2), 0.0, mats["foam"], water, pitch=6.0),
    ]
    join_objects("FX_Water_FoamCards", foam_cards, water)


def duplicate_at(src: bpy.types.Object, name: str, location: tuple[float, float, float], collection: bpy.types.Collection) -> bpy.types.Object:
    obj = src.copy()
    obj.data = src.data
    obj.name = name
    obj.location = location
    collection.objects.link(obj)
    EXPORTABLE.append(obj)
    return obj


def duplicate_unique(src: bpy.types.Object, name: str, location: tuple[float, float, float], collection: bpy.types.Collection) -> bpy.types.Object:
    obj = src.copy()
    obj.data = src.data.copy()
    obj.name = name
    obj.data.name = name
    obj.location = location
    collection.objects.link(obj)
    EXPORTABLE.append(obj)
    return obj


def make_alpha_card(
    name: str,
    location: tuple[float, float, float],
    size: tuple[float, float],
    yaw: float,
    mat: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    pitch: float = 90.0,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=location)
    card = bpy.context.active_object
    card.name = name
    card.data.name = name
    card.rotation_euler = (math.radians(pitch), 0.0, yaw)
    card.scale = (size[0], 1.0, size[1])
    select_only(card)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    card.data.materials.append(mat)
    return link(card, collection)


def add_leaf_cluster(
    prefix: str,
    location: tuple[float, float, float],
    mats: dict[str, bpy.types.Material],
    collection: bpy.types.Collection,
    rng: random.Random,
    *,
    scale: float,
    lod: int,
) -> list[bpy.types.Object]:
    cards: list[bpy.types.Object] = []
    cs = rng.uniform(0.85, 1.25) * scale
    yaw0 = rng.uniform(0.0, math.tau)
    planes = ((82.0, 0.0), (88.0, 58.0), (74.0, 118.0))
    if lod >= 2:
        planes = planes[:2]
    elif lod == 1:
        planes = planes[:2]
    leaf_mat = mats["canopy"] if rng.random() < 0.55 else mats["canopy_b"]
    for i, (pitch, yaw_off) in enumerate(planes):
        jitter = (
            location[0] + rng.uniform(-0.08, 0.08),
            location[1] + rng.uniform(-0.08, 0.08),
            location[2] + rng.uniform(-0.10, 0.12),
        )
        cards.append(
            make_alpha_card(
                f"{prefix}_{i}",
                jitter,
                (cs * rng.uniform(0.85, 1.12), cs * rng.uniform(1.05, 1.32)),
                yaw0 + math.radians(yaw_off) + rng.uniform(-0.2, 0.2),
                leaf_mat,
                collection,
                pitch=pitch + rng.uniform(-8.0, 8.0),
            )
        )
    return cards


def instance_at(
    src: bpy.types.Object,
    name: str,
    location: tuple[float, float, float],
    collection: bpy.types.Collection,
    *,
    yaw: float = 0.0,
    scale: float = 1.0,
) -> bpy.types.Object:
    obj = duplicate_at(src, name, location, collection)
    obj.rotation_euler = (0.0, 0.0, yaw)
    obj.scale = (scale, scale, scale)
    return obj


def make_tapered_limb(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    r1: float,
    r2: float,
    mat: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    verts: int = 8,
) -> bpy.types.Object:
    start_v = Vector(start)
    end_v = Vector(end)
    direction = end_v - start_v
    length = max(float(direction.length), 0.08)
    mid = (start_v + end_v) * 0.5
    bpy.ops.mesh.primitive_cone_add(
        vertices=verts,
        radius1=r1,
        radius2=r2,
        depth=length,
        location=mid,
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.data.name = name
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    select_only(obj)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if mat is not None:
        obj.data.materials.append(mat)
    return link(obj, collection)


def set_origin_world(obj: bpy.types.Object, location: tuple[float, float, float]) -> None:
    select_only(obj)
    bpy.context.scene.cursor.location = location
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    obj.location = location


def build_tree_prototype(
    prefix: str,
    mats: dict[str, bpy.types.Material],
    collection: bpy.types.Collection,
    *,
    lod: int,
    seed: int,
    height: float,
) -> tuple[bpy.types.Object, bpy.types.Object]:
    rng = random.Random(seed)
    ox, oy = 0.0, 0.0
    trunk_h = height * 0.62
    base_r = 0.30 * (height / 6.0)
    lean = (rng.uniform(-0.12, 0.12), rng.uniform(-0.12, 0.12))
    trunk = make_tapered_limb(
        f"{prefix}_Trunk",
        (ox, oy, 0.08),
        (ox + lean[0], oy + lean[1], trunk_h),
        base_r,
        base_r * 0.42,
        mats["trunk"],
        collection,
        verts=12 if lod == 0 else 8,
    )
    unwrap_cube(trunk, cube_size=1.5)
    wood = [trunk]
    foliage: list[bpy.types.Object] = []
    n_primary = 7 if lod == 0 else 5 if lod == 1 else 3
    n_mid = 1 if lod == 0 else 0
    for i in range(n_primary):
        az = (i / n_primary) * math.tau + rng.uniform(-0.28, 0.28)
        el = rng.uniform(0.22, 0.98)
        length = rng.uniform(1.15, 2.25) * (height / 6.2)
        attach_z = trunk_h * rng.uniform(0.28, 0.94)
        sx = ox + lean[0] * (attach_z / trunk_h) + math.cos(az) * 0.05
        sy = oy + lean[1] * (attach_z / trunk_h) + math.sin(az) * 0.05
        ex = ox + math.cos(az) * length * math.cos(el)
        ey = oy + math.sin(az) * length * math.cos(el)
        ez = attach_z + math.sin(el) * length
        r1 = base_r * rng.uniform(0.18, 0.30)
        wood.append(
            make_tapered_limb(
                f"{prefix}_Limb_{i:02d}",
                (sx, sy, attach_z),
                (ex, ey, ez),
                r1,
                r1 * 0.28,
                mats["trunk"],
                collection,
                verts=8 if lod == 0 else 6,
            )
        )
        for m in range(n_mid + 1):
            t = 0.45 + m * 0.28
            foliage.extend(
                add_leaf_cluster(
                    f"{prefix}_Cl_{i:02d}_{m}",
                    (sx + (ex - sx) * t, sy + (ey - sy) * t, attach_z + (ez - attach_z) * t),
                    mats,
                    collection,
                    rng,
                    scale=(height / 6.2) * (1.05 if lod == 0 else 1.2),
                    lod=lod,
                )
            )
    n_crown = 8 if lod == 0 else 5 if lod == 1 else 2
    for i in range(n_crown):
        az = rng.uniform(0.0, math.tau)
        r = rng.uniform(0.35, 1.55) * (height / 6.2)
        z = trunk_h + rng.uniform(-0.15, 1.35) * (height / 6.2)
        foliage.extend(
            add_leaf_cluster(
                f"{prefix}_Crown_{i:02d}",
                (ox + math.cos(az) * r, oy + math.sin(az) * r, z),
                mats,
                collection,
                rng,
                scale=(height / 6.2) * 1.12,
                lod=lod,
            )
        )
    if lod == 0:
        for i in range(5):
            az = rng.uniform(0.0, math.tau)
            r = rng.uniform(0.45, 1.15)
            z = trunk_h * rng.uniform(0.42, 0.88)
            wood.append(
                make_tapered_limb(
                    f"{prefix}_Twig_{i:02d}",
                    (ox, oy, z),
                    (ox + math.cos(az) * r, oy + math.sin(az) * r, z + rng.uniform(0.25, 0.85)),
                    base_r * 0.12,
                    0.012,
                    mats["trunk"],
                    collection,
                    verts=6,
                )
            )
    wood_obj = join_objects(f"{prefix}_Wood", wood, collection)
    leaf_obj = join_objects(f"{prefix}_Foliage", foliage, collection)
    set_origin_world(wood_obj, (0.0, 0.0, 0.0))
    set_origin_world(leaf_obj, (0.0, 0.0, 0.0))
    return wood_obj, leaf_obj


def place_tree(
    wood: bpy.types.Object,
    foliage: bpy.types.Object,
    name: str,
    location: tuple[float, float, float],
    collection: bpy.types.Collection,
    *,
    yaw: float,
    scale: float,
    linked: bool,
) -> None:
    if linked:
        instance_at(wood, f"{name}_Wood", location, collection, yaw=yaw, scale=scale)
        instance_at(foliage, f"{name}_Foliage", location, collection, yaw=yaw, scale=scale)
        return
    w = duplicate_unique(wood, f"{name}_Wood", location, collection)
    f = duplicate_unique(foliage, f"{name}_Foliage", location, collection)
    for obj in (w, f):
        obj.rotation_euler = (0.0, 0.0, yaw)
        obj.scale = (scale, scale, scale)


def add_tree_base(
    name: str,
    location: tuple[float, float, float],
    mats: dict[str, bpy.types.Material],
    collection: bpy.types.Collection,
    rng: random.Random,
) -> None:
    make_box(
        f"{name}_Soil",
        (1.55, 1.55, 0.16),
        (location[0] - 0.78, location[1] - 0.78, 0.0),
        mats["trunk"],
        collection,
        bevel=True,
        bevel_width=0.04,
    )
    pebble = make_rock(
        f"{name}_RootRock",
        (location[0] + rng.uniform(-0.45, 0.45), location[1] + rng.uniform(-0.4, 0.4), 0.08),
        (0.38, 0.28, 0.22),
        mats["rock"],
        collection,
        rng,
    )
    pebble.scale = (1.0, 1.0, 1.0)


def build_palm_prototype(
    prefix: str,
    mats: dict[str, bpy.types.Material],
    collection: bpy.types.Collection,
    *,
    seed: int,
    height: float,
) -> tuple[bpy.types.Object, bpy.types.Object]:
    rng = random.Random(seed)
    trunk = make_tapered_limb(
        f"{prefix}_Trunk",
        (0.0, 0.0, 0.06),
        (rng.uniform(-0.18, 0.18), rng.uniform(-0.18, 0.18), height * 0.78),
        0.22 * (height / 7.0),
        0.08,
        mats["trunk"],
        collection,
        verts=10,
    )
    unwrap_cube(trunk, cube_size=1.4)
    cards: list[bpy.types.Object] = []
    crown_z = height * 0.78
    for i in range(6):
        yaw = (i / 6.0) * math.tau + rng.uniform(-0.2, 0.2)
        cards.append(
            make_alpha_card(
                f"{prefix}_Frond_{i}",
                (math.cos(yaw) * 0.22, math.sin(yaw) * 0.22, crown_z + rng.uniform(-0.1, 0.2)),
                (2.35 * rng.uniform(0.9, 1.15), 2.7 * rng.uniform(0.9, 1.12)),
                yaw,
                mats["palm"],
                collection,
                pitch=58.0 + rng.uniform(-10.0, 12.0),
            )
        )
    wood = join_objects(f"{prefix}_Wood", [trunk], collection)
    foliage = join_objects(f"{prefix}_Foliage", cards, collection)
    set_origin_world(wood, (0.0, 0.0, 0.0))
    set_origin_world(foliage, (0.0, 0.0, 0.0))
    return wood, foliage


def build_distant_billboard(
    prefix: str,
    mats: dict[str, bpy.types.Material],
    collection: bpy.types.Collection,
) -> tuple[bpy.types.Object, bpy.types.Object]:
    trunk = make_tapered_limb(
        f"{prefix}_Trunk",
        (0.0, 0.0, 0.05),
        (0.0, 0.0, 2.4),
        0.16,
        0.06,
        mats["trunk"],
        collection,
        verts=6,
    )
    cards = [
        make_alpha_card(f"{prefix}_Card_A", (0.0, 0.0, 3.15), (3.4, 5.6), 0.12, mats["palm_far"], collection, pitch=90.0),
        make_alpha_card(
            f"{prefix}_Card_B",
            (0.0, 0.0, 3.2),
            (3.2, 5.4),
            math.radians(72.0),
            mats["palm_far"],
            collection,
            pitch=90.0,
        ),
    ]
    wood = join_objects(f"{prefix}_Wood", [trunk], collection)
    foliage = join_objects(f"{prefix}_Foliage", cards, collection)
    set_origin_world(wood, (0.0, 0.0, 0.0))
    set_origin_world(foliage, (0.0, 0.0, 0.0))
    return wood, foliage


def build_landscape(mats: dict[str, bpy.types.Material]) -> None:
    landscape = col("07_LANDSCAPE")
    lights = col("10_LIGHTS")
    make_box("PROP_Planter_Approach_L", (3.4, 6.8, 0.62), (-12.2, -17.6, 0.1), mats["concrete"], landscape, bevel=True)
    make_box("PROP_Planter_Approach_R", (3.2, 5.4, 0.62), (11.8, -16.8, 0.1), mats["concrete"], landscape, bevel=True)
    make_box("PROP_Planter_East", (7.6, 2.0, 0.5), (18.6, -8.2, 0.1), mats["concrete"], landscape, bevel=True)

    hedge_cards = []
    for i, x in enumerate((-24.8, -21.8, -18.6, -15.4, -12.2, 12.4, 15.6, 18.8, 21.8, 24.6)):
        hedge_cards.append(
            make_alpha_card(
                f"PROP_Hedge_Boundary_{i+1:02d}",
                (x, -24.85, 1.05),
                (1.85, 1.55),
                math.radians(8.0 + i * 7.0),
                mats["hedge"],
                landscape,
            )
        )
    for i, (x, y, yaw) in enumerate(
        (
            (-12.2, -15.4, 12.0),
            (-12.2, -17.8, 38.0),
            (-12.2, -19.8, 64.0),
            (11.8, -15.2, 18.0),
            (11.8, -17.4, 52.0),
            (18.6, -8.2, 6.0),
            (16.4, -8.15, 28.0),
            (20.6, -8.25, 44.0),
        )
    ):
        hedge_cards.append(
            make_alpha_card(
                f"PROP_Hedge_Planter_{i+1:02d}",
                (x, y, 1.22),
                (1.55, 1.25),
                math.radians(yaw),
                mats["hedge"],
                landscape,
            )
        )
    join_objects("PROP_Hedge_Masses", hedge_cards, landscape)

    lod0_a = build_tree_prototype("PROP_Tree_LOD0_A", mats, landscape, lod=0, seed=11, height=6.6)
    lod0_b = build_tree_prototype("PROP_Tree_LOD0_B", mats, landscape, lod=0, seed=27, height=7.1)
    lod0_c = build_tree_prototype("PROP_Tree_LOD0_C", mats, landscape, lod=0, seed=43, height=6.2)
    lod0_d = build_tree_prototype("PROP_Tree_LOD0_D", mats, landscape, lod=0, seed=59, height=6.8)
    hero_trees = [
        (lod0_a, (-12.2, -19.8, 0.0), 0.18, 1.00, False),
        (lod0_b, (11.8, -16.8, 0.0), 1.05, 1.04, False),
        (lod0_c, (-14.8, -11.2, 0.0), 2.40, 0.94, False),
        (lod0_d, (8.6, -21.8, 0.0), 0.62, 0.96, False),
        (lod0_a, (10.6, -14.4, 0.0), 2.85, 0.88, True),
        (lod0_b, (-8.4, -21.5, 0.0), 4.10, 0.90, True),
    ]
    for proto, loc, yaw, scale, linked in hero_trees:
        wood, foliage = proto
        suffix = f"{int(abs(loc[0]*10)):03d}_{int(abs(loc[1]*10)):03d}"
        place_tree(wood, foliage, f"PROP_Tree_Hero_{suffix}", loc, landscape, yaw=yaw, scale=scale, linked=linked)
        add_tree_base(f"PROP_Tree_Hero_{suffix}", loc, mats, landscape, random.Random(int(abs(loc[0] * 13))))
    for proto in (lod0_a, lod0_b, lod0_c, lod0_d):
        for obj in proto:
            obj.location = (80.0, 80.0, -20.0)
            obj.hide_render = True
            obj.hide_viewport = True
            if obj in EXPORTABLE:
                EXPORTABLE.remove(obj)

    lod1_a = build_tree_prototype("PROP_Tree_LOD1_A", mats, landscape, lod=1, seed=71, height=5.4)
    lod1_b = build_tree_prototype("PROP_Tree_LOD1_B", mats, landscape, lod=1, seed=88, height=5.8)
    secondary_sites = [
        ((21.6, -12.4, 0.0), lod1_a, 0.4, 1.08),
        ((-21.8, -12.8, 0.0), lod1_b, 1.7, 1.02),
        ((16.8, -22.6, 0.0), lod1_a, 2.9, 0.94),
        ((-17.4, -21.2, 0.0), lod1_b, 0.2, 0.98),
        ((22.8, -20.2, 0.0), lod1_a, 4.4, 1.12),
        ((-24.6, -6.4, 0.0), lod1_b, 3.3, 1.06),
        ((18.6, -8.2, 0.0), lod1_a, 1.1, 0.86),
        ((12.4, -18.6, 0.0), lod1_b, 5.2, 0.92),
    ]
    for loc, proto, yaw, scale in secondary_sites:
        suffix = f"{int(abs(loc[0]*10)):03d}_{int(abs(loc[1]*10)):03d}"
        place_tree(proto[0], proto[1], f"PROP_Tree_Sec_{suffix}", loc, landscape, yaw=yaw, scale=scale, linked=True)
    for proto in (lod1_a, lod1_b):
        for obj in proto:
            obj.location = (82.0, 80.0, -20.0)
            obj.hide_render = True
            obj.hide_viewport = True
            if obj in EXPORTABLE:
                EXPORTABLE.remove(obj)

    lod2 = build_distant_billboard("PROP_Tree_LOD2_A", mats, landscape)
    far_sites = [
        ((18.8, -32.4, 0.0), 0.5, 1.18),
        ((-15.6, -31.6, 0.0), 1.9, 1.05),
        ((24.2, -28.8, 0.0), 3.4, 1.22),
        ((-22.8, -28.4, 0.0), 4.8, 1.10),
        ((14.2, -34.6, 0.0), 2.2, 1.28),
        ((-10.2, -33.5, 0.0), 5.5, 1.00),
    ]
    for loc, yaw, scale in far_sites:
        suffix = f"{int(abs(loc[0]*10)):03d}_{int(abs(loc[1]*10)):03d}"
        place_tree(lod2[0], lod2[1], f"PROP_Tree_Far_{suffix}", loc, landscape, yaw=yaw, scale=scale, linked=True)
    lod2[0].location = (84.0, 80.0, -20.0)
    lod2[1].location = (84.0, 80.0, -20.0)
    lod2[0].hide_render = True
    lod2[1].hide_render = True
    lod2[0].hide_viewport = True
    lod2[1].hide_viewport = True
    for obj in lod2:
        if obj in EXPORTABLE:
            EXPORTABLE.remove(obj)

    palm_a = build_palm_prototype("PROP_Palm_A", mats, landscape, seed=201, height=7.6)
    palm_b = build_palm_prototype("PROP_Palm_B", mats, landscape, seed=223, height=6.9)
    palm_sites = [
        ((-26.4, -18.6, 0.0), palm_a, 0.4, 1.05),
        ((25.8, -17.4, 0.0), palm_b, 1.6, 0.96),
        ((-20.2, -26.8, 0.0), palm_a, 2.3, 1.12),
        ((19.4, -27.2, 0.0), palm_b, 4.1, 1.08),
        ((-8.8, -29.6, 0.0), palm_a, 5.2, 0.92),
        ((8.4, -30.1, 0.0), palm_b, 0.8, 1.00),
    ]
    for loc, proto, yaw, scale in palm_sites:
        suffix = f"{int(abs(loc[0]*10)):03d}_{int(abs(loc[1]*10)):03d}"
        place_tree(proto[0], proto[1], f"PROP_Palm_{suffix}", loc, landscape, yaw=yaw, scale=scale, linked=True)
        add_tree_base(f"PROP_Palm_{suffix}", loc, mats, landscape, random.Random(int(abs(loc[1] * 9))))
    for proto in (palm_a, palm_b):
        for obj in proto:
            obj.location = (86.0, 80.0, -20.0)
            obj.hide_render = True
            obj.hide_viewport = True
            if obj in EXPORTABLE:
                EXPORTABLE.remove(obj)

    uplights = []
    for i, (x, y) in enumerate(
        ((-12.2, -19.8), (11.8, -16.8), (-14.8, -11.2), (8.6, -21.8), (21.6, -12.4), (-21.8, -12.8))
    ):
        uplights.append(
            make_box(
                f"LIGHT_Tree_Uplight_{i+1:02d}",
                (0.16, 0.16, 0.04),
                (x, y + 0.42, 0.16),
                mats["led_warm"],
                lights,
                unwrap=False,
            )
        )
    join_objects("LIGHT_Tree_Uplights", uplights, lights)

    shrub_sites = [
        (-20.4, -24.4, 18.0),
        (-16.8, -24.35, 34.0),
        (-13.2, -24.45, 52.0),
        (13.6, -24.4, 12.0),
        (17.2, -24.5, 41.0),
        (20.8, -24.35, 63.0),
        (-14.2, -10.8, 22.0),
        (-9.2, -11.4, 48.0),
        (-12.8, -14.6, 8.0),
        (9.4, -13.8, 31.0),
        (-4.6, -14.8, 16.0),
        (4.2, -15.2, 44.0),
    ]
    shrubs = []
    for i, (x, y, yaw) in enumerate(shrub_sites, start=1):
        shrubs.append(
            make_alpha_card(
                f"PROP_Shrub_{i:02d}",
                (x, y, 0.95),
                (1.25, 1.45),
                math.radians(yaw),
                mats["canopy"],
                landscape,
            )
        )
    join_objects("PROP_Shrubs", shrubs, landscape)

    grasses = []
    for i, (x, y, yaw) in enumerate(
        (
            (-5.4, -18.6, 12.0),
            (-5.2, -20.8, 38.0),
            (5.4, -18.4, 22.0),
            (5.5, -21.0, 48.0),
            (-14.6, -23.6, 8.0),
            (14.8, -23.4, 28.0),
            (-22.4, -23.8, 16.0),
            (22.2, -23.6, 40.0),
            (-8.6, -28.4, 18.0),
            (8.8, -28.2, 42.0),
            (-12.4, -30.6, 6.0),
            (12.6, -30.4, 33.0),
            (-3.8, -16.8, 24.0),
            (3.8, -16.6, 51.0),
            (-18.2, -27.8, 14.0),
            (19.4, -27.4, 37.0),
            (-13.4, -12.6, 20.0),
            (-10.2, -12.8, 46.0),
            (-11.8, -15.6, 12.0),
            (-6.8, -13.4, 34.0),
        )
    ):
        grasses.append(
            make_alpha_card(
                f"PROP_Grass_{i+1:02d}",
                (x, y, 0.55),
                (1.05, 0.85),
                math.radians(yaw),
                mats["grass"],
                landscape,
            )
        )
    join_objects("PROP_Ornamental_Grass", grasses, landscape)

    path_lights = []
    for i, x in enumerate((-3.2, -1.05, 1.05, 3.2)):
        path_lights.append(
            make_box(
                f"PROP_PathLight_{i+1:02d}",
                (0.14, 0.14, 0.55),
                (x, -22.4, 0.1),
                mats["bronze"],
                landscape,
                bevel=True,
                exportable=False,
            )
        )
        path_lights.append(
            make_box(
                f"LIGHT_Path_{i+1:02d}",
                (0.1, 0.1, 0.04),
                (x, -22.4, 0.62),
                mats["led_warm"],
                lights,
                exportable=False,
                unwrap=False,
            )
        )
    join_objects("PROP_PathLights", path_lights, landscape)


def build_collision() -> None:
    collision = col("11_COLLISION")
    mat = bpy.data.materials["MAT_CollisionProxy"]
    proxies = [
        ("COL_Ground", (54.0, 46.0, 1.2), (0.0, -4.0, -1.2)),
        ("COL_Entrance_Steps", (17.0, 5.0, 1.7), (0.0, -9.6, 0.0)),
        ("COL_Entrance_Platform", (22.4, 11.2, 1.55), (0.0, -0.4, 0.0)),
        ("COL_Door", (10.2, 0.5, 5.0), (0.0, -0.72, 1.58)),
        ("COL_Boundary", (54.0, 0.9, 2.5), (0.0, -26.2, 0.08)),
        ("COL_Gate", (9.0, 1.5, 4.2), (0.0, -26.2, 0.08)),
        ("COL_Building_Base", (38.4, 13.6, 5.6), (0.5, 9.6, 1.55)),
        ("COL_Building_West", (14.6, 15.6, 8.9), (-18.4, 8.5, 1.55)),
        ("COL_Building_East", (10.4, 11.6, 16.4), (19.4, 7.9, 1.55)),
        ("COL_Water_Edge", (19.0, 6.0, 0.7), (-6.2, -12.4, -0.05)),
        ("COL_Identity_Monolith", (4.4, 1.4, 17.4), (-28.4, 1.70, 0.08)),
    ]
    for name, size, origin in proxies:
        obj = make_box(name, size, origin, mat, collision, bevel=False, unwrap=False)
        obj.hide_render = True
        obj.display_type = "WIRE"


def build_anchors() -> None:
    ui = col("12_UI_ANCHORS")
    make_empty("UI_Entrance_Trigger", (0.0, -8.4, 1.8), ui)
    make_empty("UI_Identity", (-28.4, 1.11, 9.8), ui)
    make_empty("UI_Identity_Monolith", (-28.4, 1.11, 9.8), ui)
    make_empty("UI_Owner_Name", (-28.4, 1.11, 9.9), ui)
    make_empty("UI_Residence_Sign", (0.0, -26.34, 3.22), ui)
    make_empty("UI_Engineering_Direction", (-17.0, -1.8, 2.2), ui)
    make_empty("UI_AI_Lab_Direction", (18.4, -3.6, 2.2), ui)
    make_empty("UI_Project_Direction", (10.5, -6.5, 2.0), ui)
    make_empty("UI_Command_Center_Direction", (0.2, 12.6, 2.4), ui)
    make_empty("UI_Building_Entry", (0.0, -2.2, 2.4), ui)
    make_empty("ENV_Exterior_Root", (0.0, 0.0, 0.0), col("90_EXPORT"))


def parent_to_root() -> None:
    root = bpy.data.objects.get("ENV_Exterior_Root")
    if root is None:
        return
    for obj in list(EXPORTABLE):
        if obj != root and obj.parent is None:
            obj.parent = root
            obj.matrix_parent_inverse = root.matrix_world.inverted()


def build_qa_cameras_and_lights() -> None:
    cameras = col("13_CAMERAS")
    debug = col("99_DEBUG")
    specs = [
        ("CAM_Hero_ThreeQuarter", (22.4, -24.8, 7.5), (-7.8, -2.2, 5.0), 32),
        ("CAM_SYSTEM_HERO", (22.4, -24.8, 7.5), (-7.8, -2.2, 5.0), 32),
        ("CAM_ISLAND_FRONT", (0.4, -36.0, 6.2), (0.0, -4.0, 4.4), 30),
        ("CAM_ISLAND_3Q", (22.4, -24.8, 7.5), (-7.8, -2.2, 5.0), 32),
        ("CAM_SHORELINE_CLOSEUP", (8.4, -20.6, 0.35), (4.0, -16.2, -1.1), 40),
        ("CAM_WATER_SYSTEM", (10.0, -28.0, 3.2), (0.0, -8.0, -0.4), 34),
        ("CAM_WATER_CINEMATIC", (10.0, -28.0, 3.2), (0.0, -8.0, -0.4), 34),
        ("CAM_WATERFALL_CLOSEUP", (-11.6, -13.2, 2.1), (-11.6, -9.2, 0.8), 38),
        ("CAM_PORTFOLIO_FACADE_SYSTEM", (0.0, -22.4, 7.8), (0.0, -7.2, 6.4), 32),
        ("CAM_SYSTEM_FRONT", (-8.0, -48.0, 4.4), (-6.0, -6.0, 6.8), 32),
        ("CAM_SYSTEM_ISLAND", (6.0, -62.0, 10.5), (0.0, -4.0, 4.0), 26),
        ("CAM_SYSTEM_MONOLITH", (-28.4, -6.6, 9.55), (-28.4, 1.11, 9.55), 38),
        ("CAM_CINEMATIC_HERO", (22.4, -24.8, 7.5), (-7.8, -2.2, 5.0), 32),
        ("CAM_CINEMATIC_SUNSET", (-34.0, -18.0, 5.2), (-6.0, -4.0, 6.5), 30),
        ("CAM_CINEMATIC_ISLAND", (14.0, -58.0, 9.4), (0.5, -8.0, 6.5), 28),
        ("CAM_TREE_HERO_CLOSEUP", (-12.05, -21.35, 1.72), (-12.2, -19.8, 2.55), 35),
        ("CAM_LANDSCAPE_CLOSEUP", (10.6, -18.4, 1.6), (11.8, -16.8, 2.4), 38),
        ("CAM_WATER_CLOSEUP", (-11.6, -13.4, 2.35), (-11.6, -8.55, 1.9), 38),
        ("CAM_SIGNAGE_CLOSEUP", (-28.4, -6.6, 9.55), (-28.4, 1.11, 9.55), 38),
        ("CAM_MATERIAL_CLOSEUP", (5.2, -9.4, 2.4), (0.6, -3.2, 4.2), 50),
        ("CAM_Front_Architectural", (-8.0, -48.0, 4.4), (-6.0, -6.0, 6.8), 32),
        ("CAM_Entrance", (0.25, -14.5, 2.05), (0.0, -3.2, 4.6), 40),
        ("CAM_Identity_Monolith_Closeup", (-28.4, -6.6, 9.55), (-28.4, 1.11, 9.55), 38),
        ("CAM_Vegetation_Closeup", (-12.05, -21.35, 1.72), (-12.2, -19.8, 2.55), 35),
        ("CAM_Gate", (0.2, -36.5, 1.85), (0.0, -26.0, 2.85), 36),
        ("CAM_Water_Feature", (-11.6, -13.4, 2.35), (-11.6, -8.55, 1.9), 38),
        ("CAM_Material_Detail", (5.2, -9.4, 2.4), (0.6, -3.2, 4.2), 50),
        ("CAM_Night_Wide", (8.0, -58.0, 8.4), (0.5, -8.0, 7.2), 28),
        ("CAM_Elevated", (18.0, -28.0, 22.0), (1.2, 0.0, 6.5), 30),
    ]
    for name, loc, target, lens in specs:
        cam_data = bpy.data.cameras.new(name)
        cam_data.lens = lens
        cam = bpy.data.objects.new(name, cam_data)
        cam.location = loc
        look_at(cam, target)
        cameras.objects.link(cam)
        QA_ONLY.append(cam)

    def add_light(name: str, type_: str, loc: tuple[float, float, float], energy: float, color, size: float = 6.0):
        data = bpy.data.lights.new(name, type_)
        data.energy = energy
        data.color = color
        if type_ == "AREA":
            data.size = size
        light = bpy.data.objects.new(name, data)
        light.location = loc
        debug.objects.link(light)
        QA_ONLY.append(light)
        return light

    moon = add_light("LIGHT_QA_Moon", "SUN", (-16.0, -14.0, 30.0), 2.35, (0.62, 0.74, 0.95))
    moon.rotation_euler = (math.radians(48), math.radians(-12), math.radians(18))
    add_light("LIGHT_QA_Fill", "AREA", (2.0, -32.0, 10.0), 4200.0, (0.68, 0.76, 0.94), 28.0)
    add_light("LIGHT_QA_Entrance", "AREA", (0.0, -7.4, 5.4), 3600.0, (1.0, 0.74, 0.42), 10.0)
    add_light("LIGHT_QA_Interior", "AREA", (0.0, 1.8, 4.2), 2400.0, (1.0, 0.72, 0.40), 8.0)
    add_light("LIGHT_QA_East", "AREA", (22.0, -5.0, 8.5), 1400.0, (1.0, 0.76, 0.48), 9.0)
    add_light("LIGHT_QA_L2", "AREA", (5.0, -4.0, 9.2), 1500.0, (1.0, 0.70, 0.38), 10.0)
    add_light("LIGHT_QA_Rim", "AREA", (-20.0, 12.0, 14.0), 900.0, (0.58, 0.66, 0.84), 12.0)
    add_light("LIGHT_QA_Monolith", "AREA", (-28.4, -4.6, 9.6), 1600.0, (1.0, 0.80, 0.50), 6.0)
    add_light("LIGHT_QA_Tree", "AREA", (-12.2, -18.6, 1.4), 900.0, (1.0, 0.82, 0.54), 4.0)
    add_light("LIGHT_QA_Water", "AREA", (-11.6, -12.4, 1.1), 720.0, (1.0, 0.78, 0.48), 5.0)
    add_light("LIGHT_QA_Facade", "AREA", (0.0, -22.0, 8.0), 1800.0, (0.72, 0.80, 0.95), 22.0)


def configure_eevee(scene: bpy.types.Scene) -> None:
    for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue
    eevee = getattr(scene, "eevee", None)
    if eevee is None:
        return
    for attr, value in (
        ("taa_render_samples", 36),
        ("use_shadows", True),
        ("use_raytracing", True),
        ("use_bloom", True),
        ("bloom_intensity", 0.16),
        ("bloom_radius", 6.0),
    ):
        if hasattr(eevee, attr):
            setattr(eevee, attr, value)


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
        "collections": COLLECTION_ORDER,
    }


def export_glb() -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in EXPORTABLE:
        obj.select_set(True)
    kwargs = dict(
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
    try:
        bpy.ops.export_scene.gltf(**kwargs, export_image_format="AUTO")
    except TypeError:
        bpy.ops.export_scene.gltf(**kwargs)


def render_qa() -> list[str]:
    scene = bpy.context.scene
    configure_eevee(scene)
    scene.render.image_settings.file_format = "PNG"
    rendered: list[str] = []
    wanted = {
        "CAM_SYSTEM_HERO",
        "CAM_Identity_Monolith_Closeup",
        "CAM_SIGNAGE_CLOSEUP",
        "CAM_PORTFOLIO_FACADE_SYSTEM",
        "CAM_Gate",
    }
    cameras = [obj for obj in bpy.data.objects if obj.type == "CAMERA"]
    if os.environ.get("FULL_QA") != "1":
        cameras = [cam for cam in cameras if cam.name in wanted]
    for cam in cameras:
        scene.camera = cam
        out = RENDER_DIR / f"{cam.name}.png"
        scene.render.filepath = str(out)
        bpy.ops.render.render(write_still=True)
        rendered.append(str(out))
    return rendered


def rename_actions() -> None:
    for action in list(bpy.data.actions):
        if "Door" in action.name and "Open" not in action.name:
            action.name = "DoorOpen_" + action.name.replace(" ", "")
        if "Gate" in action.name or "Main_Gate" in action.name:
            action.name = "GateOpen_" + action.name.replace(" ", "")
    if "PROP_Door_Main_LAction" in bpy.data.actions:
        bpy.data.actions["PROP_Door_Main_LAction"].name = "DoorOpen"


def main() -> None:
    ensure_dirs()
    reset_scene()
    mats = materials()
    build_ground(mats)
    build_stairs(mats)
    build_masses(mats)
    build_structure(mats)
    build_glazing(mats)
    build_interior_depth(mats)
    build_entrance(mats)
    build_boundary_and_gate(mats)
    build_identity(mats)
    build_portfolio_bays(mats)
    build_water(mats)
    build_landscape(mats)
    build_collision()
    build_anchors()
    parent_to_root()
    build_qa_cameras_and_lights()
    rename_actions()
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    rendered = render_qa()
    export_glb()
    stats = collect_stats()
    if GLB_PATH.exists():
        stats["glbBytes"] = GLB_PATH.stat().st_size
    stats["renders"] = rendered
    STATS_PATH.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    (SCRIPT_DIR / "last-build-stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    bpy.ops.wm.save_mainfile()
    print("BUILD_STATS", json.dumps(stats))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("BUILD_FAILED", exc, file=sys.stderr)
        raise
