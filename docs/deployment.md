# Deployment

Static-first, CDN-first. One codebase; geography-aware delivery later, not duplicated product logic.

## Topology

```text
Visitor → DNS → CDN + WAF
              → hashed JS/CSS/GLB
              → index.html (short cache)
              → optional API gateway (AI, contact, analytics, health)
```

## Cache

| Artifact        | Cache                          |
| --------------- | ------------------------------ |
| `index.html`    | short / no-cache               |
| hashed JS/CSS   | immutable                      |
| hashed GLB/KTX2 | immutable                      |
| asset manifest  | versioned with the app release |

## Environments

`LOCAL → PREVIEW → STAGING → RELEASE CANDIDATE → PRODUCTION`

Developer machines do not deploy production.

## China / global

Self-host critical fonts and runtime assets. AI provider routing must tolerate regional differences. If AI is down, search and Quick Portfolio remain useful.

## This phase

`npm run build` produces `dist/`. Host it on any static platform. Do not attach provider secrets to the static bucket.

Security headers from `src/security/csp.ts` should be applied at the CDN/WAF, not in Vite HMR.
