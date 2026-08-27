# ADR-007: Canonical content as single source of truth

- Status: Accepted
- Date: 2026-08-28

## Context

3D, Quick Portfolio, search, skill evidence, architecture views, AI, and SEO all need the same professional facts. Duplicating copy guarantees drift and invented claims.

## Decision

Author content once in a Zod-validated catalog. Consumers read repositories/selectors. AI and search only see published + permitted visibility flags.

## Alternatives

- Copy in each scene file
- Headless CMS in v1
- Markdown per page with no relations

## Rationale

Relational evidence (skill ↔ project ↔ architecture) is core to the product. Static TypeScript seed is enough for v1; a CMS can replace the seed loader later if the schema stays.

## Trade-offs

- Non-engineers need a future authoring path
- Validation must stay strict

## Consequences

Placeholder profile is explicit. Build fails on broken relations. No fake percentage skills.

## Security / performance / UX impact

Internal records cannot leak to AI or JSON-LD. One pipeline to test.
