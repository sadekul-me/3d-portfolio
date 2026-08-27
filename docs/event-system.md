# Event system

The bus is a **lightweight synchronous** pub/sub. It is not the source of truth.

## Rules

- Past-tense event names, ID-based payloads
- Subscribers resolve canonical data themselves
- One subscriber failure cannot break others
- Every subscription has an owner and an unsubscribe path
- No pointer/camera/frame streams on the bus
- Correlation IDs on multi-step flows
- Bounded debug history in development only

## Categories present in the foundation

Navigation, content/selection, AI intentions, assets, contact, recovery, system errors.

## Adding an event

1. Add a variant to `DomainEvent` in `src/events/types/eventTypes.ts`
2. Publish only after state has changed (or after a rejected command)
3. Subscribe from a named owner (audio, telemetry, AI context) — not from random UI leaves
