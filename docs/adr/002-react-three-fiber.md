# ADR-002: React Three Fiber over a raw Three.js-only architecture

- Status: Accepted
- Date: 2026-08-28

## Context

The experience engine must compose rooms, lighting, and spatial UI inside a React application without putting frame data into React state.

## Decision

Use Three.js through React Three Fiber, with Drei as an opt-in helper layer. Scene objects still must not store canonical content.

## Alternatives

- Imperative Three.js owned outside React
- A full game engine (Unity/PlayCanvas)

## Rationale

R3F matches the React shell, enables lazy room modules, and keeps disposal aligned with React trees when used carefully.

## Trade-offs

- Risk of leaking per-frame values into React if discipline slips
- Drei helpers can hide cost

## Consequences

`useFrame` is a hot path. Quality, camera, and particles stay in refs/GSAP. Content stays in the catalog.

## Security / performance / UX impact

Performance is an architectural constraint. Helpers require profiling before adoption.
