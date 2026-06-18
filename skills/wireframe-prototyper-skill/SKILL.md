---
name: wireframe-prototyper
description: Build interactive low-fidelity wireframes and/or high-fidelity prototypes of websites as a deployed web application. Use when the user asks to create wireframes, prototypes, mockups, or design screens for a website or web app.
---

# Wireframe Prototyper

Build interactive website wireframes and prototypes as a deployed web application with dual-fidelity mode switching (Lo-Fi / Hi-Fi), a Material Design 3 color system, screen navigation sidebar, and presentation tools (fullscreen, Figma Capture mode).

## Workflow

### Phase 1: Discovery Questions

Before implementation, ask the user these questions **one at a time** like an interview. Wait for the user's response to each question before asking the next one. Do NOT batch multiple questions together.

**Question order:**

1. **Fidelity scope** — Do you need both low-fidelity wireframes and high-fidelity prototype, or just one? (If both, Hi-Fi is the default mode on load.)
2. **Competitor analysis** — Is there a competitor website to analyse and draw inspiration from? (If yes, browse it first to understand patterns, layout, and features before continuing.)
3. **Feature clarification** — Before suggesting screens, ask the user about specific features you are uncertain about. For example: "Do you need user authentication?", "Should there be a messaging system?", "Do you need a payment/checkout flow?", etc. Ask about features that are ambiguous or not explicitly mentioned — do NOT assume features exist. Tailor these questions to the type of website being built.
4. **Screen list** — After understanding the confirmed features, suggest as many screens as possible to ensure the website feels complete and covers the full user journey. Think through every flow (authentication, onboarding, core features, settings, error states, empty states, informational pages, etc.) and propose a comprehensive list. The website should NOT feel incomplete or missing key pages. Present the suggested screens grouped by section, then listen to the user's additions/removals/reordering.
5. **Project name** — Suggest a name for the prototype website and confirm.
6. **Color palette** — Ask which color palette style they prefer (warm, cool, earthy, vibrant, etc.). Generate a full M3-compliant palette from their preference and add it as the default on top of the built-in presets. The generated palette MUST pass all WCAG contrast checks (AA minimum for body text, AAA for large text).
7. **Typography** — Ask and suggest a font family to use for the website (e.g., Inter, Poppins, Nunito, DM Sans). Confirm with the user before proceeding. Load the chosen font via Google Fonts CDN in `client/index.html`.

### Phase 2: Setup

1. Initialize a webdev project (static or server template depending on needs — typically static is sufficient for wireframes).
2. Copy all files from `templates/` into the project following the folder mapping: contexts → `client/src/contexts/`, tools → `client/src/tools/`, routes.ts → `client/src/routes.ts`. Refer to `references/TEMPLATES_REFERENCE.md` for the full file list and descriptions.
3. Update `dsPresets.ts`: Add the user's custom palette as the first item in `DS_PRESETS`. Keep the standard built-in presets (Terracotta & Gold, Ocean Breeze, Midnight Violet, Emerald Garden, Arctic Frost, Berry Dusk, Slate & Citrus) below it. `DEFAULT_DS_COLORS` automatically references the first preset.
4. Update `projectConfig.ts`: Set `PROJECT_NAME` to the project's display name and `PROJECT_INITIALS` to a 1–3 letter abbreviation for the sidebar logo.
5. Update `routes.ts`: Update the route entries to match the project's screens.
6. Update `screens.ts`: Replace the screen entries with the project's actual screens (label, path pairs).
7. Set up providers in `App.tsx`: `ErrorBoundary` > `ThemeProvider` > `DesignSystemProvider` > `FidelityModeProvider` > `Router` > `AppShell`.
8. Read ALL reference files before proceeding to Phase 3.

### Phase 3: Design System Components

Before building any screens, create reusable components that enforce the design system. Each component MUST be in its own separate file under `client/src/components/`.

**Required components** (adapt names to project):
- `ActionButton` — Primary/secondary/outlined/destructive variants; uses DS tokens in Hi-Fi, black/white in Lo-Fi
- `TextInputField` — Single-line input; no placeholder in Lo-Fi, DS-styled in Hi-Fi
- `TextInputFieldMultiLine` — Multi-line textarea
- `SelectInputField` — Dropdown select
- `ImagePlaceholder` — Crossbox in Lo-Fi, real AI-generated image in Hi-Fi
- `TextPlaceholder` — Black lines in Lo-Fi, real text in Hi-Fi
- `NavigationBar` — Top nav bar
- `Footer` — Page footer
- `ProductCard` / `ListItem` — Reusable content cards
- `SearchBar`, `TabItem`, `ChipItem`, `BadgeLabel`, `Avatar`, `Checkbox`, `RadioButton`, `Switch`, `ProgressBar`, `RatingBar`, `PaginationBar`, `Carousel`, `SectionHeader`, `PageHeader`, `Accordion`

Each component must branch on `isLofi` / `isHifi` from `useFidelityMode()`.

### Phase 4: Screen Implementation

Build screens one at a time. Each screen MUST be very detailed in its implementation. Do not create sparse or skeleton-like screens. Every section, form field, label, button, list item, and piece of content that would exist in a real production app should be present. The screens should feel complete and thorough, not like placeholders waiting to be filled in later.

Each screen file goes in `client/src/screens/`:
- Imports `useFidelityMode()` and `useDSSync()` from their respective contexts
- Imports `DS` from `@/contexts/DesignSystem` for inline style color values
- **CRITICAL: Every screen MUST call `useDSSync()` at the top of the component.** This hook syncs the mutable `DS` object with the current context colours. Without it, colour changes from the Color Palette Tool will NOT propagate to that screen in real-time. The `DS` object is used for inline styles (e.g., `style={{ color: DS.primary, background: DS.surface }}`), and `useDSSync()` ensures it always reflects the latest palette.
- Renders completely different markup for Lo-Fi vs Hi-Fi (or shared structure with conditional styling)
- Uses only the design system components created in Phase 3
- Includes working navigation links between screens (both fidelity modes)

### Phase 5: Compliance Verification

This phase is MANDATORY. Do NOT skip it. Do NOT deliver to the user until every check passes. Read and follow the full checklist in `references/COMPLIANCE_CHECKLIST.md`.

## Rules

All design and implementation rules are documented in the reference files. You MUST read all of them before starting Phase 3:

1. **`references/DESIGN_RULES_REFERENCE.md`** — Common rules that apply to BOTH fidelity modes (component-first approach, app shell, color system, routes, navigation, spacing, Gestalt principles, Figma Capture mode, file structure).
2. **`references/HIGH_FIDELITY_PROTOTYPE_REFERENCE.md`** — Additional rules specific to Hi-Fi mode (DS token colors, hover states, border radius, elevation, images, typography).
3. **`references/LOW_FIDELITY_WIREFRAME_REFERENCE.md`** — Additional rules specific to Lo-Fi mode (black/white only, crossbox placeholders, text as lines, no rounded corners, no hover states, no placeholders in inputs).
4. **`references/M3_COLOR_ROLES_REFERENCE.md`** — Complete M3 color role definitions, pairing rules, component-to-token mapping, and accessibility contrast requirements.
5. **`references/TEMPLATES_REFERENCE.md`** — Template file descriptions, folder mapping, and project file structure.
6. **`references/COMPLIANCE_CHECKLIST.md`** — Phase 5 verification checklist (contexts/tools integrity, design rules audit, Hi-Fi audit, Lo-Fi audit, navigation test).
