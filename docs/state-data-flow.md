# State and data flow

```text
Canonical content
        ↓
Selectors / application state
        ↓
Command dispatcher
        ↓
Zustand truth
        ↓
Events (facts)
        ↓
UI / Experience / telemetry subscribers
```

## Commands vs state vs events

- **Commands** request change (`NAVIGATE_TO_ROOM`, `SET_LANGUAGE`).
- **State** records truth (current room, locale, selection).
- **Events** announce completed facts (`ROOM_ENTERED`, `LANGUAGE_CHANGED`).

`dispatchCommand` in `src/app/commands/dispatcher.ts` is the application mutation boundary.

## What belongs in Zustand

- current room and navigation phase
- selected project / skill / architecture case
- language, sound, quality, experience-mode override
- privacy-safe session context
- transition flags

## What must stay out of React/Zustand

- camera transforms
- shader time
- pointer coordinates
- particle transforms
- other per-frame render values

Those live in Three.js refs, uniforms, and GSAP timelines.

## Selectors

Derive values in `src/store/selectors.ts`. Do not duplicate facts in extra store fields.
