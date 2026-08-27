# Performance budget

Targets:

- Capable desktop: ~60 FPS, stable frame time, **16.67ms** budget
- Supported mobile: 30+ FPS with reduced fidelity
- Frame stability matters more than average FPS

## Quality model

`AUTO | HIGH | BALANCED | LOW`

`resolveQuality` maps a preset + device capabilities to DPR cap, particles, post-processing, shadows, and texture tier. User overrides are respected. Aggressive runtime auto-tuning is an extension point, not implemented.

## Render-loop rule

No uncontrolled O(n) work inside `useFrame`. Partition:

- frame-critical: camera follow already in GSAP/Three
- interaction hints: ~10–20 Hz
- analytics: ~1 Hz

Future tools: instancing, object pools, BVH raycasts, LOD, dirty flags.

## Core Web Vitals (shell / non-3D)

Aim for LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1 on the 2D shell. 3D load must not block identity/resume/contact.
