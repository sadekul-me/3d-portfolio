# Testing strategy

No single layer replaces another. This phase implements **architecture tests**, not visual/E2E completeness.

## Present now (Vitest)

- Content schema + relationship validation
- Navigation graph BFS
- Navigation FSM
- Event bus isolation
- AI tool allowlist / unpublished entity rejection
- Fallback decisions
- i18n fallback
- Zustand selectors / commands
- Asset lifecycle
- JSON-LD placeholder gate
- Frontend secret hygiene

## Required later

| Track            | Why it exists                                         |
| ---------------- | ----------------------------------------------------- |
| Component        | Overlay/HUD behavior                                  |
| Integration      | AI → tool → command → navigation → event              |
| E2E              | Landing, 3D entry, Quick Portfolio, EN/zh-CN, contact |
| 3D / graphics    | FPS, context loss, memory                             |
| AI eval          | Grounding, refusal, injection, bilingual quality      |
| Security         | XSS, CSP, rate limits                                 |
| Accessibility    | Keyboard, SR path, reduced motion                     |
| Chaos / fallback | Break GLB, disable WebGL, fail AI                     |

## Local commands

```bash
npm test
npm run typecheck
npm run lint
npm run build
```

CI runs the same gates on pull requests.
