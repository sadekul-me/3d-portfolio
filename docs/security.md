# Security

The public site is untrusted. Keep the attack surface small.

## Secrets

- Only `VITE_PUBLIC_*` may reach the browser.
- `.env.example` contains public placeholders only.
- LLM, SMTP, and database credentials never belong in this app bundle.

## Headers

`src/security/csp.ts` exports a CSP and companion headers for CDN/WAF configuration. They are **not** injected into Vite dev `index.html` because HMR would break. Wire them at the edge in deployment.

## Links and contact

- External links: `noopener noreferrer`
- Contact (future): server validation, honeypot `website` field, rate limits, generic errors
- Request size limits at the API boundary

## AI

- Tool allowlist
- No arbitrary URL/shell/filesystem tools
- Prompt injection: system and tool policy remain authoritative
- AI cannot index `internal` or unpublished content

## Dependencies

CI should block release on critical vulnerabilities once scanning is attached. Do not install packages without a documented reason.
