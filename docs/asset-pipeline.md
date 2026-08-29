# Asset pipeline

## Runtime lifecycle

```text
UNLOADED → QUEUED → LOADING → READY
                         ↘ FAILED
```

See `nextAssetState` in `src/assets/loaders/assetLifecycle.ts`.

## Manifests

Each room has a manifest id (`room-exterior`, …). The exterior room now references a real GLB; other rooms remain empty until modeled.

Designed to carry:

- GLB / KTX2 / audio / image / video
- quality variants (HIGH / BALANCED / LOW)
- byte estimates
- fallback asset ids
- preload priority

## Production pipeline (later)

```text
.blend → GLB export → validate → optimize mesh → compress textures
      → quality variants → manifest → hashed CDN objects
```

Rules:

- 1 Blender unit = 1 meter
- apply scale/rotation before export
- never ship `.blend` files in `public/`
- hashed assets are immutable; `index.html` is not

## Current production asset

The Phase 1 exterior lives at:

- source: `assets-source/blender/digital-residence/DigitalResidence_Exterior.blend` (private, gitignored)
- generator: `tools/blender/digital-residence/build_exterior.py`
- runtime: `public/assets/world/exterior/digital-residence-exterior.glb`

Rebuild with the local Blender 5.2 CLI as documented in `tools/blender/digital-residence/README.md`.

Private QA stills live under `assets-source/blender/digital-residence/renders/` (gitignored).

## Loading order

App shell and Quick Portfolio first. Current room highest priority. Adjacent rooms preload. Distant rooms lazy. Optional effects last.
