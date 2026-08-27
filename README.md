# Digital Residence

Production-grade architecture foundation for an interactive 3D portfolio.

This repository currently contains **Phase 0 — Foundations**. It is not the finished residence, not a complete AI assistant, and not a populated biography. It is the software architecture that later phases will implement against.

## Start here

1. Read [`docs/README.md`](docs/README.md)
2. Read [`docs/architecture.md`](docs/architecture.md)
3. Read [`docs/project-structure.md`](docs/project-structure.md)

The locked product/architecture contract is:

`Digital Residence CTO Production Architecture Handbook.docx`

Implementation documentation in `docs/` translates that handbook into the repository. If the two ever conflict, reopen the decision through an ADR. Do not silently diverge.

## Scripts

```bash
npm install
npm run dev
npm run test
npm run lint
npm run typecheck
npm run build
```

## Non-negotiables

- Canonical content is defined once and reused by 3D, Quick Portfolio, search, AI, and SEO.
- The 3D experience is an experience layer, never an information barrier.
- AI cannot mutate React, Zustand, Three.js, or the filesystem.
- No secrets in frontend environment variables.
- Do not invent professional claims. Placeholder catalog records are marked as such.
