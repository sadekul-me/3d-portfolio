# ADR-003: GSAP for cinematic sequences, Motion for 2D UI

- Status: Accepted
- Date: 2026-08-28

## Context

Room travel is cinematic and interruptible. Overlay UI needs short bilingual-safe motion. One library doing both jobs usually produces either sluggish UI or weak camera control.

## Decision

GSAP owns 3D cinematic timelines (camera, room activation, lighting cues) via `CameraDirector`. Motion owns 2D UI. Shared numeric tokens live in `src/animation/tokens`.

## Alternatives

- Motion/Framer for everything
- Custom lerp loops in `useFrame`
- Theatre.js / other editorial timeline tools

## Rationale

GSAP is proven for interruptible camera timelines. Motion is appropriate for React trees. Tokens stop random durations.

## Trade-offs

- Two animation libraries to learn
- Must not mix responsibilities

## Consequences

Reduced-motion users skip GSAP travel. UI still uses Motion with near-zero duration.

## Security / performance / UX impact

Cinematics remain skippable. No animation library may block information access.
