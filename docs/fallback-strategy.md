# Fallback strategy

```text
Premium 3D → Reduced 3D → Lightweight → Quick Portfolio → Static core
```

Implemented by `decideExperienceMode` in `src/experience/fallback/fallbackPolicy.ts`.

User overrides are honored unless they require an unavailable capability (for example Premium 3D without WebGL).

## Failure matrix

| Failure                      | Behavior                                                           |
| ---------------------------- | ------------------------------------------------------------------ |
| WebGL missing / context lost | Quick Portfolio                                                    |
| Heavy GLB fails              | Retry → lower variant → 2D representation                          |
| AI down                      | Search + navigation remain                                         |
| Contact provider down        | Retry + professional email (when published)                        |
| Missing zh-CN                | English fallback; production validation should catch required gaps |
| Animation interrupted        | FSM safe state                                                     |
| Audio fails                  | Silent continue                                                    |
| Resume asset fails           | HTML resume route                                                  |

## Boundaries

App → Experience → Scene → AI → Project → Contact.

A failed optional layer must not white-screen the portfolio.
