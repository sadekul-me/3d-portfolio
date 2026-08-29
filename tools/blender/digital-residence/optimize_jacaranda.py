"""Download Poly Haven jacaranda (CC0) and optimize LODs for WebGL."""
from __future__ import annotations

import json
import math
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "assets-source" / "vegetation" / "polyhaven" / "jacaranda_tree"
PUBLIC = REPO / "public" / "assets" / "world" / "vegetation"
LICENSE = REPO / "assets-source" / "licenses" / "POLYHAVEN.md"
API = "https://api.polyhaven.com/files/jacaranda_tree"


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 1024:
        print("skip", dest.name, dest.stat().st_size)
        return
    print("get", url)
    req = urllib.request.Request(url, headers={"User-Agent": "DigitalResidenceAssetPipeline/1.0"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        dest.write_bytes(resp.read())
    print("wrote", dest, dest.stat().st_size)


def fetch_source() -> Path:
    req = urllib.request.Request(API, headers={"User-Agent": "DigitalResidenceAssetPipeline/1.0"})
    data = json.loads(urllib.request.urlopen(req, timeout=60).read().decode("utf-8"))
    gltf = data["gltf"]["1k"]["gltf"]
    download(gltf["url"], SRC / "jacaranda_tree_1k.gltf")
    for rel, info in (gltf.get("include") or {}).items():
        download(info["url"], SRC / rel.replace("\\", "/"))
    LICENSE.parent.mkdir(parents=True, exist_ok=True)
    LICENSE.write_text(
        "\n".join(
            [
                "# Poly Haven — Jacaranda Tree",
                "",
                "Source: https://polyhaven.com/a/jacaranda_tree",
                "Authors: Poly Haven / contributing artists listed on the asset page",
                "License: CC0 1.0 (public domain equivalent, commercial use allowed)",
                "Original files: assets-source/vegetation/polyhaven/jacaranda_tree/",
                "Web LODs: public/assets/world/vegetation/tree-jacaranda-lod*.glb",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return SRC / "jacaranda_tree_1k.gltf"


def optimize() -> None:
    import bpy

    gltf_path = fetch_source()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(gltf_path))
    meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    if not meshes:
        raise RuntimeError("no meshes imported")
    root = bpy.data.objects.new("TREE_Jacaranda_Root", None)
    bpy.context.scene.collection.objects.link(root)
    for obj in meshes:
        obj.parent = root
    # Measure combined bounds after parenting.
    bpy.context.view_layer.update()
    xs, ys, zs = [], [], []
    for obj in meshes:
        for v in obj.data.vertices:
            w = obj.matrix_world @ v.co
            xs.append(w.x)
            ys.append(w.y)
            zs.append(w.z)
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

    PUBLIC.mkdir(parents=True, exist_ok=True)
    SRC.mkdir(parents=True, exist_ok=True)
    snap = SRC / "_jacaranda_prepared.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(snap))
    print("saved snapshot", snap)

    def export_lod(ratio: float, name: str) -> None:
        bpy.ops.wm.open_mainfile(filepath=str(snap))
        meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
        if not meshes:
            raise RuntimeError("snapshot has no meshes")
        before = 0
        for obj in meshes:
            obj.data.calc_loop_triangles()
            before += len(obj.data.loop_triangles)
        for obj in meshes:
            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode="OBJECT")
            mod = obj.modifiers.new(name="Decimate", type="DECIMATE")
            mod.decimate_type = "COLLAPSE"
            mod.ratio = ratio
            depsgraph = bpy.context.evaluated_depsgraph_get()
            evaluated = obj.evaluated_get(depsgraph)
            collapsed = bpy.data.meshes.new_from_object(evaluated)
            obj.modifiers.clear()
            old = obj.data
            obj.data = collapsed
            if old.users == 0:
                bpy.data.meshes.remove(old)
        tris = 0
        for obj in meshes:
            obj.data.calc_loop_triangles()
            tris += len(obj.data.loop_triangles)
        print(name, "before", before, "after", tris, "ratio", round(tris / max(before, 1), 4))
        if tris >= before * 0.9:
            raise RuntimeError(f"decimate failed for {name}: {before} -> {tris}")
        bpy.ops.object.select_all(action="DESELECT")
        for obj in meshes:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = meshes[0]
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
        print("exported", name, "tris", tris, "bytes", out.stat().st_size)

    print("source objects", [obj.name for obj in meshes])
    export_lod(0.028, "tree-jacaranda-lod0.glb")
    export_lod(0.012, "tree-jacaranda-lod1.glb")
    export_lod(0.004, "tree-jacaranda-lod2.glb")


if __name__ == "__main__":
    if "--download-only" in sys.argv:
        fetch_source()
    else:
        optimize()
