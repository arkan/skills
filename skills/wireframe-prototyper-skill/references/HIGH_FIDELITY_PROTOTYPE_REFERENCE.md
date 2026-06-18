# High-Fidelity Prototype Reference

> **Prerequisite:** Read and follow all rules in `DESIGN_RULES_REFERENCE.md` first. The rules below are additional requirements specific to High-Fidelity mode.

---

## Color Usage

- All colors MUST use DS tokens (`DS.primary`, `DS.onSurface`, `DS.surfaceContainer`, etc.) — never hardcode hex values in screen files.
- Colors update in real-time when the user changes them via the Color Picker Panel. The `useDSSync()` hook ensures all screen components re-render with updated token values immediately.
- Follow M3 component-to-token mapping strictly (see `M3_COLOR_ROLES_REFERENCE.md`).
- **AppShell is excluded.** The AppShell (sidebar, toolbar, canvas background) MUST NEVER use DS tokens or have its colors changed. Its styling is fixed and independent of the design system.

## Hover States

- Add hover states for ALL UI components that would normally be clickable (buttons, chips, tabs, clickable list items, cards, links, navigation items, icons, toggles, etc.) — even if the element is static and not actually wired to a click handler in the prototype. If it looks clickable, it must have a hover state.

## Border Radius & Elevation

- Use `DS.radius` / `DS.radiusSm` for border-radius values.
- Use `DS.shadow` / `DS.shadowMd` for elevation.

## Images

- MUST generate images for **every single image slot** using AI image generation tools — no exceptions. Never show crossbox placeholders, colored rectangles, gray boxes, or generic placeholder images in Hi-Fi mode.
- **Zero tolerance for missed placeholders:** Before delivering any screen, audit it to confirm every `<img>` element and every image area has a real generated image. If a screen has 10 image slots, all 10 must have generated images.
- Generate contextually relevant images (e.g., product photos, avatars, hero banners, category images) and upload them to CDN to get hosted URLs.
- Every image visible in the prototype must be a real generated image that represents the actual content it would show in a production website.
- When building screens that display repeated items (e.g., product grids, user avatars, gallery thumbnails), generate a unique image for **each** item — do not reuse the same image across all items unless they logically represent the same thing.

## Typography

- Use the project's chosen font family loaded via Google Fonts CDN.
- Apply proper typographic hierarchy (headings, subheadings, body, captions) using consistent sizing.
- **Tools folder is excluded.** The AppShell, ScreensSidebar, Toolbar, and ColorPaletteTool keep their own fixed font styling. The chosen project font applies only to screens, dialogs, and components — never to files in the tools folder.

## Component Styling

- All components branch on `isHifi` from `useFidelityMode()` and render their full-color, rounded, shadowed, hover-enabled variant.
- Dialogs follow the same Hi-Fi rules: DS tokens, rounded corners, shadows, hover states on interactive elements within the dialog.
