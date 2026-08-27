# UX standards

Priority: **Understand → Navigate → Interact → Experience → Impress**

No effect may reduce usability. Bloom, reflections, and camera motion yield to readability, FPS, and comfort.

## Interface layers

- Invisible UI: minimal HUD
- Spatial UI: labels in-world, length-aware for EN/zh-CN (`src/ui/spatial`)
- Overlay UI: project/contact/AI/settings readability

## Navigation UX

- Guided cinematic travel by default, not mandatory WASD
- Map / direct room buttons always available
- Resume, Contact, Quick Portfolio remain one click away
- Skip cinematic during transitions
- Reduced motion shortens travel to a logical cut
- Mobile is touch-first, not a shrunk desktop rig

## Accessibility foundation

- Skip link to `#main`
- Keyboard-focusable chrome
- Semantic Quick Portfolio
- Contrast-oriented tokens
- Non-color-only current-room state (label text + selected chip)
- 3D geometry is never the only representation of a professional fact

## Motion tokens

Use `src/animation/tokens/motionTokens.ts`. Do not invent per-component durations.
