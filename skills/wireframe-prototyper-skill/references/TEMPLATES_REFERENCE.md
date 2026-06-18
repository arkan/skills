# Templates Reference

## Template Files

All tool-related templates go into `client/src/tools/`:

- `templates/AppShell.tsx` — App shell wrapper that composes ScreensSidebar and Toolbar. Handles fullscreen mode, keyboard shortcuts, help overlay, and container size measurement. Use this file directly — do NOT rewrite from scratch.
- `templates/ScreensSidebar.tsx` — Left sidebar with project logo, screen count badge, numbered navigation list with active state highlighting and auto-scroll. Use this file directly — do NOT rewrite from scratch.
- `templates/Toolbar.tsx` — Top toolbar with: screen name display, fidelity mode toggle (Lo-Fi / Hi-Fi), container size display, ColorPaletteTool (Hi-Fi only), Figma Capture Mode toggle, Full Screen button, Help button, and Prev/Next navigation. Use this file directly — do NOT rewrite from scratch.
- `templates/ColorPaletteTool.tsx` — Complete color palette tool with: manual hex editing per token, built-in and custom preset selection, save/update/rename/delete custom presets, export/import JSON, eyedropper tool, WCAG contrast checker with per-swatch warning indicators. Use this file directly — do NOT rewrite from scratch.
- `templates/screens.ts` — Screen definitions array (label + path pairs). Use this file directly — only update the entries to match the project's screens.
- `templates/projectConfig.ts` — Project name and initials config. Update the TODO values with the project's name and a 1–3 letter abbreviation for the sidebar logo.

Context templates go into `client/src/contexts/`:

- `templates/FidelityModeContext.tsx` — Fidelity mode context provider (Lo-Fi / Hi-Fi, Figma Capture). Use this file directly — do NOT rewrite from scratch.
- `templates/DesignSystem.ts` — DS token object with live sync hook for real-time color updates. Use this file directly — do NOT rewrite from scratch.
- `templates/DesignSystemContext.tsx` — Full context provider with token state, CSS variable injection, localStorage persistence, preset management (built-in + custom), and the `useDesignSystem()` hook. Use this file directly — do NOT rewrite from scratch.
- `templates/dsPresets.ts` — Preset palettes array and DEFAULT_DS_COLORS reference. Update with the user's custom palette as the first entry. Keep the built-in presets below it.

Component templates go into `client/src/components/`:

- `templates/ImagePlaceholder.tsx` — Image placeholder component. Lo-Fi: crossbox with label. Hi-Fi: real image with border radius from DS tokens. Adapt the image source helper to your project.
- `templates/TextPlaceholder.tsx` — Text placeholder component. Lo-Fi: black bars/lines. Hi-Fi: real text with DS colour tokens. Supports single-line (inline span) and multi-line (block paragraph) modes.

Route template:

- `templates/routes.ts` — Route constants pattern. Use this file directly — do NOT rewrite from scratch. Only update the route entries to match the project's screens.

## File Structure

```
client/src/
  components/                     ← Reusable UI components (one per file)
    ImagePlaceholder.tsx           ← Image placeholder (crossbox in Lo-Fi, real image in Hi-Fi)
    TextPlaceholder.tsx            ← Text placeholder (bars in Lo-Fi, real text in Hi-Fi)
  contexts/                       ← React contexts
    DesignSystem.ts               ← DS token object & useDSSync hook
    DesignSystemContext.tsx        ← M3 colour state, presets, import/export
    dsPresets.ts                  ← Built-in colour presets & DEFAULT_DS_COLORS
    FidelityModeContext.tsx        ← Lo-Fi / Hi-Fi toggle & Figma Capture state
  dialogs/                        ← Interactive dialog/overlay components
  hooks/                          ← Custom hooks
  icons/                          ← Icon component files
  layout/                         ← Layout wrappers (e.g., SettingsLayout)
  lib/                            ← Utility helpers
  photos/                         ← CDN photo URL mappings
  screens/                        ← All screen components
  tools/                          ← App shell and toolbar tools
    AppShell.tsx                   ← Shell wrapper (sidebar + toolbar + canvas)
    ColorPaletteTool.tsx           ← M3 colour system editor with presets & WCAG checker
    projectConfig.ts              ← Project name & initials for sidebar
    screens.ts                    ← Screen definitions (label + path)
    ScreensSidebar.tsx             ← Left sidebar with screen navigation
    Toolbar.tsx                    ← Top toolbar with fidelity toggle and tools
  ui/                             ← shadcn/ui components
  App.tsx                         ← Routes & provider setup
  index.css                       ← Global styles & Tailwind design tokens
  main.tsx                        ← React entry point
  routes.ts                       ← Route constants
```
