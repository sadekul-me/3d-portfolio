# Navigation system

## Graph

Rooms are an adjacency list sourced from the canonical catalog. Direct targeting is allowed. BFS resolves unweighted paths (`src/navigation/graph/resolvePath.ts`).

The algorithm is intentionally simple so a later Dijkstra/A* adapter can add cinematic weights without rewriting callers.

Fallback destination: `identity`.

## Finite state machine

```text
IDLE → REQUESTED → TRANSITIONING → ARRIVED → ACTIVE
```

Handled cases:

- invalid room → rejected event, no camera mutation
- click current room → ignored
- click during transition → interrupt and retarget (never two cameras)
- reduced motion → skip to ARRIVED
- FAIL → safe ACTIVE at last known room
- RESET → identity

GSAP/camera code **observes** phase changes through `CameraDirector`. It does not own room identity.

## URLs

| Path                  | Purpose                 |
| --------------------- | ----------------------- |
| `/`                   | Landing, crawlable      |
| `/experience/:roomId` | 3D experience deep link |
| `/portfolio/*`        | Quick Portfolio         |
| `/resume`             | Resume surface          |
| `/contact`            | Contact surface         |
