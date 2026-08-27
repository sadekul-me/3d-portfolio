# ADR-004: Zustand for minimal global application state

- Status: Accepted
- Date: 2026-08-28

## Context

Several features share room, selection, locale, and quality. React context for high-churn values would re-render too broadly. A large Redux store would invite dumping frame state into it.

## Decision

Use Zustand with a small store: navigation, preferences, selection, session. Mutations go through `dispatchCommand`. Derived data uses selectors.

## Alternatives

- React context only
- Redux Toolkit
- XState as the global store

## Rationale

Minimal API, good selector performance, easy to keep frame data out. Navigation lifecycle still uses a pure FSM module, not a giant machine-as-store.

## Trade-offs

- Discipline is required; the store will not stop a developer from putting camera position in it
- Tests must reset the singleton

## Consequences

Command / state / event remain separated. The event bus does not replace the store.

## Security / performance / UX impact

No high-frequency subscriptions. Session context stays non-PII.
