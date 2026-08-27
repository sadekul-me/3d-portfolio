# Architecture knowledge base

This folder is the implementation knowledge base for **Digital Residence**.

It is derived from the locked CTO Production Architecture Handbook. It is not a copy of that handbook. Use these pages to find where work belongs in _this_ repository.

## Read order

| Role           | Start                                        | Then                                                                                                                   |
| -------------- | -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| New engineer   | [project-structure.md](project-structure.md) | [architecture.md](architecture.md), [content-model.md](content-model.md)                                               |
| Senior / staff | [architecture.md](architecture.md)           | [state-data-flow.md](state-data-flow.md), [event-system.md](event-system.md), [ai-architecture.md](ai-architecture.md) |
| Reviewer / CTO | [system-context.md](system-context.md)       | [security.md](security.md), [fallback-strategy.md](fallback-strategy.md), [adr/](adr/)                                 |

## Index

- [architecture.md](architecture.md) — locked thesis, stack, and module boundaries
- [system-context.md](system-context.md) — actors, trust boundaries, topology
- [project-structure.md](project-structure.md) — where new code belongs
- [content-model.md](content-model.md) — canonical catalog, visibility, validation
- [state-data-flow.md](state-data-flow.md) — commands, Zustand, frame-local state
- [event-system.md](event-system.md) — typed events and subscriber rules
- [navigation-system.md](navigation-system.md) — room graph and FSM
- [asset-pipeline.md](asset-pipeline.md) — manifests, lifecycle, Blender export intent
- [performance-budget.md](performance-budget.md) — quality tiers and frame budget
- [ux-standards.md](ux-standards.md) — guided UX, motion, accessibility
- [ai-architecture.md](ai-architecture.md) — visitor-facing intelligence boundary
- [ai-maintenance-policy.md](ai-maintenance-policy.md) — constrained engineering assistant
- [security.md](security.md) — CSP, secrets, tool allowlists
- [observability.md](observability.md) — telemetry, errors, diagnostics
- [fallback-strategy.md](fallback-strategy.md) — degradation hierarchy
- [testing-strategy.md](testing-strategy.md) — what to test at which layer
- [deployment.md](deployment.md) — static-first delivery
- [seo-aeo-geo.md](seo-aeo-geo.md) — crawlable professional information
- [adr/](adr/) — architecture decision records

## Current phase

Phase 0 — Foundations. The 3D house, authored biography, and live LLM integration are intentionally absent.
