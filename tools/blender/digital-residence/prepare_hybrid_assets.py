"""Prepare generated hybrid textures: alpha cleanup, resize, copy into source and public."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[3]
CURSOR_ASSETS = Path(r"C:\Users\Li Ao\.cursor\projects\d-3d-portfolio\assets")
GEN_DIR = Path(__file__).resolve().parent / "textures" / "generated"
PUBLIC_VEG = REPO / "public" / "assets" / "world" / "vegetation"
PUBLIC_WATER = REPO / "public" / "assets" / "world" / "water"
PUBLIC_ROCKS = REPO / "public" / "assets" / "world" / "rocks"
SOURCE_VEG = REPO / "assets-source" / "vegetation" / "generated"
SOURCE_WATER = REPO / "assets-source" / "water"
SOURCE_ROCKS = REPO / "assets-source" / "rocks"
LICENSE_DIR = REPO / "assets-source" / "licenses"
MANIFEST = REPO / "assets-source" / "hybrid-asset-manifest.json"


def smoothstep(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def knock_light_checker(im: Image.Image) -> Image.Image:
    rgb = im.convert("RGB")
    out = Image.new("RGBA", rgb.size)
    src = rgb.load()
    dst = out.load()
    w, h = rgb.size
    for y in range(h):
        for x in range(w):
            r, g, b = src[x, y]
            mx = max(r, g, b)
            mn = min(r, g, b)
            sat = (mx - mn) / max(mx, 1)
            lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
            if lum > 228 and sat < 0.07:
                a = 0
            elif lum > 198 and sat < 0.10:
                a = int(255 * (1.0 - smoothstep((lum - 198) / 40.0)))
            else:
                a = 255
            if a < 16:
                dst[x, y] = (r, g, b, 0)
            else:
                dst[x, y] = (r, g, b, a)
    return defringe(out)


def foam_alpha(im: Image.Image) -> Image.Image:
    rgb = im.convert("RGB")
    out = Image.new("RGBA", rgb.size)
    src = rgb.load()
    dst = out.load()
    w, h = rgb.size
    for y in range(h):
        for x in range(w):
            r, g, b = src[x, y]
            lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
            a = int(255 * smoothstep((lum - 118.0) / 70.0))
            dst[x, y] = (255, 255, 255, a)
    return out


def defringe(im: Image.Image) -> Image.Image:
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0 or a > 240:
                continue
            t = a / 255.0
            px[x, y] = (
                int(r * t + 20 * (1 - t)),
                int(g * t + 28 * (1 - t)),
                int(b * t + 12 * (1 - t)),
                a,
            )
    return im


def save(im: Image.Image, dests: list[Path], size: tuple[int, int] | None = None) -> None:
    if size:
        im = im.resize(size, Image.Resampling.LANCZOS)
    for dest in dests:
        dest.parent.mkdir(parents=True, exist_ok=True)
        im.save(dest, "PNG", optimize=True)


def main() -> None:
    jobs = [
        (
            "foliage-cluster-side-a.png",
            knock_light_checker,
            (1024, 1024),
            [GEN_DIR, PUBLIC_VEG, SOURCE_VEG / "hero"],
        ),
        (
            "foliage-cluster-side-b.png",
            knock_light_checker,
            (1024, 1024),
            [GEN_DIR, PUBLIC_VEG, SOURCE_VEG / "hero"],
        ),
        (
            "foliage-cluster-palm.png",
            knock_light_checker,
            (1024, 1024),
            [GEN_DIR, PUBLIC_VEG, SOURCE_VEG / "mid"],
        ),
        (
            "foliage-cluster-broadleaf.png",
            knock_light_checker,
            (768, 768),
            [GEN_DIR, PUBLIC_VEG, SOURCE_VEG / "mid"],
        ),
        (
            "tree-palm-distant.png",
            knock_light_checker,
            (768, 1152),
            [GEN_DIR, PUBLIC_VEG, SOURCE_VEG / "distant"],
        ),
        (
            "water-foam-shore.png",
            foam_alpha,
            (1024, 682),
            [GEN_DIR, PUBLIC_WATER, SOURCE_WATER],
        ),
    ]
    records = []
    for name, processor, size, dest_roots in jobs:
        src = CURSOR_ASSETS / name
        if not src.exists():
            raise SystemExit(f"missing source {src}")
        processed = processor(Image.open(src))
        dests = [root / name for root in dest_roots]
        save(processed, dests, size)
        records.append(
            {
                "id": Path(name).stem,
                "type": "png-alpha" if processor is not foam_alpha or True else "png",
                "source": "locally generated image asset",
                "license": "project-original / generated for Digital Residence",
                "purpose": name,
                "resolution": list(size),
                "alpha": True,
                "LOD": dest_roots[2].name if len(dest_roots) > 2 else "shared",
                "public": True,
                "originalFilename": name,
                "localDestination": str(dests[1].relative_to(REPO)).replace("\\", "/"),
            }
        )

    rock_src = CURSOR_ASSETS / "rock-basalt-albedo.png"
    rock = Image.open(rock_src).convert("RGB").resize((1024, 1024), Image.Resampling.LANCZOS)
    rock_dests = [
        GEN_DIR / "rock-basalt-albedo.png",
        PUBLIC_ROCKS / "rock-basalt-albedo.png",
        SOURCE_ROCKS / "rock-basalt-albedo.png",
    ]
    save(rock, rock_dests)
    records.append(
        {
            "id": "rock-basalt-albedo",
            "type": "pbr-albedo",
            "source": "locally generated image asset",
            "license": "project-original / generated for Digital Residence",
            "purpose": "island cliff / shoreline rock albedo",
            "resolution": [1024, 1024],
            "alpha": False,
            "LOD": "hero",
            "public": True,
            "originalFilename": "rock-basalt-albedo.png",
            "localDestination": "public/assets/world/rocks/rock-basalt-albedo.png",
        }
    )

    LICENSE_DIR.mkdir(parents=True, exist_ok=True)
    (LICENSE_DIR / "GENERATED_HYBRID_ASSETS.md").write_text(
        "\n".join(
            [
                "# Hybrid visual assets",
                "",
                "These textures were generated locally for Digital Residence production.",
                "They are original project assets, not scraped from Google Images.",
                "",
                "Author: Digital Residence production (generated image assets)",
                "License: project-original, commercial use within this portfolio",
                "Sources: foliage-cluster-*.png, tree-palm-distant.png, water-foam-shore.png, rock-basalt-albedo.png",
                "",
                "No Poly Haven / ambientCG downloads were required for this pass.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    MANIFEST.write_text(json.dumps(records, indent=2), encoding="utf-8")
    shutil.copy2(MANIFEST, GEN_DIR / "hybrid-asset-manifest.json")
    print("prepared", len(records), "assets")


if __name__ == "__main__":
    main()
