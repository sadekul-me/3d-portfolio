# Asset pipeline

## Runtime lifecycle

```text
UNLOADED → QUEUED → LOADING → READY
                         ↘ FAILED
```

See `nextAssetState` in `src/assets/loaders/assetLifecycle.ts`.

## Manifests

Each room has a manifest id (`room-exterior`, …). Foundation manifests are empty on purpose: there is no final Blender content yet.

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

## Loading order

App shell and Quick Portfolio first. Current room highest priority. Adjacent rooms preload. Distant rooms lazy. Optional effects last.
