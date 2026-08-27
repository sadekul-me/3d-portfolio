# Content model

Canonical content is the single source of truth for:

- 3D spatial UI
- Quick Portfolio
- Search
- Skill evidence
- Architecture graphs
- AI retrieval (published + `aiReadable` only)
- SEO / JSON-LD (published + `public` only)

## Pipeline

```text
raw seed → Zod schema → relationship validation → CanonicalCatalog → consumers
```

Build-time validation runs via `npm run validate:content` (also chained into `npm run build`). Invalid relations fail the build.

## Entities

Profile, Experience, Education, Skill, Project, ArchitectureCase (nodes, edges, flows, decisions), Achievement, MediaAsset, SceneBinding, Room.

Skills have **evidence**, not percentages. Evidence is derived:

`Skill → Projects + Experience + Architecture cases`

## Visibility

Each record has:

- `publicationStatus`: `placeholder` | `draft` | `published`
- `visibility`: `public`, `aiReadable`, `searchable`, `internal`

Foundation seed marks the owner profile as **placeholder** and **internal**. JSON-LD Person nodes are therefore not emitted. Do not treat placeholder strings as biography.

## Validation catches

- missing rooms from the locked zone list
- duplicate ids/slugs
- unknown skill/project/architecture references
- broken architecture edges/flows
- broken scene bindings
- placeholders when `rejectPlaceholders: true` (release gate, not current phase)

## Authoring rule

One fact, one record. Do not repeat skill names as free text on projects when a `skillId` exists.
