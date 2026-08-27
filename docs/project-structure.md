# Project structure

```text
src/
  app/           Application shell: bootstrap, routes, command dispatcher, config
  experience/    3D runtime policies: camera, quality, loading, fallback, audio
  scenes/        Per-room modules. Today: definitions only, not final art
  content/       Canonical catalog: schemas, seed, validation, repositories
  navigation/    Room graph, BFS pathing, navigation FSM, URL map
  events/        Typed event bus (facts, not state)
  ai/            Tool contracts, policy, intention → command mapping
  api/           Shared HTTP contracts for a later small API
  ui/            Primitives, HUD, overlays, Quick Portfolio, accessibility
  animation/     Motion tokens shared by UI and future GSAP timelines
  assets/        Registry, manifests, lifecycle — no .blend files
  shaders/       Registration policy for future GLSL
  store/         Zustand application state and selectors
  hooks/         Thin React bindings to store/config
  i18n/          EN / zh-CN UI catalogs
  observability/ Telemetry, errors, diagnostics HUD
  security/      CSP, external links, env hygiene
  search/        Deterministic linear index over published content
  seo/           Meta + JSON-LD builders
  lib/           Result type, ids, storage
  types/         Brands, rooms, locale, visibility, quality
  tests/         Cross-cutting architecture tests
```

## Where new work goes

| If you are adding…      | Put it here                                | Do not                               |
| ----------------------- | ------------------------------------------ | ------------------------------------ |
| A professional fact     | `src/content/seed` then validate           | Duplicate it in a scene or UI string |
| A room/scene            | `src/scenes/<room>/` plus catalog room row | Store copy inside the GLB            |
| A cinematic camera move | GSAP via `CameraDirector`                  | Zustand per-frame position           |
| A 2D micro-interaction  | Motion + `motionTokens`                    | GSAP                                 |
| An AI action            | `src/ai` tool schema → command             | Direct Three.js mutation             |
| A user-facing string    | `src/i18n` or localized content fields     | Hardcode in feature logic            |
| A secret                | server-side only (future API)              | `VITE_*` or repo files               |

## Scene ownership

When a room is implemented, split it:

- definition / bindings
- lighting
- interaction
- effects
- spatial UI
- disposal

Do not create a god-component house.
