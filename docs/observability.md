# Observability

Vendor-neutral `TelemetryService`:

- `log`
- `metric`
- `trace` / `traceAsync`
- `reportError`

Metadata: app version, build id, asset manifest version, correlation id, anonymous session id, module, latency, fallback used.

Development uses a console adapter. Production uses a no-op until a vendor adapter is attached. Telemetry must never crash the app and must redact secret-like payloads.

## Error taxonomy

Categories: APP, SCENE, ASSET, RENDER, NAVIGATION, AI, RETRIEVAL, TOOL, CONTACT, I18N, PERFORMANCE, SECURITY, RECOVERY.

Severity: INFO, WARN, ERROR, CRITICAL.

Visitor-facing copy is an i18n key. Technical messages stay in telemetry.

## Diagnostics HUD

FPS, frame time, draw calls, room, quality, assets, AI status.

Shown only when `import.meta.env.DEV` **and** `VITE_PUBLIC_ENABLE_DIAGNOSTICS=true`. Not a visitor feature. Production may later expose a curated health view inside the AI Lab.
