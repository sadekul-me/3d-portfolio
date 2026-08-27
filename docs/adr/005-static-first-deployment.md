# ADR-005: Static-first core deployment

- Status: Accepted
- Date: 2026-08-28

## Context

The portfolio must remain useful if AI, contact, or WebGL fail. A mandatory backend would make the core product fragile and expensive.

## Decision

Ship the application as a static Vite build. Optional APIs are additive. Cache hashed assets immutably; keep `index.html` short-cached.

## Alternatives

- Always-on Node server
- Multi-service microservice backend

## Rationale

Matches the locked handbook: CDN-first, rollbackable, economical for an asset-heavy 3D app.

## Trade-offs

- Preview/staging still need a real host
- China/global routing is a delivery concern, not a second codebase

## Consequences

CI produces `dist/`. Secrets never go into the static bucket.

## Security / performance / UX impact

Smaller attack surface, better cache behavior, Quick Portfolio works without APIs.
