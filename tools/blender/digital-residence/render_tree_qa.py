"""Solo QA renders for jacaranda LODs (neutral daylight, no scene lighting tricks)."""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
VEG = REPO / "public" / "assets" / "world" / "vegetation"
OUT = REPO / "assets-source" / "blender" / "digital-residence" / "renders"
SHOTS = (
    ("tree-jacaranda-lod0.glb", "TREE_LOD0_CLOSEUP.png", (3.4, -7.2, 2.8), (0.0, 0.0, 3.4), 35),
    ("tree-jacaranda-lod1.glb", "TREE_LOD1_CLOSEUP.png", (4.2, -8.4, 3.1), (0.0, 0.0, 3.2), 32),
    ("tree-jacaranda-lod2.glb", "TREE_LOD2_DISTANCE.png", (11.0, -22.0, 6.5), (0.0, 0.0, 3.8), 28),
)


def configure_world(bpy) -> None:
    world = bpy.data.worlds.new("QA_Daylight")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.62, 0.7, 0.78, 1.0)
        bg.inputs[1].default_value = 1.15


def add_sun(bpy) -> None:
    data = bpy.data.lights.new("QA_Sun", "SUN")
    data.energy = 3.2
    data.color = (1.0, 0.96, 0.9)
    data.angle = 0.12
    sun = bpy.data.objects.new("QA_Sun", data)
    sun.rotation_euler = (0.85, 0.15, 0.4)
    bpy.context.scene.collection.objects.link(sun)


def look_at(obj, target) -> None:
    import math
    from mathutils import Vector

    direction = Vector(target) - obj.location
    rot_quat = direction.to_track_quat("-Z", "Y")
    obj.rotation_euler = rot_quat.to_euler()


def render_one(bpy, glb: Path, name: str, loc, target, lens: float) -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(glb))
    configure_world(bpy)
    add_sun(bpy)
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = lens
    cam = bpy.data.objects.new(name, cam_data)
    cam.location = loc
    look_at(cam, target)
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    scene = bpy.context.scene
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except TypeError:
        scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1000
    scene.render.filepath = str(OUT / name)
    scene.render.image_settings.file_format = "PNG"
    OUT.mkdir(parents=True, exist_ok=True)
    bpy.ops.render.render(write_still=True)
    print("wrote", OUT / name)


def main() -> None:
    import bpy

    for file, name, loc, target, lens in SHOTS:
        path = VEG / file
        if not path.exists():
            raise FileNotFoundError(path)
        render_one(bpy, path, name, loc, target, lens)


if __name__ == "__main__":
    main()
