# ADR-008: Quick Portfolio as a mandatory non-3D access path

- Status: Accepted
- Date: 2026-08-28

## Context

WebGL, heavy assets, and cinematic motion will fail for some visitors. A 3D-only portfolio would hide the candidate.

## Decision

Quick Portfolio is a first-class product surface at `/portfolio/*`, not a degraded afterthought. Fallback policy can route here automatically. Semantic HTML is the crawlable professional record.

## Alternatives

- 3D-only with a screenshot fallback
- PDF-only resume
- Hidden “text version” link

## Rationale

Matches the architectural thesis and accessibility/SEO requirements. Recruiters can complete the journey without entering the residence.

## Trade-offs

- Two presentations to keep in sync — solved by the canonical catalog, not duplicated copy
- Landing must advertise the path equally

## Consequences

Experience routes may redirect here. JSON-LD and sitemap include these URLs.

## Security / performance / UX impact

Core Web Vitals apply to this path. Keyboard and screen-reader access live here first.
