# System context

```mermaid
flowchart LR
  visitor[Visitor browser]
  app[Digital Residence]
  cdn[CDN / WAF / static hosting]
  assets[Hashed GLB / KTX2 / media]
  api[API / edge gateway]
  llm[LLM provider]
  mail[Mail provider]
  tel[Telemetry backend]

  visitor --> cdn --> app
  app --> assets
  app --> api
  api --> llm
  api --> mail
  app --> tel
```

## Actors

- **Visitor** — untrusted. Receives static assets and public JSON. Never receives secrets.
- **Application shell** — trusted only as client code. Assume it can be modified.
- **Same-origin API** (future) — the only place provider credentials may exist.
- **Canonical catalog** — trusted content after Zod + relationship validation.

## Trust boundary

Browser → HTTPS → CDN/WAF → static app.

Dynamic calls, when introduced, stay on:

- `POST /api/v1/ai/chat`
- `POST /api/v1/contact`
- `POST /api/v1/analytics/events`
- `GET /api/v1/config/public`
- `GET /api/v1/health/*`

The frontend must not call OpenAI, Anthropic, SMTP, or analytics vendor SDKs directly.

## Runtime context that is allowed

Privacy-safe session context in memory: language, motion preference, coarse visitor type, current room. No durable invasive profile.
