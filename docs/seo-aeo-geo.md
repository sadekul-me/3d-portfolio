# SEO, AEO, and GEO

Important professional information must never exist only inside WebGL.

## Traditional SEO

- Semantic HTML on `/`, `/portfolio/*`, `/resume`, `/contact`
- Document title + description via `applyDocumentMeta`
- Canonical URLs from `VITE_PUBLIC_SITE_URL`
- `public/robots.txt` and `public/sitemap.xml`
- Open Graph tags
- Project deep links: `/portfolio/projects/:slug`

## Structured data

`buildJsonLd` emits WebSite always. Person / ProfilePage only for **published public** profiles. Placeholder biographies do not become schema.org Person claims.

Additional types (CreativeWork, BreadcrumbList) are added when real public case studies exist.

## AEO

Structure content so common questions are directly answerable in HTML:

- Who is this engineer?
- What technologies?
- What AI systems?
- Which projects show backend architecture?
- How to contact?

Do not keyword-stuff. Do not invent answers before canonical facts exist.

## GEO

Stable canonical pages, entity consistency, evidence-backed claims, multilingual discoverability (`en`, `zh-CN`), crawlable case studies. AI indexes only `aiReadable` published records.
