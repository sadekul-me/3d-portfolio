# ADR-001: React + Vite instead of a server-first framework

- Status: Accepted
- Date: 2026-08-28

## Context

The product is a cinematic 3D portfolio with a mandatory non-3D path. A server-rendered app framework would add runtime cost without helping the WebGL experience.

## Decision

Use React 19 + Vite as the application shell. Core content is compiled into the static bundle. A small same-origin API may be added later for AI, contact, and analytics.

## Alternatives

- Next.js / Remix / other SSR frameworks
- Raw Three.js + vanilla DOM

## Rationale

Static-first delivery, fast HMR, explicit client architecture for R3F, and a tiny dynamic surface.

## Trade-offs

- Less built-in SSR/SEO than a server framework; we compensate with crawlable Quick Portfolio routes, meta, sitemap, and JSON-LD.
- Dynamic features require an explicit API later.

## Consequences

Hosting is CDN-friendly. Engineers must keep professional information in HTML routes, not only in the canvas.

## Security / performance / UX impact

Smaller origin attack surface. Shell can paint before 3D loads. Quick Portfolio remains first-class.
