"""Clean recovery-pass vegetation PNGs: aggressive light-bg knockout, no halo."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[3]
CURSOR = Path(r"C:\Users\Li Ao\.cursor\projects\d-3d-portfolio\assets")
PUBLIC_VEG = REPO / "public" / "assets" / "world" / "vegetation"
SOURCE = REPO / "assets-source" / "vegetation" / "generated" / "hero"


def smoothstep(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def knockout(im: Image.Image) -> Image.Image:
    rgb = im.convert("RGB")
    w, h = rgb.size
    src = rgb.load()
    out = Image.new("RGBA", (w, h))
    dst = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b = src[x, y]
            mx = max(r, g, b)
            mn = min(r, g, b)
            sat = (mx - mn) / max(mx, 1)
            lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
            green = g - max(r, b)
            if lum > 236 or (lum > 168 and sat < 0.11 and green < 12):
                a = 0
            elif lum > 150 and sat < 0.16 and green < 18:
                a = int(255 * (1.0 - smoothstep((lum - 150) / 70.0)))
            else:
                a = 255
            if a < 18:
                dst[x, y] = (r, g, b, 0)
            else:
                t = a / 255.0
                dst[x, y] = (int(r * t + 18 * (1 - t)), int(g * t + 28 * (1 - t)), int(b * t + 10 * (1 - t)), a)
    return out


def main() -> None:
    jobs = [
        ("veg-cluster-hero-a.png", "foliage-hero-a.png", (1024, 1024)),
        ("veg-cluster-hero-b.png", "foliage-hero-b.png", (1024, 1024)),
        ("veg-palm-frond.png", "foliage-palm-frond.png", (1024, 1024)),
        ("veg-shrub-tuft.png", "foliage-shrub.png", (768, 768)),
    ]
    PUBLIC_VEG.mkdir(parents=True, exist_ok=True)
    SOURCE.mkdir(parents=True, exist_ok=True)
    for src_name, dest_name, size in jobs:
        src = CURSOR / src_name
        processed = knockout(Image.open(src)).resize(size, Image.Resampling.LANCZOS)
        processed.save(PUBLIC_VEG / dest_name, "PNG", optimize=True)
        processed.save(SOURCE / dest_name, "PNG", optimize=True)
        print("wrote", dest_name, processed.mode, processed.size)
    print("done")


if __name__ == "__main__":
    main()
