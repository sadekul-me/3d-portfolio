"""Replace fragmented scan-wood with one skinned trunk/branch mesh. Keep original leaves."""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from optimize_jacaranda import fetch_source

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "assets-source" / "vegetation" / "polyhaven" / "jacaranda_tree"
PUBLIC = REPO / "public" / "assets" / "world" / "vegetation"
RENDER = REPO / "assets-source" / "blender" / "digital-residence" / "renders"
SNAP = SRC / "_jacaranda_wood_repaired.blend"


def classify_parts(parts: list):
    labeled = []
    for obj in parts:
        names = " ".join(m.name.lower() for m in obj.data.materials if m)
        labeled.append((obj, names, len(obj.data.vertices)))
        print("PART", obj.name, "mats", names or "<none>", "verts", len(obj.data.vertices))
    leaves = [obj for obj, names, _n in labeled if "leaf" in names]
    wood = [obj for obj, names, _n in labeled if "leaf" not in names]
    if not leaves:
        ordered = sorted(parts, key=lambda o: -len(o.data.vertices))
        leaves = [ordered[0]]
        wood = ordered[1:]
    return wood, leaves


def build_skin_armature(bpy, bmesh, height: float = 7.7, targets: list | None = None):
    from mathutils import Vector

    rng = random.Random(17)
    bm = bmesh.new()
    radius_of = {}

    def vert(co, radius: float):
        v = bm.verts.new((co[0], co[1], co[2]) if not hasattr(co, "x") else co)
        radius_of[v] = radius
        return v

    trunk = []
    trunk_n = 12
    for i in range(trunk_n):
        t = i / (trunk_n - 1)
        radius = 0.34 * (1.0 - 0.62 * t) + 0.05
        co = (
            0.16 * t * math.sin(t * 2.05 + 0.35),
            0.11 * t * math.cos(t * 1.55),
            t * height,
        )
        v = vert(co, radius)
        if trunk:
            bm.edges.new((trunk[-1], v))
        trunk.append(v)

    def branch(start, direction, length: float, r0: float, segments: int, droop: float):
        chain = [start]
        direction = Vector(direction).normalized()
        for s in range(1, segments + 1):
            u = s / segments
            side = Vector(
                (
                    0.05 * u * rng.uniform(-1.0, 1.0),
                    0.05 * u * rng.uniform(-1.0, 1.0),
                    -droop * u * u,
                )
            )
            co = start.co + direction * (length * u) + side
            # Keep the first step almost as thick as the parent so the skin welds.
            fade = 0.12 if s == 1 else (0.78 * u)
            radius = max(0.014, r0 * (1.0 - fade))
            v = vert(co, radius)
            bm.edges.new((chain[-1], v))
            chain.append(v)
        return chain

    def add_primary(origin, direction, length: float, r_scale: float = 0.82):
        r0 = radius_of[origin] * r_scale
        return branch(origin, direction, length, r0, 6, 0.18)

    primaries = []
    for b in range(10):
        attach = 3 + (b % 7)
        origin = trunk[attach]
        az = b * 2.15 + rng.uniform(-0.28, 0.28)
        elev = rng.uniform(0.18, 0.72)
        length = rng.uniform(1.7, 3.15) * (1.05 - attach / trunk_n * 0.4)
        direction = Vector(
            (
                math.cos(az) * math.cos(elev),
                math.sin(az) * math.cos(elev),
                math.sin(elev) * 0.85 + 0.12,
            )
        )
        primaries.append(add_primary(origin, direction, length))

    if targets:
        for i, target in enumerate(targets[:28]):
            goal = Vector(target)
            attach = min(range(4, trunk_n - 1), key=lambda idx: (trunk[idx].co - goal).length)
            origin = trunk[attach]
            delta = goal - origin.co
            if delta.length < 0.4:
                continue
            primaries.append(add_primary(origin, delta, delta.length * 0.88, 0.74))

    for chain in primaries:
        if len(chain) < 4:
            continue
        fork = chain[2]
        fork_r = radius_of[fork]
        az = rng.uniform(0, math.tau)
        elev = rng.uniform(-0.1, 0.55)
        direction = Vector((math.cos(az) * 0.9, math.sin(az) * 0.9, math.sin(elev)))
        branch(fork, direction, rng.uniform(0.85, 1.55), fork_r * 0.78, 4, 0.16)
        if rng.random() > 0.3:
            az2 = az + rng.uniform(0.8, 2.2)
            direction2 = Vector((math.cos(az2) * 0.9, math.sin(az2) * 0.9, math.sin(elev * 0.6)))
            branch(fork, direction2, rng.uniform(0.7, 1.25), fork_r * 0.7, 3, 0.14)

    bm.verts.ensure_lookup_table()
    mesh = bpy.data.meshes.new("TREE_Wood")
    bm.to_mesh(mesh)
    ordered_radii = [radius_of[v] for v in bm.verts]
    bm.free()
    obj = bpy.data.objects.new("TREE_Wood", mesh)
    bpy.context.scene.collection.objects.link(obj)
    skin = obj.modifiers.new(name="Skin", type="SKIN")
    skin.use_x_symmetry = False
    skin.use_y_symmetry = False
    if hasattr(skin, "branch_smoothing"):
        skin.branch_smoothing = 0.35
    data = obj.data.skin_vertices[0].data
    for i, radius in enumerate(ordered_radii):
        data[i].radius = (radius, radius)
        data[i].use_root = i == 0
    sub = obj.modifiers.new(name="Subdiv", type="SUBSURF")
    sub.levels = 2
    sub.render_levels = 2
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=skin.name)
    bpy.ops.object.modifier_apply(modifier=sub.name)
    smooth = obj.modifiers.new(name="WeldSmooth", type="SMOOTH")
    smooth.factor = 0.45
    smooth.iterations = 14
    bpy.ops.object.modifier_apply(modifier=smooth.name)
    return obj


def assign_bark(bpy, obj) -> None:
    tex_path = SRC / "textures" / "jacaranda_tree_trunk_diff_1k.jpg"
    mat = bpy.data.materials.new("Wood_Welded")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    tex = nodes.new("ShaderNodeTexImage")
    if tex_path.exists():
        tex.image = bpy.data.images.load(str(tex_path))
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.88
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.cylinder_project(correct_aspect=True, scale_to_bounds=True)
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    bpy.ops.object.shade_smooth()


def sample_leaf_targets(leaf_obj, count: int = 28) -> list:
    from mathutils import Vector

    n = len(leaf_obj.data.vertices)
    step = max(1, n // count)
    targets = []
    for i in range(0, n, step):
        co = leaf_obj.matrix_world @ leaf_obj.data.vertices[i].co
        if co.z > 1.8:
            targets.append(Vector(co))
        if len(targets) >= count:
            break
    print("leaf_targets", len(targets), flush=True)
    return targets


def prepare() -> None:
    import bmesh
    import bpy

    gltf_path = fetch_source()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(gltf_path))
    meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    root = bpy.data.objects.new("TREE_Jacaranda_Root", None)
    bpy.context.scene.collection.objects.link(root)
    for obj in meshes:
        obj.parent = root
    bpy.context.view_layer.update()
    zs = [(obj.matrix_world @ v.co).z for obj in meshes for v in obj.data.vertices]
    height = max(zs) - min(zs)
    if height > 0.01:
        root.scale = (8.6 / height,) * 3
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action="DESELECT")
    root.select_set(True)
    for obj in meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    min_z = min((obj.matrix_world @ v.co).z for obj in meshes for v in obj.data.vertices)
    root.location.z -= min_z
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

    src = meshes[0]
    bpy.ops.object.select_all(action="DESELECT")
    src.select_set(True)
    bpy.context.view_layer.objects.active = src
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.separate(type="MATERIAL")
    bpy.ops.object.mode_set(mode="OBJECT")
    parts = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    wood_parts, leaf_parts = classify_parts(parts)
    print("classified wood", [o.name for o in wood_parts], "leaves", [o.name for o in leaf_parts], flush=True)
    for obj in wood_parts:
        bpy.data.objects.remove(obj, do_unlink=True)
    for leaf in leaf_parts:
        leaf.name = "TREE_Leaves"
        leaf.parent = root
        leaf.data.calc_loop_triangles()
        print("leaf_tris", len(leaf.data.loop_triangles), flush=True)
    targets = sample_leaf_targets(leaf_parts[0]) if leaf_parts else []
    wood = build_skin_armature(bpy, bmesh, targets=targets)
    wood.parent = root
    assign_bark(bpy, wood)
    wood.data.calc_loop_triangles()
    print("wood_tris", len(wood.data.loop_triangles), "verts", len(wood.data.vertices), flush=True)
    SRC.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(SNAP))
    print("saved", SNAP, flush=True)


def rebuild_from_snap() -> None:
    import bmesh
    import bpy

    bpy.ops.wm.open_mainfile(filepath=str(SNAP))
    wood = bpy.data.objects.get("TREE_Wood")
    leaves = bpy.data.objects.get("TREE_Leaves")
    root = bpy.data.objects.get("TREE_Jacaranda_Root")
    if leaves is None:
        raise RuntimeError("snap missing TREE_Leaves")
    targets = sample_leaf_targets(leaves)
    if wood is not None:
        bpy.data.objects.remove(wood, do_unlink=True)
    wood = build_skin_armature(bpy, bmesh, targets=targets)
    if root is not None:
        wood.parent = root
    assign_bark(bpy, wood)
    wood.data.calc_loop_triangles()
    print("wood_tris", len(wood.data.loop_triangles), flush=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(SNAP))
    print("saved", SNAP, flush=True)


def export_lods() -> None:
    import bpy

    PUBLIC.mkdir(parents=True, exist_ok=True)

    def export_one(leaf_ratio: float, wood_ratio: float, name: str) -> None:
        bpy.ops.wm.open_mainfile(filepath=str(SNAP))
        wood = bpy.data.objects.get("TREE_Wood")
        leaves = [obj for obj in bpy.data.objects if obj.type == "MESH" and obj != wood]
        if wood is None:
            raise RuntimeError("missing TREE_Wood")
        pairs = [(wood, wood_ratio)] + [(leaf, leaf_ratio) for leaf in leaves]
        for obj, ratio in pairs:
            if ratio >= 0.999:
                continue
            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            mod = obj.modifiers.new(name="Decimate", type="DECIMATE")
            mod.decimate_type = "COLLAPSE"
            mod.ratio = ratio
            depsgraph = bpy.context.evaluated_depsgraph_get()
            mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(depsgraph))
            obj.modifiers.clear()
            old = obj.data
            obj.data = mesh
            if old.users == 0:
                bpy.data.meshes.remove(old)
        tris = 0
        exportables = [wood, *leaves]
        for obj in exportables:
            obj.data.calc_loop_triangles()
            tris += len(obj.data.loop_triangles)
            print(" ", obj.name, len(obj.data.loop_triangles), flush=True)
        bpy.ops.object.select_all(action="DESELECT")
        for obj in exportables:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = wood
        out = PUBLIC / name
        bpy.ops.export_scene.gltf(
            filepath=str(out),
            export_format="GLB",
            use_selection=True,
            export_apply=True,
            export_animations=False,
            export_lights=False,
            export_cameras=False,
            export_yup=True,
            export_image_format="JPEG",
            export_draco_mesh_compression_enable=True,
            export_draco_mesh_compression_level=6,
        )
        print("exported", name, "tris", tris, "bytes", out.stat().st_size, flush=True)

    export_one(0.045, 1.0, "tree-jacaranda-lod0.glb")
    export_one(0.018, 0.55, "tree-jacaranda-lod1.glb")
    export_one(0.007, 0.22, "tree-jacaranda-lod2.glb")


def look_at(obj, target) -> None:
    from mathutils import Vector

    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def render_structure_qa() -> None:
    import bpy

    shots = (
        ("TREE_TRUNK_FRONT.png", (0.0, -9.2, 3.4), (0.0, 0.0, 3.2), 32, True),
        ("TREE_TRUNK_LEFT_3Q.png", (-6.4, -7.2, 3.6), (0.0, 0.0, 3.1), 32, True),
        ("TREE_TRUNK_RIGHT_3Q.png", (6.4, -7.2, 3.6), (0.0, 0.0, 3.1), 32, True),
        ("TREE_TRUNK_CLOSEUP.png", (1.55, -3.2, 1.45), (0.0, 0.0, 1.25), 40, True),
        ("TREE_JUNCTION_CLOSEUP.png", (1.4, -2.6, 2.7), (0.1, 0.0, 2.45), 50, True),
        ("TREE_LOD0_CLOSEUP.png", (3.4, -7.2, 2.8), (0.0, 0.0, 3.4), 35, False),
    )
    glb = PUBLIC / "tree-jacaranda-lod0.glb"
    RENDER.mkdir(parents=True, exist_ok=True)
    for name, loc, target, lens, hide_leaves in shots:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(glb))
        if hide_leaves:
            for obj in bpy.data.objects:
                if obj.type != "MESH":
                    continue
                mats = [m.name.lower() for m in obj.data.materials if m]
                if "leaf" in obj.name.lower() or any("leaf" in m for m in mats):
                    obj.hide_render = True
                    obj.hide_viewport = True
        world = bpy.data.worlds.new("QA")
        bpy.context.scene.world = world
        world.use_nodes = True
        bg = world.node_tree.nodes.get("Background")
        if bg:
            bg.inputs[0].default_value = (0.55, 0.58, 0.6, 1.0)
            bg.inputs[1].default_value = 0.95
        sun_data = bpy.data.lights.new("QA_Sun", "SUN")
        sun_data.energy = 3.6
        sun = bpy.data.objects.new("QA_Sun", sun_data)
        sun.rotation_euler = (0.95, 0.18, 0.45)
        bpy.context.scene.collection.objects.link(sun)
        fill_data = bpy.data.lights.new("QA_Fill", "AREA")
        fill_data.energy = 280.0
        fill_data.size = 7.0
        fill = bpy.data.objects.new("QA_Fill", fill_data)
        fill.location = (-2.5, -4.2, 3.8)
        bpy.context.scene.collection.objects.link(fill)
        cam_data = bpy.data.cameras.new(name)
        cam_data.lens = lens
        cam = bpy.data.objects.new(name, cam_data)
        cam.location = loc
        look_at(cam, target)
        bpy.context.scene.collection.objects.link(cam)
        scene = bpy.context.scene
        scene.camera = cam
        try:
            scene.render.engine = "BLENDER_EEVEE_NEXT"
        except TypeError:
            scene.render.engine = "BLENDER_EEVEE"
        scene.render.resolution_x = 1600
        scene.render.resolution_y = 1000
        scene.render.filepath = str(RENDER / name)
        scene.render.image_settings.file_format = "PNG"
        bpy.ops.render.render(write_still=True)
        print("wrote", RENDER / name, flush=True)


if __name__ == "__main__":
    if "--from-snap" in sys.argv:
        rebuild_from_snap()
    else:
        prepare()
    export_lods()
    render_structure_qa()
