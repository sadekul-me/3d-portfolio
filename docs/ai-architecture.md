# AI architecture

Visitor-facing intelligence is a **grounded, tool-enabled** layer. It is not implemented in this phase. The boundary is.

```text
Question → retrieval (approved knowledge)
        → model
        → structured tool / intention
        → schema validation
        → policy / allowlist
        → application command
        → navigation / UI / Three.js
```

The LLM never mutates Three.js objects, React state, Zustand, or the filesystem.

## Allowlisted tools

- `navigate_to_room`
- `open_project`
- `show_skill`
- `show_architecture`
- `open_resume`
- `open_contact`

Unknown tools fail closed. Unpublished or non-`aiReadable` entities cannot be opened by AI.

## Deterministic shortcuts

Opening contact/resume or navigating by exact room name should not require an LLM when local routing can answer.

## Grounding

Answers must come from approved canonical fields. Unsupported claims are refused. Placeholder catalog content is not AI-indexable.

## Streaming

HTTP streaming is allowed later. WebSocket is not introduced without a real bidirectional need.

## Client

`UnimplementedAiClient` throws if called. Production will use `POST /api/v1/ai/chat` with the shared Zod contract.
