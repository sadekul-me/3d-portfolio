"""Inspect jacaranda wood topology: materials, islands, trunk-branch gaps."""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "assets-source" / "vegetation" / "polyhaven" / "jacaranda_tree"
GLTF = SRC / "jacaranda_tree_1k.gltf"


def island_count(mesh) -> int:
    import bmesh

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    seen = set()
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


def main() -> None:
    import bpy
    from mathutils import Vector, kdtree

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(GLTF))
    meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    print("OBJECTS", [(obj.name, len(obj.data.vertices), len(obj.data.materials), [m.name for m in obj.data.materials if m]) for obj in meshes])

    for obj in meshes:
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.separate(type="MATERIAL")
        bpy.ops.object.mode_set(mode="OBJECT")

    parts = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    print("AFTER_SEPARATE")
    for obj in parts:
        obj.data.calc_loop_triangles()
        mat = obj.data.materials[0].name if obj.data.materials and obj.data.materials[0] else "?"
        islands = -1
        if "leaf" not in mat.lower():
            islands = island_count(obj.data)
        print(
            "PART",
            obj.name,
            "mat",
            mat,
            "verts",
            len(obj.data.vertices),
            "tris",
            len(obj.data.loop_triangles),
            "islands",
            islands,
        )

    def by_mat(token: str):
        token = token.lower()
        return [obj for obj in parts if obj.data.materials and token in (obj.data.materials[0].name or "").lower()]

    trunks = by_mat("trunk") or by_mat("bark")
    branches = by_mat("branch")
    leaves = by_mat("leaf")
    print("GROUPS", "trunk", [o.name for o in trunks], "branch", [o.name for o in branches], "leaf", [o.name for o in leaves])

    if trunks and branches:
        trunk = trunks[0]
        tree = kdtree.KDTree(len(trunk.data.vertices))
        for i, v in enumerate(trunk.data.vertices):
            tree.insert(trunk.matrix_world @ v.co, i)
        tree.balance()
        gaps = []
        for obj in branches:
            best = None
            for v in obj.data.vertices:
                w = obj.matrix_world @ v.co
                co, _idx, dist = tree.find(w)
                if best is None or dist < best[2]:
                    best = (w, co, dist)
            if best:
                gaps.append((obj.name, best[2], tuple(best[0]), tuple(best[1])))
        gaps.sort(key=lambda g: -g[1])
        print("BRANCH_TO_TRUNK_MIN_GAP_COUNT", len(gaps))
        for row in gaps[:12]:
            print("GAP", round(row[1], 4), row[0])
        print("GAP_MAX", round(gaps[0][1], 4) if gaps else 0)
        print("GAP_MEDIAN", round(gaps[len(gaps) // 2][1], 4) if gaps else 0)


if __name__ == "__main__":
    main()
