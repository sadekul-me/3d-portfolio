# ADR-006: AI structured tool boundary

- Status: Accepted
- Date: 2026-08-28

## Context

The product wants a bilingual AI guide that can navigate rooms and open evidence. Unconstrained model output is a security, UX, and hallucination risk.

## Decision

The model may only emit structured intentions/tools from an allowlist. Output is schema-validated, policy-checked, then mapped to `AppCommand`. Unpublished content is not tool-addressable.

## Alternatives

- Free-form HTML/JS from the model
- Direct Three.js/React mutation from tool callbacks
- Unbounded function calling

## Rationale

Keeps the LLM outside the runtime. Enables evals, refusals, and prompt-injection resistance.

## Trade-offs

- More boilerplate than “just call the SDK”
- Some natural-language requests must be refused

## Consequences

`src/ai` has no provider keys. `UnimplementedAiClient` stands in until `/api/v1/ai/chat` exists.

## Security / performance / UX impact

No arbitrary execution. Deterministic navigation still works when AI is down.
