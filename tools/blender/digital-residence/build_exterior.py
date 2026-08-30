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
    base = 0.24 + n * 0.09 + vein - pit
    if mortar:
        base *= 0.62
    return (base * 1.04, base * 1.01, base * 0.96)


def paint_concrete(u: float, v: float, x: int, y: int) -> tuple[float, float, float]:
    n = fbm(u * 6.0, v * 6.0, 8.1)
    speckle = 0.025 * hash_noise(x * 0.37, y * 0.41, 3.0)
    g = 0.34 + n * 0.08 + speckle
    return (g * 0.98, g * 0.99, g * 1.02)


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
    g = 0.13 + n * 0.05
    return (g * 0.96, g * 0.98, g * 1.04)


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
    ramp.color_ramp.elements[0].color = (0.34, 0.36, 0.38, 1.0)
    mid = ramp.color_ramp.elements.new(0.34)
    mid.color = (0.18, 0.22, 0.28, 1.0)
    ramp.color_ramp.elements[-1].position = 1.0
    ramp.color_ramp.elements[-1].color = (0.08, 0.12, 0.18, 1.0)
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
            "MAT_Stone_Graphite", stone_img, roughness=0.58, scale=2.2, bump_strength=0.18
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
        "clay": untextured_material("MAT_Clay_Neutral", color=(0.52, 0.50, 0.47), roughness=0.72),
        "glass": untextured_material(
            "MAT_Glass_Smoked",
            color=(0.16, 0.165, 0.17),
            roughness=0.045,
            transmission=0.0,
            alpha=0.18,
        ),
        "glass_clear": untextured_material(
            "MAT_Glass_Clear",
            color=(0.20, 0.205, 0.21),
            roughness=0.03,
            transmission=0.0,
            alpha=0.10,
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
            color=(0.72, 0.64, 0.52),
            metallic=0.92,
            roughness=0.32,
            emission=(0.36, 0.30, 0.22),
            emission_strength=0.16,
        ),
        "sign_back": untextured_material(
            "MAT_Sign_Backlight",
            color=(0.10, 0.08, 0.06),
            roughness=0.62,
            emission=(0.72, 0.52, 0.28),
            emission_strength=0.85,
        ),
        "sign_zone": untextured_material(
            "MAT_Sign_Zone",
            color=(0.62, 0.64, 0.66),
            metallic=0.48,
            roughness=0.40,
            emission=(0.28, 0.30, 0.32),
            emission_strength=0.18,
        ),
        "sign_cyan": untextured_material(
            "MAT_Sign_Cyan",
            color=(0.14, 0.48, 0.54),
            metallic=0.28,
            roughness=0.36,
            emission=(0.12, 0.55, 0.62),
            emission_strength=0.72,
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


def make_roof(
    name: str,
    size: tuple[float, float, float],
    origin: tuple[float, float, float],
    mats: dict[str, bpy.types.Material],
    arch: bpy.types.Collection,
    facade: bpy.types.Collection,
    lights: bpy.types.Collection,
    *,
    parapet: float = 0.52,
) -> None:
    sx, sy, sz = size
    make_box(name, size, origin, mats["metal"], arch, bevel=True, bevel_width=0.035)
    south = origin[1] - sy * 0.5
    make_box(
        name + "_Fascia",
        (sx + 0.10, 0.16, 0.22),
        (origin[0], south + 0.02, origin[2] - 0.14),
        mats["metal"],
        arch,
        bevel=True,
        bevel_width=0.015,
    )
    make_box(
        name + "_Soffit",
        (sx - 0.30, sy - 0.28, 0.06),
        (origin[0], origin[1] + 0.04, origin[2] - 0.02),
        mats["wood"],
        facade,
    )
    make_box(
        name + "_Parapet",
        (sx + 0.08, 0.18, parapet),
        (origin[0], south + 0.04, origin[2] + sz),
        mats["metal"],
        arch,
        bevel=True,
        bevel_width=0.012,
    )
    make_box(
        "LIGHT_" + name + "_Cove",
        (sx - 0.50, 0.045, 0.03),
        (origin[0], south + 0.22, origin[2] - 0.05),
        mats["led_warm"],
        lights,
        unwrap=False,
    )


def make_curtain(
    prefix: str,
    width: float,
    height: float,
    origin: tuple[float, float, float],
    mats: dict[str, bpy.types.Material],
    glass_col: bpy.types.Collection,
    facade: bpy.types.Collection,
    *,
    module: float = 1.55,
    smoked: bool = False,
) -> None:
    glass_mat = mats["glass"] if smoked else mats["glass_clear"]
    make_box(prefix, (width, 0.06, height), origin, glass_mat, glass_col)
    count = max(2, int(round(width / module)))
    spacing = width / count
    x0 = origin[0] - width * 0.5 + spacing
    mullions = []
    for i in range(count - 1):
        mullions.append(
            make_box(
                f"{prefix}_Mullion_{i+1:02d}",
                (0.09, 0.18, height),
                (x0 + i * spacing, origin[1] + 0.07, origin[2]),
                mats["metal"],
                facade,
                exportable=False,
                unwrap=False,
            )
        )
    if mullions:
        join_objects(prefix + "_Mullions", mullions, facade)
    make_box(prefix + "_Head", (width + 0.12, 0.20, 0.14), (origin[0], origin[1] + 0.08, origin[2] + height - 0.04), mats["metal"], facade, bevel=True)
    make_box(prefix + "_Sill", (width + 0.12, 0.22, 0.12), (origin[0], origin[1] + 0.08, origin[2]), mats["metal"], facade)
    make_box(prefix + "_Transom", (width, 0.16, 0.08), (origin[0], origin[1] + 0.07, origin[2] + height * 0.62), mats["metal"], facade, unwrap=False)


def make_empty(name: str, location: tuple[float, float, float], collection: bpy.types.Collection) -> bpy.types.Object:
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = "PLAIN_AXES"
    empty.empty_display_size = 0.6
    empty.location = location
    collection.objects.link(empty)
    EXPORTABLE.append(empty)
    return empty


_SIGN_FONT_BOLD = None
_SIGN_FONT_BOOK = None


def _load_font(candidates: tuple[Path, ...]):
    for candidate in candidates:
        if candidate.exists():
            return bpy.data.fonts.load(str(candidate))
    return None


def sign_font_bold():
    global _SIGN_FONT_BOLD
    if _SIGN_FONT_BOLD is not None:
        return _SIGN_FONT_BOLD
    _SIGN_FONT_BOLD = _load_font(
        (
            Path(r"C:\Windows\Fonts\segoeuib.ttf"),
            Path(r"C:\Windows\Fonts\calibrib.ttf"),
            Path(r"C:\Windows\Fonts\arialbd.ttf"),
        )
    )
    return _SIGN_FONT_BOLD


def sign_font_book():
    global _SIGN_FONT_BOOK
    if _SIGN_FONT_BOOK is not None:
        return _SIGN_FONT_BOOK
    _SIGN_FONT_BOOK = _load_font(
        (
            Path(r"C:\Windows\Fonts\segoeui.ttf"),
            Path(r"C:\Windows\Fonts\calibri.ttf"),
            Path(r"C:\Windows\Fonts\arial.ttf"),
        )
    )
    return _SIGN_FONT_BOOK or sign_font_bold()


def cap_size(meters: float) -> float:
    """Blender text size that yields approximately `meters` of capital height."""
    return meters / 0.43


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
    space: float = 0.94,
    bevel_depth: float | None = None,
    align_x: str = "CENTER",
    weight: str = "bold",
) -> bpy.types.Object:
    bpy.ops.object.text_add(location=(0.0, 0.0, 0.0))
    obj = bpy.context.active_object
    curve = obj.data
    curve.body = body
    curve.size = size
    curve.extrude = extrude
    curve.bevel_depth = (
        bevel_depth if bevel_depth is not None else max(0.0006, min(0.010, size * 0.006, extrude * 0.32))
    )
    curve.space_character = space
    curve.align_x = align_x
    curve.align_y = "CENTER"
    font = sign_font_book() if weight == "book" else sign_font_bold()
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


def make_zone_plaque(
    mats: dict[str, bpy.types.Material],
    collection: bpy.types.Collection,
    *,
    slot_name: str,
    number: str,
    title_lines: tuple[str, ...],
    tagline: str,
    loc: tuple[float, float, float],
    size: tuple[float, float, float],
) -> None:
    south = loc[1] - size[1] * 0.5
    left = loc[0] - size[0] * 0.38
    make_box(slot_name, size, loc, mats["metal_dark"], collection, bevel=True, bevel_width=0.012)
    make_box(
        slot_name + "_Bed",
        (size[0] - 0.16, 0.028, size[2] - 0.16),
        (loc[0], south + 0.038, loc[2] + 0.08),
        mats["sign_back"],
        collection,
        bevel=False,
        unwrap=False,
    )
    top = loc[2] + size[2]
    make_face_lettering(
        slot_name + "_No",
        number,
        face_point=(left, south, top - 0.20),
        normal=(0.0, -1.0, 0.0),
        size=cap_size(0.18),
        extrude=0.010,
        mat=mats["sign_cyan"],
        collection=collection,
        offset=0.016,
        space=1.04,
        bevel_depth=0.0012,
        align_x="LEFT",
        weight="bold",
    )
    line_h = 0.28 if len(title_lines) == 1 else 0.26
    title_top = top - 0.46
    for index, line in enumerate(title_lines):
        make_face_lettering(
            slot_name + f"_Title_{index+1:02d}",
            line,
            face_point=(left, south, title_top - index * (line_h + 0.07)),
            normal=(0.0, -1.0, 0.0),
            size=cap_size(line_h),
            extrude=0.014,
            mat=mats["sign"],
            collection=collection,
            offset=0.018,
            space=1.00,
            bevel_depth=0.0020,
            align_x="LEFT",
            weight="bold",
        )
    make_face_lettering(
        slot_name + "_Tag",
        tagline,
        face_point=(left, south, loc[2] + 0.18),
        normal=(0.0, -1.0, 0.0),
        size=cap_size(0.11),
        extrude=0.005,
        mat=mats["sign_zone"],
        collection=collection,
        offset=0.014,
        space=1.06,
        bevel_depth=0.0006,
        align_x="LEFT",
        weight="book",
    )


def build_portfolio_bays(mats: dict[str, bpy.types.Material]) -> None:
    facade = col("02_FACADE")
    depth = 0.10
    plaques = [
        {
            "slot_name": "SIGN_SLOT_Identity",
            "number": "01",
            "title_lines": ("IDENTITY", "ATRIUM"),
            "tagline": "Arrive. Belong. Begin.",
            "loc": (-8.05, -4.20 + depth * 0.5, 3.05),
            "size": (2.15, depth, 1.48),
        },
        {
            "slot_name": "SIGN_SLOT_Engineering",
            "number": "02",
            "title_lines": ("ENGINEERING", "WING"),
            "tagline": "Build. Architect. Solve.",
            "loc": (-17.22, -9.72 + depth * 0.5, 6.28),
            "size": (1.92, depth, 1.52),
        },
        {
            "slot_name": "SIGN_SLOT_AILab",
            "number": "03",
            "title_lines": ("AI LAB",),
            "tagline": "Models. Agents. Systems.",
            "loc": (15.85, -1.15 + depth * 0.5, 10.05),
            "size": (2.15, depth, 1.36),
        },
        {
            "slot_name": "SIGN_SLOT_Projects",
            "number": "04",
            "title_lines": ("PROJECTS", "GALLERY"),
            "tagline": "Selected Work.",
            "loc": (13.55, -4.55 + depth * 0.5, 4.05),
            "size": (2.15, depth, 1.48),
        },
        {
            "slot_name": "SIGN_SLOT_Architecture",
            "number": "05",
            "title_lines": ("ARCHITECTURE", "CORE"),
            "tagline": "Spaces. Structure. Craft.",
            "loc": (-13.25, -4.20 + depth * 0.5, 2.85),
            "size": (2.15, depth, 1.48),
        },
        {
            "slot_name": "SIGN_SLOT_Command",
            "number": "06",
            "title_lines": ("COMMAND", "CENTER"),
            "tagline": "Live State.",
            "loc": (3.55, -1.35 + depth * 0.5, 10.08),
            "size": (2.15, depth, 1.48),
        },
    ]
    for plaque in plaques:
        make_zone_plaque(mats, facade, **plaque)


def build_stairs(mats: dict[str, bpy.types.Material]) -> None:
    arch = col("01_ARCHITECTURE")
    lights = col("10_LIGHTS")
    # Stepped foundations — not a single plaza pad.
    make_box("ENV_Foundation_Atrium", (26.5, 16.8, 1.80), (0.8, 2.4, 0.0), mats["stone"], arch, bevel=True, bevel_width=0.07)
    make_box("ENV_Foundation_West", (15.4, 13.2, 1.15), (-14.8, 1.4, 0.0), mats["stone"], arch, bevel=True, bevel_width=0.06)
    make_box("ENV_Foundation_East", (14.8, 12.4, 1.40), (14.6, 1.8, 0.0), mats["stone"], arch, bevel=True, bevel_width=0.06)
    make_box("ENV_Foundation_Retain_S", (34.0, 0.72, 2.55), (0.4, -9.55, -0.55), mats["stone"], arch, bevel=True, bevel_width=0.05)
    make_box("ENV_Foundation_Retain_SW", (0.72, 10.8, 2.15), (-16.6, -5.4, -0.20), mats["stone"], arch, bevel=True)
    make_box("ENV_Foundation_Shelf_W", (9.4, 6.2, 0.85), (-18.4, -6.8, 0.0), mats["stone"], arch, bevel=True)
    make_box("ENV_Monolith_Terrace", (9.2, 11.4, 0.95), (-24.6, 0.8, 0.0), mats["stone"], arch, bevel=True, bevel_width=0.05)
    make_box("ENV_Entrance_Platform", (18.4, 8.6, 0.18), (0.0, -2.35, 1.80), mats["paving"], arch, bevel=True, bevel_width=0.04)
    make_box("ENV_Terrace_Arrival", (12.6, 2.8, 0.14), (0.0, -7.15, 1.80), mats["paving"], arch, bevel=True)
    treads = []
    nosings = []
    tread_lights = []
    for i in range(12):
        y = -8.05 - i * 0.42
        z = 1.80 - i * 0.15
        treads.append(
            make_box(
                f"ENV_Stairs_Tread_{i:02d}",
                (6.50, 0.40, 0.15),
                (0.0, y, z),
                mats["stone"],
                arch,
                bevel=True,
                bevel_width=0.012,
                exportable=False,
            )
        )
        nosings.append(
            make_box(
                f"ENV_Stairs_Nosing_{i:02d}",
                (6.50, 0.04, 0.03),
                (0.0, y - 0.20, z + 0.15),
                mats["metal"],
                arch,
                exportable=False,
                unwrap=False,
            )
        )
        tread_lights.append(
            make_box(
                f"LIGHT_Stair_{i:02d}",
                (5.8, 0.03, 0.02),
                (0.0, y + 0.12, z + 0.14),
                mats["led_warm"],
                lights,
                exportable=False,
                unwrap=False,
            )
        )
    join_objects("ENV_Entrance_Steps", treads, arch)
    join_objects("ENV_Entrance_Nosings", nosings, arch)
    join_objects("LIGHT_Stair_Wash", tread_lights, lights)
    make_box("ENV_Stair_Cheek_L", (0.55, 5.4, 2.05), (-3.52, -10.35, 0.0), mats["stone"], arch, bevel=True, bevel_width=0.04)
    make_box("ENV_Stair_Cheek_R", (0.55, 5.4, 2.05), (3.52, -10.35, 0.0), mats["stone"], arch, bevel=True, bevel_width=0.04)
    make_box("ENV_Approach_Landing", (7.2, 7.4, 0.12), (0.0, -17.6, 0.08), mats["paving"], arch, bevel=True)


def build_masses(mats: dict[str, bpy.types.Material]) -> None:
    arch = col("01_ARCHITECTURE")
    facade = col("02_FACADE")
    lights = col("10_LIGHTS")
    # Vertical spine — one core from arrival through Command.
    make_box("ENV_Spine_Core", (5.40, 7.40, 11.05), (0.0, 5.55, 1.80), mats["stone"], arch, bevel=True, bevel_width=0.08)
    # Identity Atrium — double-height chamber grown around the spine.
    make_box("ENV_Atrium_Floor", (14.6, 12.8, 0.22), (0.0, 2.10, 1.80), mats["stone"], arch, bevel=True)
    make_box("ENV_Atrium_Wall_L", (0.72, 12.2, 7.60), (-6.95, 2.20, 1.80), mats["stone"], arch, bevel=True, bevel_width=0.05)
    make_box("ENV_Atrium_Wall_R", (0.72, 12.2, 7.60), (6.95, 2.20, 1.80), mats["stone"], arch, bevel=True, bevel_width=0.05)
    make_box("ENV_Atrium_Back", (14.6, 0.70, 7.60), (0.0, 8.15, 1.80), mats["stone"], arch, bevel=True)
    make_box("ENV_Atrium_Mezzanine", (10.2, 3.40, 0.22), (0.0, 4.85, 5.60), mats["concrete"], arch, bevel=True)
    make_box("ENV_Atrium_Portal_L", (1.35, 1.70, 7.55), (-4.55, -3.85, 1.80), mats["stone"], arch, bevel=True, bevel_width=0.05)
    make_box("ENV_Atrium_Portal_R", (1.35, 1.70, 7.55), (4.55, -3.85, 1.80), mats["stone"], arch, bevel=True, bevel_width=0.05)
    # Architecture Core — heaviest L0 mass, west of atrium, shared west wall.
    make_box("ENV_Architecture_Core", (12.6, 15.8, 3.80), (-13.25, 3.70, 1.80), mats["stone"], arch, bevel=True, bevel_width=0.08)
    make_box("ENV_Architecture_Link", (2.40, 10.4, 3.80), (-7.40, 3.40, 1.80), mats["stone"], arch, bevel=True)
    # Engineering — L1 volume grown from the core, cantilever explained by shear + beam + columns.
    make_box("ENV_Engineering_Body", (15.4, 13.2, 3.80), (-16.55, 3.10, 5.60), mats["concrete"], arch, bevel=True, bevel_width=0.07)
    make_box("ENV_Engineering_Shear", (0.62, 16.4, 9.40), (-24.15, 1.10, 0.0), mats["concrete"], arch, bevel=True, bevel_width=0.05)
    make_box("ENV_Engineering_Beam", (15.0, 0.72, 0.72), (-16.55, -3.50, 8.68), mats["metal"], arch, bevel=True, bevel_width=0.03)
    make_box("ENV_Engineering_Backspan", (4.20, 8.6, 3.80), (-8.40, 4.20, 5.60), mats["concrete"], arch, bevel=True)
    make_box("ENV_Engineering_Cantilever", (14.8, 9.40, 0.48), (-16.55, -5.55, 8.92), mats["concrete"], arch, bevel=True, bevel_width=0.04)
    make_box("ENV_Engineering_Soffit", (14.2, 8.90, 0.07), (-16.55, -5.55, 8.86), mats["wood"], facade)
    for i, x in enumerate((-21.4, -16.55, -11.7)):
        make_box(
            f"ENV_Engineering_Col_{i+1:02d}",
            (0.48, 0.48, 8.92),
            (x, -7.85, 0.0),
            mats["metal"],
            arch,
            bevel=True,
            bevel_width=0.02,
        )
        make_box(
            f"ENV_Engineering_ColBase_{i+1:02d}",
            (0.72, 0.72, 0.28),
            (x, -7.85, 0.0),
            mats["stone"],
            arch,
            bevel=True,
        )
    # Projects Gallery — L0+L1 east of atrium, same roof datum.
    make_box("ENV_Projects_Gallery", (13.4, 14.2, 7.60), (13.55, 2.55, 1.80), mats["concrete"], arch, bevel=True, bevel_width=0.06)
    make_box("ENV_Projects_Link", (2.50, 10.6, 7.60), (7.40, 2.80, 1.80), mats["concrete"], arch, bevel=True)
    make_box("ENV_Terrace_Projects", (12.8, 3.10, 0.16), (13.55, -5.85, 1.80), mats["paving"], arch, bevel=True)
    # AI Lab — set back on the gallery roof, carried by the gallery mass.
    make_box("ENV_AI_Lab", (11.6, 11.4, 3.45), (15.85, 4.55, 9.40), mats["metal_dark"], arch, bevel=True, bevel_width=0.06)
    make_box("ENV_AI_Lab_Core", (0.55, 10.2, 3.45), (10.25, 4.40, 9.40), mats["metal_dark"], arch, bevel=True)
    make_box("ENV_AI_Lab_Return_L", (0.42, 0.55, 3.45), (10.25, -1.05, 9.40), mats["metal"], arch, bevel=True)
    make_box("ENV_AI_Lab_Return_R", (0.42, 0.55, 3.45), (21.45, -1.05, 9.40), mats["metal"], arch, bevel=True)
    # Command Center — privileged L2, spine punches through, set back from atrium glass.
    make_box("ENV_Command_Center", (16.6, 11.2, 3.45), (3.55, 4.25, 9.40), mats["stone"], arch, bevel=True, bevel_width=0.06)
    make_box("ENV_Command_Return_L", (0.48, 0.55, 3.45), (-4.55, -1.25, 9.40), mats["metal"], arch, bevel=True)
    make_box("ENV_Command_Return_R", (0.48, 0.55, 3.45), (11.65, -1.25, 9.40), mats["metal"], arch, bevel=True)
    # Shared terraces / floor plates that stitch wings together.
    make_box("ENV_Terrace_L1", (28.5, 3.40, 0.18), (-2.4, -6.35, 5.60), mats["paving"], arch, bevel=True, bevel_width=0.03)
    make_box("ENV_Datum_L1", (38.4, 0.58, 0.42), (-1.2, -6.55, 5.60), mats["concrete"], arch, bevel=True, bevel_width=0.04)
    make_box("ENV_Terrace_L2", (22.4, 2.55, 0.16), (6.8, -2.55, 9.40), mats["paving"], arch, bevel=True)
    make_box("ENV_Plate_Atrium", (16.8, 14.2, 0.22), (0.0, 2.10, 9.18), mats["concrete"], arch, bevel=True, bevel_width=0.03)
    make_roof("ENV_Roof_AtriumEdge", (16.8, 5.2, 0.42), (0.0, -3.05, 9.40), mats, arch, facade, lights, parapet=0.42)
    make_roof("ENV_Roof_Engineering", (16.2, 20.4, 0.42), (-16.55, 0.55, 9.40), mats, arch, facade, lights, parapet=0.50)
    make_roof("ENV_Roof_AILab", (12.2, 12.0, 0.38), (15.85, 4.55, 12.85), mats, arch, facade, lights, parapet=0.46)
    make_roof("ENV_Roof_Command", (17.4, 11.8, 0.42), (3.55, 4.25, 12.85), mats, arch, facade, lights, parapet=0.55)
    # Monumental canopy — thick, back-spanned into the portal lintel.
    make_box("ENV_Canopy_Entrance", (16.8, 7.40, 0.46), (0.0, -6.05, 6.85), mats["metal"], arch, bevel=True, bevel_width=0.04)
    make_box("ENV_Canopy_Soffit", (16.2, 7.00, 0.07), (0.0, -6.05, 6.80), mats["wood"], facade)
    make_box("ENV_Canopy_Fascia", (16.9, 0.16, 0.22), (0.0, -9.72, 6.71), mats["metal"], arch, bevel=True)
    make_box("ENV_Canopy_Backspan", (10.4, 2.20, 0.46), (0.0, -3.55, 6.85), mats["metal"], arch, bevel=True)
    make_box("LIGHT_Canopy_Cove", (15.6, 0.05, 0.03), (0.0, -9.45, 6.82), mats["led_warm"], lights, unwrap=False)


def build_structure(mats: dict[str, bpy.types.Material]) -> None:
    facade = col("02_FACADE")
    lights = col("10_LIGHTS")
    columns = []
    bases = []
    for i, x in enumerate((-5.40, -2.15, 2.15, 5.40)):
        bases.append(
            make_box(
                f"ENV_ColumnBase_{i+1:02d}",
                (0.70, 0.70, 0.30),
                (x, -6.85, 1.80),
                mats["stone"],
                facade,
                bevel=True,
                bevel_width=0.03,
                exportable=False,
            )
        )
        columns.append(
            make_box(
                f"ENV_Column_{i+1:02d}",
                (0.46, 0.46, 5.05),
                (x, -6.85, 2.10),
                mats["metal"],
                facade,
                bevel=True,
                bevel_width=0.02,
                exportable=False,
            )
        )
    join_objects("ENV_Portico_ColumnBases", bases, facade)
    join_objects("ENV_Portico_Columns", columns, facade)
    make_box("ENV_Frame_Portal_L", (0.28, 1.55, 7.40), (-3.95, -3.85, 1.82), mats["metal"], facade, bevel=True)
    make_box("ENV_Frame_Portal_R", (0.28, 1.55, 7.40), (3.95, -3.85, 1.82), mats["metal"], facade, bevel=True)
    make_box("ENV_Frame_Lobby_Head", (8.40, 0.42, 0.32), (0.0, -3.85, 9.05), mats["metal"], facade, bevel=True)
    make_box("ENV_Frame_Lobby_Sill", (8.40, 0.28, 0.14), (0.0, -3.85, 1.82), mats["metal"], facade)
    fins = []
    for i in range(7):
        fins.append(
            make_box(
                f"ENV_Fin_West_{i+1:02d}",
                (0.12, 2.85, 3.55),
                (-23.4 + i * 1.45, -3.55, 1.95),
                mats["metal"],
                facade,
                exportable=False,
                unwrap=False,
            )
        )
    join_objects("ENV_West_Fins", fins, facade)
    eng_fins = []
    for i in range(6):
        eng_fins.append(
            make_box(
                f"ENV_Fin_Engineering_{i+1:02d}",
                (0.10, 1.85, 3.55),
                (-22.6 + i * 2.15, -8.85, 5.70),
                mats["metal"],
                facade,
                exportable=False,
                unwrap=False,
            )
        )
    join_objects("ENV_Engineering_Fins", eng_fins, facade)
    make_box("LIGHT_FacadeWash_L", (0.05, 0.04, 3.4), (-16.55, -3.6, 2.1), mats["led_warm"], lights, unwrap=False)
    make_box("LIGHT_FacadeWash_R", (0.05, 0.04, 5.8), (13.55, -4.2, 2.1), mats["led_warm"], lights, unwrap=False)
    make_box("LIGHT_AILab_Slot", (9.6, 0.04, 0.04), (15.85, -0.85, 12.72), mats["led_cool"], lights, unwrap=False)
    make_box("LIGHT_SLOT_Entrance_L", (0.04, 1.4, 6.8), (-4.55, -3.55, 1.90), mats["led_warm"], lights, unwrap=False)
    make_box("LIGHT_SLOT_Entrance_R", (0.04, 1.4, 6.8), (4.55, -3.55, 1.90), mats["led_warm"], lights, unwrap=False)


def build_glazing(mats: dict[str, bpy.types.Material]) -> None:
    glass = col("03_GLASS")
    facade = col("02_FACADE")
    make_curtain("ENV_Glass_Lobby", 7.85, 7.25, (0.0, -2.45, 1.88), mats, glass, facade, module=1.48)
    make_curtain("ENV_Glass_Engineering", 13.4, 3.35, (-16.55, -8.35, 5.70), mats, glass, facade, module=1.68, smoked=True)
    make_curtain("ENV_Glass_Projects", 11.6, 7.15, (13.55, -4.15, 1.88), mats, glass, facade, module=1.65)
    make_curtain("ENV_Glass_AILab", 10.4, 3.15, (15.85, -0.85, 9.50), mats, glass, facade, module=1.48, smoked=True)
    make_curtain("ENV_Glass_Command", 15.2, 3.15, (3.55, -1.15, 9.50), mats, glass, facade, module=1.70)
    punches = []
    for i, z in enumerate((2.55, 3.95)):
        for j in range(3):
            punches.append(
                make_box(
                    f"ENV_Glass_ArchPunch_{i}{j}",
                    (1.45, 0.08, 0.95),
                    (-16.8 + j * 2.15, -4.05, z),
                    mats["glass"],
                    glass,
                    exportable=False,
                    unwrap=False,
                )
            )
    join_objects("ENV_Glass_Architecture", punches, glass)
    make_box("ENV_Railing_Arrival", (12.2, 0.05, 1.05), (0.0, -8.45, 1.82), mats["glass_clear"], glass)
    make_box("ENV_Railing_Arrival_Cap", (12.4, 0.08, 0.05), (0.0, -8.45, 2.87), mats["metal"], facade)
    make_box("ENV_Railing_L1", (28.0, 0.05, 0.98), (-2.4, -8.00, 5.78), mats["glass_clear"], glass)
    make_box("ENV_Railing_L1_Cap", (28.2, 0.08, 0.05), (-2.4, -8.00, 6.76), mats["metal"], facade)
    make_box("ENV_Railing_L2", (21.8, 0.05, 0.92), (6.8, -3.75, 9.56), mats["glass_clear"], glass)
    make_box("ENV_Railing_L2_Cap", (22.0, 0.08, 0.05), (6.8, -3.75, 10.48), mats["metal"], facade)


def build_interior_depth(mats: dict[str, bpy.types.Material]) -> None:
    props = col("09_PROPS")
    lights = col("10_LIGHTS")
    make_box("ENV_Interior_LobbyFloor", (12.8, 10.6, 0.10), (0.0, 2.0, 1.82), mats["wood"], props)
    make_box("ENV_Interior_LobbyCeiling", (12.8, 10.6, 0.10), (0.0, 2.0, 9.18), mats["interior"], lights)
    make_box("LIGHT_Lobby_Fill", (10.8, 8.2, 0.05), (0.0, 1.8, 8.95), mats["interior"], lights, unwrap=False)
    make_box("ENV_Interior_LobbyBack", (12.4, 0.16, 7.10), (0.0, 7.70, 1.88), mats["interior_wall"], props)
    make_box("ENV_Interior_Lobby_Wall_L", (0.12, 9.4, 7.00), (-6.45, 2.1, 1.88), mats["interior_wall"], props)
    make_box("ENV_Interior_Lobby_Wall_R", (0.12, 9.4, 7.00), (6.45, 2.1, 1.88), mats["interior_wall"], props)
    make_box("PROP_Lobby_Screen", (4.2, 0.10, 2.15), (0.0, 7.55, 3.55), mats["rack"], props)
    make_box("PROP_Lobby_Bench", (3.4, 0.85, 0.48), (-2.6, 0.4, 1.82), mats["wood"], props, bevel=True)
    make_box("PROP_Lobby_Console", (2.2, 0.58, 0.95), (2.8, 2.4, 1.82), mats["bronze"], props, bevel=True)
    make_box("PROP_Atrium_Feature", (1.15, 1.15, 2.40), (0.0, 3.2, 1.82), mats["bronze"], props, bevel=True, bevel_width=0.04)
    make_box("LIGHT_Lobby_Cove", (11.6, 0.05, 0.05), (0.0, 2.0, 9.05), mats["led_warm"], lights)
    make_box("ENV_Interior_EngineeringFloor", (14.2, 11.6, 0.10), (-16.55, 2.6, 5.62), mats["wood"], props)
    make_box("ENV_Interior_EngineeringBack", (13.8, 0.14, 3.35), (-16.55, 8.4, 5.70), mats["interior_wall"], props)
    make_box("ENV_Interior_ProjectsFloor", (12.2, 11.4, 0.10), (13.55, 2.4, 1.82), mats["wood"], props)
    make_box("ENV_Interior_ProjectsBack", (11.8, 0.14, 7.00), (13.55, 8.4, 1.88), mats["interior_wall"], props)
    make_box("ENV_Interior_ProjectsSlab", (12.0, 10.8, 0.16), (13.55, 2.6, 5.55), mats["wood"], props)
    make_box("ENV_Interior_AILabFloor", (10.6, 9.8, 0.10), (15.85, 4.4, 9.42), mats["interior_wall"], props)
    make_box("ENV_Interior_AILabBack", (10.2, 0.14, 3.10), (15.85, 9.4, 9.50), mats["interior_wall"], props)
    make_box("ENV_Interior_CommandFloor", (15.6, 9.6, 0.08), (3.55, 4.1, 9.42), mats["wood"], props)
    make_box("ENV_Interior_CommandCeiling", (15.6, 9.6, 0.06), (3.55, 4.1, 12.72), mats["interior"], lights)
    make_box("LIGHT_L1_Fill", (12.4, 8.0, 0.04), (-16.55, 2.2, 9.15), mats["interior"], lights, unwrap=False)
    make_box("LIGHT_Command_Fill", (13.6, 7.2, 0.04), (3.55, 3.8, 12.55), mats["interior"], lights, unwrap=False)
    make_box("LIGHT_AILab_Fill", (9.2, 6.4, 0.04), (15.85, 4.2, 12.55), mats["interior"], lights, unwrap=False)
    make_box("PROP_Stair_Hint", (1.55, 4.2, 0.14), (1.55, 5.1, 3.55), mats["bronze"], props, bevel=True)
    racks = []
    edges = []
    for i in range(6):
        racks.append(
            make_box(
                f"PROP_ServerHint_{i+1:02d}",
                (0.52, 0.85, 1.85),
                (11.4 + (i % 3) * 1.45, 3.1 + (i // 3) * 2.1, 1.90),
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
                (11.4 + (i % 3) * 1.45, 2.65 + (i // 3) * 2.1, 1.96),
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
    make_box("ENV_Portal_Lintel", (9.4, 1.70, 0.48), (0.0, -3.85, 9.00), mats["metal"], arch, bevel=True, bevel_width=0.03)
    make_box("ENV_Portal_Jamb_L", (0.55, 1.70, 7.20), (-4.45, -3.85, 1.80), mats["metal"], arch, bevel=True)
    make_box("ENV_Portal_Jamb_R", (0.55, 1.70, 7.20), (4.45, -3.85, 1.80), mats["metal"], arch, bevel=True)
    canopy_south = -6.05 - 7.40 * 0.5
    make_box(
        "PROP_Residence_NameBar",
        (7.40, 0.12, 0.78),
        (0.0, canopy_south - 0.04, 6.38),
        mats["metal_dark"],
        props,
        bevel=True,
        bevel_width=0.014,
    )
    make_box(
        "PROP_Residence_NameBed",
        (6.85, 0.03, 0.52),
        (0.0, canopy_south - 0.08, 6.50),
        mats["sign_back"],
        props,
        bevel=False,
        unwrap=False,
    )
    make_face_lettering(
        "PROP_Residence_Name",
        "DIGITAL RESIDENCE",
        face_point=(0.0, canopy_south - 0.10, 6.78),
        normal=(0.0, -1.0, 0.0),
        size=cap_size(0.42),
        extrude=0.022,
        mat=mats["sign"],
        collection=props,
        offset=0.020,
        space=1.04,
        bevel_depth=0.0032,
        weight="bold",
    )
    make_box("LIGHT_Entrance_Warm", (8.2, 0.06, 0.06), (0.0, -4.55, 8.85), mats["led_warm"], lights)
    make_box("LIGHT_Cantilever_Cove", (14.0, 0.06, 0.05), (-16.55, -9.85, 8.88), mats["led_warm"], lights)
    make_box("LIGHT_Command_Cove", (15.4, 0.05, 0.04), (3.55, -1.15, 9.38), mats["led_warm"], lights)
    make_box("LIGHT_EastCrown", (10.8, 0.05, 0.05), (15.85, -0.85, 12.78), mats["led_cool"], lights)
    left = make_box("PROP_Door_Main_L", (2.15, 0.16, 6.25), (-2.20, -2.55, 1.82), mats["metal_dark"], anim, bevel=True, bevel_width=0.01)
    right = make_box("PROP_Door_Main_R", (2.15, 0.16, 6.25), (2.20, -2.55, 1.82), mats["metal_dark"], anim, bevel=True, bevel_width=0.01)
    select_only(left)
    bpy.context.scene.cursor.location = (-3.18, -2.55, 1.82)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    select_only(right)
    bpy.context.scene.cursor.location = (3.18, -2.55, 1.82)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    for door, angle in ((left, 82), (right, -82)):
        door.keyframe_insert(data_path="rotation_euler", frame=1)
        door.rotation_euler[2] = math.radians(angle)
        door.keyframe_insert(data_path="rotation_euler", frame=70)
        door.rotation_euler[2] = 0.0
    make_box("PROP_Door_Handle_L", (0.04, 0.09, 0.62), (-0.18, -2.65, 4.15), mats["bronze"], props, unwrap=False)
    make_box("PROP_Door_Handle_R", (0.04, 0.09, 0.62), (0.18, -2.65, 4.15), mats["bronze"], props, unwrap=False)

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
    obj.scale = (0.18, 0.012, 0.18)
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
        (3.48, 0.042, 4.05),
        (mx, south + 0.018, 9.35),
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
    make_box("LIGHT_Monolith_Reveal", (3.2, 0.02, 0.03), (mx, south - 0.04, 13.22), mats["led_warm"], lights)
    make_box("LIGHT_Monolith_Slit_L", (0.03, 0.02, 6.2), (mx - 1.98, south - 0.03, 6.7), mats["led_warm"], lights)
    make_box("LIGHT_Monolith_Slit_R", (0.03, 0.02, 6.2), (mx + 1.98, south - 0.03, 6.7), mats["led_warm"], lights)
    make_box("LIGHT_Monolith_Uplight", (1.5, 0.55, 0.05), (mx, south - 0.28, 0.38), mats["led_warm"], lights, unwrap=False)
    make_box("LIGHT_Monolith_Graze", (0.10, 0.62, 5.8), (mx - 1.95, south - 0.22, 7.0), mats["led_warm"], lights, unwrap=False)
    make_box("LIGHT_Monolith_NameWash", (2.85, 0.03, 0.03), (mx, south - 0.05, 12.62), mats["led_warm"], lights, unwrap=False)
    make_box(
        "PROP_Identity_LetterBed",
        (3.22, 0.010, 3.78),
        (mx, south + 0.032, 9.48),
        mats["metal_dark"],
        props,
        bevel=False,
        unwrap=False,
    )
    make_si_mark("PROP_Identity_Mark", (mx, south + 0.020, 13.08), mats["sign_cyan"], props)
    make_face_lettering(
        "PROP_Identity_Name_01",
        "SADEKUL",
        face_point=(mx, south, 12.22),
        normal=(0.0, -1.0, 0.0),
        size=cap_size(0.68),
        extrude=0.028,
        mat=mats["sign"],
        collection=props,
        offset=0.016,
        space=0.88,
        bevel_depth=0.0045,
        weight="bold",
    )
    make_face_lettering(
        "PROP_Identity_Name_02",
        "ISLAM",
        face_point=(mx, south, 11.38),
        normal=(0.0, -1.0, 0.0),
        size=cap_size(0.68),
        extrude=0.028,
        mat=mats["sign"],
        collection=props,
        offset=0.016,
        space=0.88,
        bevel_depth=0.0045,
        weight="bold",
    )
    make_box("PROP_Identity_Rule", (1.42, 0.008, 0.006), (mx, south + 0.014, 10.88), mats["sign_cyan"], props)
    make_face_lettering(
        "PROP_Identity_Title_01",
        "SOFTWARE ENGINEER",
        face_point=(mx, south, 10.48),
        normal=(0.0, -1.0, 0.0),
        size=cap_size(0.14),
        extrude=0.010,
        mat=mats["sign_zone"],
        collection=props,
        offset=0.014,
        space=1.02,
        bevel_depth=0.0012,
        weight="book",
    )
    make_face_lettering(
        "PROP_Identity_Title_02",
        "SYSTEMS ARCHITECT",
        face_point=(mx, south, 10.18),
        normal=(0.0, -1.0, 0.0),
        size=cap_size(0.14),
        extrude=0.010,
        mat=mats["sign_zone"],
        collection=props,
        offset=0.014,
        space=1.02,
        bevel_depth=0.0012,
        weight="book",
    )
    make_face_lettering(
        "PROP_Identity_Title_03",
        "DIGITAL RESIDENCE",
        face_point=(mx, south, 9.78),
        normal=(0.0, -1.0, 0.0),
        size=cap_size(0.08),
        extrude=0.005,
        mat=mats["sign_zone"],
        collection=props,
        offset=0.012,
        space=1.12,
        bevel_depth=0.0005,
        weight="book",
    )


def build_water(mats: dict[str, bpy.types.Material]) -> None:
    water = col("08_WATER")
    lights = col("10_LIGHTS")
    make_box("ENV_Waterfall_Basin_Upper", (5.2, 3.2, 0.50), (-18.4, -4.4, 5.60), mats["stone"], water, bevel=True, bevel_width=0.04)
    make_box("ENV_Waterfall_Channel", (2.05, 4.4, 0.32), (-18.4, -7.0, 5.40), mats["stone"], water, bevel=True)
    make_box("ENV_Waterfall_Lip", (4.6, 0.38, 0.22), (-18.4, -9.2, 5.45), mats["stone"], water, bevel=True)
    make_box("ENV_Waterfall_Wall", (6.4, 0.72, 6.55), (-18.4, -9.15, 0.0), mats["stone"], water, bevel=True, bevel_width=0.05)
    make_box("ENV_Waterfall_Retain", (8.0, 1.15, 2.4), (-18.4, -10.6, 0.0), mats["stone"], water, bevel=True)
    make_box("FX_Waterfall_Sheet", (5.2, 0.04, 5.8), (-14.4, -9.38, 0.28), mats["water"], water)
    make_box("FX_Waterfall_Sheet_B", (4.8, 0.03, 5.4), (-14.4, -9.48, 0.22), mats["water"], water)
    make_box("FX_Waterfall_Sheet_C", (4.2, 0.025, 4.9), (-14.4, -9.56, 0.18), mats["water"], water)
    make_box("ENV_Water_Basin", (8.6, 3.8, 0.50), (-14.4, -11.4, -0.08), mats["stone"], water, bevel=True)
    make_box("FX_Water_ReflectingPool", (18.5, 5.4, 0.05), (-6.2, -12.4, 0.28), mats["water"], water)
    make_box("ENV_Pool_Coping_S", (19.0, 0.28, 0.12), (-6.2, -15.1, 0.28), mats["bronze"], water)
    make_box("ENV_Pool_Coping_N", (19.0, 0.28, 0.12), (-6.2, -9.7, 0.28), mats["bronze"], water)
    make_box("LIGHT_Waterfall_Base", (5.4, 0.08, 0.05), (-14.4, -9.45, 0.32), mats["led_warm"], lights)
    make_box("LIGHT_Waterfall_Mid", (4.8, 0.04, 0.03), (-14.4, -9.42, 3.2), mats["led_warm"], lights)
    make_box("LIGHT_Pool_Edge", (17.8, 0.05, 0.03), (-6.2, -15.05, 0.34), mats["led_warm"], lights)
    foam_cards = [
        make_alpha_card("FX_Waterfall_Foam_A", (-14.4, -10.05, 0.55), (3.4, 1.15), 0.0, mats["foam"], water, pitch=12.0),
        make_alpha_card("FX_Waterfall_Foam_B", (-14.2, -11.15, 0.42), (2.8, 0.85), 0.35, mats["foam"], water, pitch=8.0),
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
        ("COL_Entrance_Steps", (7.2, 5.6, 2.05), (0.0, -10.5, 0.0)),
        ("COL_Entrance_Platform", (18.4, 8.6, 1.98), (0.0, -2.35, 0.0)),
        ("COL_Door", (8.4, 0.6, 5.4), (0.0, -2.55, 1.82)),
        ("COL_Boundary", (54.0, 0.9, 2.5), (0.0, -26.2, 0.08)),
        ("COL_Gate", (9.0, 1.5, 4.2), (0.0, -26.2, 0.08)),
        ("COL_Building_Base", (14.6, 12.8, 7.60), (0.0, 2.10, 1.80)),
        ("COL_Building_West", (15.4, 16.4, 9.40), (-16.55, 2.4, 1.80)),
        ("COL_Building_East", (13.4, 14.2, 7.60), (13.55, 2.55, 1.80)),
        ("COL_Water_Edge", (19.0, 6.0, 0.7), (-6.2, -12.4, -0.05)),
        ("COL_Identity_Monolith", (4.4, 1.4, 17.4), (-28.4, 1.70, 0.08)),
    ]
    for name, size, origin in proxies:
        obj = make_box(name, size, origin, mat, collision, bevel=False, unwrap=False)
        obj.hide_render = True
        obj.display_type = "WIRE"


def build_anchors() -> None:
    ui = col("12_UI_ANCHORS")
    make_empty("UI_Entrance_Trigger", (0.0, -11.2, 1.9), ui)
    make_empty("UI_Identity", (-28.4, 1.11, 9.8), ui)
    make_empty("UI_Identity_Monolith", (-28.4, 1.11, 9.8), ui)
    make_empty("UI_Owner_Name", (-28.4, 1.11, 9.9), ui)
    make_empty("UI_Residence_Sign", (0.0, -26.34, 3.22), ui)
    make_empty("UI_Engineering_Direction", (-16.55, -8.2, 2.4), ui)
    make_empty("UI_AI_Lab_Direction", (15.85, -0.8, 2.4), ui)
    make_empty("UI_Project_Direction", (13.55, -4.4, 2.2), ui)
    make_empty("UI_Command_Center_Direction", (3.55, 4.2, 10.2), ui)
    make_empty("UI_Building_Entry", (0.0, -3.6, 2.6), ui)
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
        ("CAM_Hero_ThreeQuarter", (17.2, -20.6, 8.35), (-3.8, 0.8, 5.4), 35),
        ("CAM_SYSTEM_HERO", (17.2, -20.6, 8.35), (-3.8, 0.8, 5.4), 35),
        ("CAM_Clay_Hero", (17.2, -20.6, 8.35), (-3.8, 0.8, 5.4), 35),
        ("CAM_Front", (0.2, -21.4, 5.8), (0.0, -1.2, 5.8), 35),
        ("CAM_Clay_Front", (0.2, -21.4, 5.8), (0.0, -1.2, 5.8), 35),
        ("CAM_LeftPerspective", (-18.8, -15.4, 6.4), (0.2, 0.8, 5.8), 35),
        ("CAM_RightPerspective", (20.6, -15.2, 6.6), (0.4, 1.0, 6.0), 35),
        ("CAM_IslandContext", (8.0, -38.0, 10.4), (0.0, -1.0, 4.8), 28),
        ("CAM_MaterialCloseup", (6.4, -10.2, 3.15), (-12.2, -5.4, 6.2), 50),
        ("CAM_GlassCloseup", (2.4, -8.6, 3.4), (0.0, -2.6, 5.2), 48),
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
        ("CAM_Entrance", (0.2, -16.8, 3.55), (0.0, -4.2, 4.6), 38),
        ("CAM_Clay_Entrance", (0.2, -16.8, 3.55), (0.0, -4.2, 4.6), 38),
        ("CAM_Identity_Monolith_Closeup", (-28.4, -6.6, 9.55), (-28.4, 1.11, 9.55), 38),
        ("CAM_Vegetation_Closeup", (-12.05, -21.35, 1.72), (-12.2, -19.8, 2.55), 35),
        ("CAM_Gate", (0.2, -36.5, 1.85), (0.0, -26.0, 2.85), 36),
        ("CAM_Water_Feature", (-11.6, -13.4, 2.35), (-11.6, -8.55, 1.9), 38),
        ("CAM_Material_Detail", (5.2, -9.4, 2.4), (0.6, -3.2, 4.2), 50),
        ("CAM_Night_Wide", (8.0, -58.0, 8.4), (0.5, -8.0, 7.2), 28),
        ("CAM_Elevated", (14.5, -18.5, 16.8), (0.8, 1.2, 6.8), 32),
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

    moon = add_light("LIGHT_QA_Moon", "SUN", (-16.0, -14.0, 30.0), 1.65, (0.78, 0.80, 0.82))
    moon.rotation_euler = (math.radians(48), math.radians(-12), math.radians(18))
    add_light("LIGHT_QA_Fill", "AREA", (2.0, -32.0, 10.0), 1100.0, (0.78, 0.80, 0.84), 28.0)
    add_light("LIGHT_QA_Entrance", "AREA", (0.0, -7.4, 5.4), 900.0, (1.0, 0.82, 0.62), 10.0)
    add_light("LIGHT_QA_Interior", "AREA", (0.0, 1.8, 4.2), 720.0, (1.0, 0.78, 0.52), 8.0)
    add_light("LIGHT_QA_East", "AREA", (22.0, -5.0, 8.5), 420.0, (0.92, 0.88, 0.82), 9.0)
    add_light("LIGHT_QA_L2", "AREA", (5.0, -4.0, 9.2), 480.0, (1.0, 0.80, 0.58), 10.0)
    add_light("LIGHT_QA_Rim", "AREA", (-20.0, 12.0, 14.0), 380.0, (0.72, 0.76, 0.82), 12.0)
    add_light("LIGHT_QA_Monolith", "AREA", (-28.4, -4.6, 9.6), 520.0, (0.95, 0.88, 0.75), 6.0)
    add_light("LIGHT_QA_Tree", "AREA", (-12.2, -18.6, 1.4), 280.0, (0.90, 0.88, 0.82), 4.0)
    add_light("LIGHT_QA_Water", "AREA", (-11.6, -12.4, 1.1), 240.0, (0.88, 0.86, 0.80), 5.0)
    add_light("LIGHT_QA_Facade", "AREA", (0.0, -22.0, 8.0), 560.0, (0.80, 0.82, 0.86), 22.0)


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


def hide_context_for_arch_qa(hide: bool) -> None:
    prefixes = (
        "PROP_Tree",
        "PROP_Palm",
        "PROP_Shrub",
        "PROP_Hedge",
        "PROP_Ornamental",
        "Island_",
        "FX_",
        "Site_Ground",
    )
    for obj in bpy.data.objects:
        if obj.name.startswith(prefixes):
            obj.hide_render = hide


def apply_clay(clay: bpy.types.Material) -> dict[str, list[bpy.types.Material]]:
    backup: dict[str, list[bpy.types.Material]] = {}
    skip = ("COL_", "CAM_", "LIGHT_QA")
    skip_mesh = (
        "PROP_Tree",
        "PROP_Palm",
        "PROP_Shrub",
        "PROP_Hedge",
        "PROP_Ornamental",
        "Island_",
        "FX_",
        "Site_",
    )
    for obj in bpy.data.objects:
        if obj.type != "MESH" or not obj.data.materials:
            continue
        if obj.name.startswith(skip) or obj.name.startswith(skip_mesh):
            continue
        backup[obj.name] = list(obj.data.materials)
        obj.data.materials.clear()
        obj.data.materials.append(clay)
    return backup


def restore_materials(backup: dict[str, list[bpy.types.Material]]) -> None:
    for name, materials_list in backup.items():
        obj = bpy.data.objects.get(name)
        if obj is None or obj.type != "MESH":
            continue
        obj.data.materials.clear()
        for mat in materials_list:
            if mat is not None:
                obj.data.materials.append(mat)


def render_camera_set(names: set[str]) -> list[str]:
    scene = bpy.context.scene
    rendered: list[str] = []
    cameras = [obj for obj in bpy.data.objects if obj.type == "CAMERA" and obj.name in names]
    for cam in cameras:
        scene.camera = cam
        out = RENDER_DIR / f"{cam.name}.png"
        scene.render.filepath = str(out)
        bpy.ops.render.render(write_still=True)
        rendered.append(str(out))
    return rendered


def render_qa(mats: dict[str, bpy.types.Material]) -> list[str]:
    if os.environ.get("SKIP_QA_RENDER") == "1":
        return []
    scene = bpy.context.scene
    configure_eevee(scene)
    scene.render.image_settings.file_format = "PNG"
    hide_context_for_arch_qa(True)
    backup = apply_clay(mats["clay"])
    rendered = render_camera_set({"CAM_Clay_Hero", "CAM_Clay_Front", "CAM_Clay_Entrance"})
    restore_materials(backup)
    beauty = {
        "CAM_Hero_ThreeQuarter",
        "CAM_Front",
        "CAM_Entrance",
        "CAM_MaterialCloseup",
        "CAM_GlassCloseup",
    }
    if os.environ.get("FULL_QA") == "1":
        beauty.update(
            {
                "CAM_LeftPerspective",
                "CAM_RightPerspective",
                "CAM_Elevated",
                "CAM_IslandContext",
            }
        )
    rendered.extend(render_camera_set(beauty))
    hide_context_for_arch_qa(False)
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
    rendered = render_qa(mats)
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
