"""Download and inspect Poly Haven landscape trees. Reject scan-shard / spaghetti wood."""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "assets-source" / "vegetation" / "polyhaven"
RENDER = REPO / "assets-source" / "blender" / "digital-residence" / "renders"
UA = "DigitalResidenceAssetPipeline/1.0"

CANDIDATES = (
    "tree_small_02",
    "searsia_burchellii",
    "island_tree_02",
)


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 1024:
        print("skip", dest, dest.stat().st_size, flush=True)
        return
    print("get", url, flush=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=600) as resp:
        dest.write_bytes(resp.read())
    print("wrote", dest, dest.stat().st_size, flush=True)


def fetch_gltf(asset_id: str) -> Path:
    data = fetch_json(f"https://api.polyhaven.com/files/{asset_id}")
    gltf = data["gltf"]["1k"]["gltf"]
    folder = SRC / asset_id
    dest = folder / f"{asset_id}_1k.gltf"
    download(gltf["url"], dest)
    for rel, info in (gltf.get("include") or {}).items():
        download(info["url"], folder / rel.replace("\\", "/"))
    return dest


def island_count(mesh) -> int:
    import bmesh

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    seen: set[int] = set()
    count = 0
    for start in bm.verts:
        if start.index in seen:
            continue
        count += 1
        stack = [start]
        seen.add(start.index)
        while stack:
            v = stack.pop()
            for e in v.link_edges:
                o = e.other_vert(v)
                if o.index not in seen:
                    seen.add(o.index)
                    stack.append(o)
    bm.free()
    return count


def classify(name: str) -> str:
    n = name.lower()
    if any(k in n for k in ("leaf", "leaves", "twig", "needle", "foliage")):
        return "leaf"
    if "branch" in n:
        return "branch"
    if any(k in n for k in ("trunk", "bark", "wood")):
        return "trunk"
    return "other"


def inspect_asset(asset_id: str, gltf_path: Path) -> dict:
    import bpy
    from mathutils import Vector

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(gltf_path))
    meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    for obj in list(meshes):
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        if len(obj.data.materials) > 1:
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.separate(type="MATERIAL")
            bpy.ops.object.mode_set(mode="OBJECT")
    meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    report: dict = {"id": asset_id, "objects": [], "world_size": None, "verdict": "unknown"}
    xs, ys, zs = [], [], []
    wood_islands = 0
    wood_tris = 0
    leaf_tris = 0
    for obj in meshes:
        obj.data.calc_loop_triangles()
        tris = len(obj.data.loop_triangles)
        mats = [m.name if m else "?" for m in obj.data.materials]
        kind = classify(" ".join(mats + [obj.name]))
        islands = island_count(obj.data) if kind != "leaf" else -1
        if kind == "leaf":
            leaf_tris += tris
        else:
            wood_tris += tris
            wood_islands += max(islands, 0)
        report["objects"].append(
            {
                "name": obj.name,
                "verts": len(obj.data.vertices),
                "tris": tris,
                "materials": mats,
                "kind": kind,
                "islands": islands,
            }
        )
        for v in obj.data.vertices:
            w = obj.matrix_world @ v.co
            xs.append(w.x)
            ys.append(w.y)
            zs.append(w.z)
    if xs:
        size = (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
        report["world_size"] = size
        report["height"] = max(size)
    report["wood_tris"] = wood_tris
    report["leaf_tris"] = leaf_tris
    report["wood_islands"] = wood_islands
    # Connected wood (one organism) should be a handful of islands, not thousands of shards.
    if wood_islands > 400:
        report["verdict"] = "REJECT_SCAN_SHARDS"
    elif wood_islands > 80:
        report["verdict"] = "RISKY_MANY_ISLANDS"
    else:
        report["verdict"] = "KEEP_INSPECT_RENDERS"
    print("INSPECT", json.dumps(report, indent=2), flush=True)
    render_inspect(asset_id, Vector((min(xs), min(ys), min(zs))), Vector((max(xs), max(ys), max(zs))))
    return report


def render_inspect(asset_id: str, mn, mx) -> None:
    import bpy
    from mathutils import Vector

    RENDER.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except TypeError:
        pass
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 1280
    scene.render.image_settings.file_format = "PNG"
    scene.world = bpy.data.worlds.new("QA_World")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.62, 0.64, 0.66, 1.0)
    bg.inputs[1].default_value = 1.0
    center = (mn + mx) * 0.5
    size = mx - mn
    radius = max(size.x, size.y, size.z) * 1.35
    cam_data = bpy.data.cameras.new("CAM_INSPECT")
    cam_data.lens = 50
    cam = bpy.data.objects.new("CAM_INSPECT", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    scene.camera = cam
    sun = bpy.data.lights.new("QA_Sun", "SUN")
    sun.energy = 4.0
    sun.angle = 0.2
    sun_obj = bpy.data.objects.new("QA_Sun", sun)
    sun_obj.rotation_euler = (0.7, 0.15, 0.9)
    bpy.context.scene.collection.objects.link(sun_obj)
    fill = bpy.data.lights.new("QA_Fill", "AREA")
    fill.energy = 180
    fill.size = 8
    fill_obj = bpy.data.objects.new("QA_Fill", fill)
    fill_obj.location = (center.x - radius, center.y - radius * 0.4, center.z + radius)
    bpy.context.scene.collection.objects.link(fill_obj)

    aliases = {
        "FRONT": "TREE_FRONT_CLOSEUP",
        "SIDE": "TREE_SIDE_CLOSEUP",
        "BACK": "TREE_BACK_CLOSEUP",
        "TRUNK": "TREE_TRUNK_JUNCTION_CLOSEUP",
    }
    views = {
        "FRONT": Vector((center.x, center.y - radius, center.z + size.z * 0.15)),
        "SIDE": Vector((center.x + radius, center.y, center.z + size.z * 0.15)),
        "BACK": Vector((center.x, center.y + radius, center.z + size.z * 0.15)),
        "TRUNK": Vector((center.x + size.x * 0.35, center.y - size.y * 0.55, mn.z + size.z * 0.28)),
    }
    for name, loc in views.items():
        cam.location = loc
        direction = center - loc
        if name == "TRUNK":
            direction = Vector((center.x, center.y, mn.z + size.z * 0.22)) - loc
        rot = direction.to_track_quat("-Z", "Y")
        cam.rotation_euler = rot.to_euler()
        out = RENDER / f"CANDIDATE_{asset_id}_{name}.png"
        scene.render.filepath = str(out)
        bpy.ops.render.render(write_still=True)
        alias = RENDER / f"{aliases[name]}.png"
        alias.write_bytes(out.read_bytes())
        print("RENDERED", out, "->", alias, flush=True)


def main() -> None:
    wanted = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else list(CANDIDATES)
    if not wanted:
        wanted = list(CANDIDATES)
    reports = []
    for asset_id in wanted:
        path = fetch_gltf(asset_id)
        reports.append(inspect_asset(asset_id, path))
    print("SUMMARY", json.dumps([{k: r[k] for k in ("id", "verdict", "wood_islands", "wood_tris", "leaf_tris", "height")} for r in reports], indent=2), flush=True)


if __name__ == "__main__":
    main()
