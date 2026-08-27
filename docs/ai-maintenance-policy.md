# AI-assisted maintenance policy

This is a **separate** AI concept from the visitor-facing guide.

Reliability is owned by deterministic engineering. AI may diagnose and propose recovery; it is not the authority for production stability.

## Doctrine

Preserve before improve. Patch before rewrite. Validate before apply. Roll back before risking stability.

Encoded in `src/ai/policies/maintenance.ts`.

## Tiers

| Tier             | Allowed                                                               |
| ---------------- | --------------------------------------------------------------------- |
| 1 Diagnose only  | Read allowed context, classify, explain, propose                      |
| 2 Safe patch     | Bounded files, targeted tests, deterministic checks, revert own patch |
| 3 Human-approved | Refactor, architecture, dependencies — never fully autonomous         |

## Forbidden

- Reading secrets
- Changing production environment
- Force-push / deploy
- Weakening TypeScript, security, or tests
- Arbitrary dependency installs
- Deleting unrelated files
- Silent architecture changes

Autonomous production code modification is **not** implemented in this phase.

## Safe runtime recovery tools (later)

`retry_asset`, `switch_asset_variant`, `set_quality_mode`, `restore_safe_scene`, `switch_ai_provider`, `disable_optional_effect`.
