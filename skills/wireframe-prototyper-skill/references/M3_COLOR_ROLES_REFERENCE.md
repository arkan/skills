# M3 Color Roles Reference

> Source: [Material Design 3 — Color Roles](https://m3.material.io/styles/color/roles) [1]

This document defines when and where each M3 color token should be used in the Kiddiwear design system. All UI components must follow these guidelines to ensure proper accessibility, visual hierarchy, and theme consistency.

---

## General Concepts

Material Design 3 organises colour into **roles** rather than fixed values. Each role carries semantic meaning that determines where and how it should be applied. Understanding these concepts is essential before using any token.

| Term | Meaning |
|------|---------|
| **Surface** | A role used for backgrounds and large, low-emphasis areas of the screen. |
| **Primary, Secondary, Tertiary** | Accent colour roles used to emphasise or de-emphasise foreground elements. |
| **Container** | Roles used as a fill colour for foreground elements like buttons, FABs, and chips. They should NOT be used for text or icons directly. |
| **On** | Indicates a colour for text or icons displayed on top of its paired parent colour. For example, "on primary" is used for text/icons placed against a primary fill. |
| **Variant** | Offers a lower-emphasis alternative to its non-variant pair. For example, "outline variant" is less emphasised than "outline". |

**Critical Rule:** Colours must only be combined in their intended pairs or layering orders. Improper combinations break accessibility contrast guarantees. [1]

---

## Primary (Most Prominent Elements)

Primary roles are reserved for the most prominent components across the UI: FABs, high-emphasis buttons, active states, and key action elements. Primary draws the most attention and should be used sparingly to maintain its impact. [1]

| Token | Role | When to Use |
|-------|------|-------------|
| **primary** | High-emphasis fills, text, and icons against surface | Filled buttons (CTA), active navigation indicators, key action icons, text links, focused input field indicators, active toggle states |
| **onPrimary** | Text and icons against primary | Text/icons inside a primary-coloured filled button; checkmark inside a selected checkbox; handle of an active switch |
| **primaryContainer** | Standout fill colour against surface for key components | FAB backgrounds, extended FAB backgrounds, selected toggle states, prominent cards requiring emphasis |
| **onPrimaryContainer** | Text and icons against primary container | Text/icons inside FABs, extended FAB labels and icons, text inside primary container elements |

---

## Secondary (Less Prominent Elements)

Secondary roles are for less prominent components that still need accent differentiation from the surface: filter chips, tonal buttons, and selected navigation states. Secondary supports primary without competing for attention. [1]

| Token | Role | When to Use |
|-------|------|-------------|
| **secondary** | Less prominent fills, text, and icons against surface | Dialog icons, secondary action icons |
| **onSecondary** | Text and icons against secondary | Text/icons inside secondary-coloured elements |
| **secondaryContainer** | Less prominent fill colour against surface | Tonal buttons, active navigation indicators in nav bars/rails, selected filter chips, selected input chips |
| **onSecondaryContainer** | Text and icons against secondary container | Text/icons inside tonal buttons, active navigation icons, selected chip labels |

---

## Tertiary (Contrasting Accents)

Tertiary roles provide contrasting accents that balance primary and secondary, or bring heightened attention to specific elements. The tertiary colour is at the designer's discretion and supports broader colour expression in the UI. [1]

| Token | Role | When to Use |
|-------|------|-------------|
| **tertiary** | Complementary fills, text, and icons against surface | Accent elements needing distinct emphasis separate from primary/secondary |
| **onTertiary** | Text and icons against tertiary | Text/icons inside tertiary-coloured elements |
| **tertiaryContainer** | Complementary container colour against surface | Accent cards, alternative emphasis containers |
| **onTertiaryContainer** | Text and icons against tertiary container | Text/icons inside tertiary container elements |

---

## Error (Error States)

Error roles communicate error states: incorrect input, validation failures, and destructive actions. Error is a **static colour** — it does not change in dynamic colour schemes but still adapts between light and dark themes. [1]

| Token | Role | When to Use |
|-------|------|-------------|
| **error** | Attention-grabbing colour for fills, icons, and text indicating urgency | Error icons, error text below inputs, destructive action buttons, badge containers for notifications |
| **onError** | Text and icons against error | Text/icons inside error-coloured elements, badge labels |
| **errorContainer** | Attention-grabbing fill colour against surface | Error message backgrounds, error banners, validation error highlights |
| **onErrorContainer** | Text and icons against error container | Text/icons inside error container elements |

---

## Surface (Backgrounds and Containers)

Surface roles provide neutral backgrounds, while surface container roles create visual hierarchy through subtle tonal differences for component fills like cards, sheets, dialogs, and navigation areas. [1]

### Base Surface Roles

| Token | Role | When to Use |
|-------|------|-------------|
| **surface** | Default colour for backgrounds | Main page background, body area background, top app bar (flat/scrolled to top), outlined card container |
| **onSurface** | Text and icons against any surface or surface container colour | Primary text, headings, high-emphasis body text, leading icons, input text in text fields, active indicator lines in filled text fields |
| **onSurfaceVariant** | Lower-emphasis text and icons against any surface or surface container colour | Secondary text, placeholder/label text in text fields, supporting icons, metadata, inactive navigation icons/labels, trailing icons, unselected chip labels, unselected radio/checkbox outlines |

### Surface Container Roles (Hierarchy and Nesting)

These create visual hierarchy through subtle tonal differences. They progress from lowest emphasis to highest emphasis, enabling nested containers and layered layouts. [1]

| Token | Role | When to Use |
|-------|------|-------------|
| **surfaceContainerLowest** | Lowest-emphasis container | Content areas that need to appear recessed below the default surface |
| **surfaceContainerLow** | Low-emphasis container | Elevated cards, assist chips (optional fill), side panels, secondary navigation areas |
| **surfaceContainer** | Default container colour | Navigation bars, navigation rails, menus, standard dialogs, bottom sheets |
| **surfaceContainerHigh** | High-emphasis container | Dialogs, full-screen dialogs, search bars, elevated containers needing emphasis |
| **surfaceContainerHighest** | Highest-emphasis container | Filled text field containers, filled card containers, switch track (off state), linear progress indicator tracks |

**Key Mapping:**
- **Body/page background** → `surface`
- **Navigation bars and rails** → `surfaceContainer`
- **Elevated cards** → `surfaceContainerLow`
- **Filled cards** → `surfaceContainerHighest`
- **Dialogs and sheets** → `surfaceContainerHigh` (standard) or `surfaceContainerLow` (bottom sheets)
- **Text field fills** → `surfaceContainerHighest`
- **Nested containers** → step up the hierarchy (Low → default → High → Highest)

### Inverse Colours

Applied selectively to create contrasting effects against the surrounding UI. These are used for components that intentionally invert the colour scheme to stand out. [1]

| Token | Role | When to Use |
|-------|------|-------------|
| **inverseSurface** | Background fills for elements contrasting against surface | Snackbar containers |
| **inverseOnSurface** | Text and icons against inverse surface | Snackbar supporting text |
| **inversePrimary** | Actionable elements against inverse surface | Snackbar action button text |

### Additional Surface Roles

| Token | Role | When to Use |
|-------|------|-------------|
| **surfaceDim** | Dimmest surface colour, maintains relative brightness across themes | Alternative backgrounds where consistent dimness is needed in both light and dark |
| **surfaceBright** | Brightest surface colour, maintains relative brightness across themes | Alternative backgrounds where consistent brightness is needed in both light and dark |
| **scrim** | Colour of the scrim overlay behind modal elements | Modal dialog scrims, bottom sheet scrims, navigation drawer scrims |

---

## Outline (Boundaries and Dividers)

Outline roles define boundaries and separators with specific contrast requirements. The distinction between outline and outline variant is critical for accessibility compliance. [1]

| Token | Role | When to Use |
|-------|------|-------------|
| **outline** | Important boundaries requiring 3:1 contrast against surface | Text field outlines (enabled state), important interactive boundaries, switch track borders (off state), assist chip outlines, suggestion chip outlines |
| **outlineVariant** | Decorative elements with lower contrast needs | Dividers, outlined card borders, list separators, decorative lines, unselected filter chip outlines, unselected input chip outlines |

### Critical Do's and Don'ts

- **DO** use `outline` for text field borders and interactive element boundaries that require 3:1 contrast.
- **DO** use `outlineVariant` for dividers, card borders, and decorative separators.
- **DON'T** use `outline` for dividers — they have different contrast requirements and `outline` is too heavy.
- **DON'T** use `outline` for card borders — use `outlineVariant` instead (cards have multiple internal elements providing contrast).
- **DON'T** use `outlineVariant` to create visual hierarchy or define target boundaries that need 3:1 contrast.
- **CAUTION:** `outlineVariant` can be used for chip/button borders only when the elements inside (icons, text) already provide 4.5:1 contrast against the surface. [1]

---

## Fixed Accent Colours (Add-on Roles)

Fixed accent colours maintain the same tone in both light and dark themes, unlike standard accent colours which invert. They are useful for elements that need consistent colour recognition regardless of theme. [1]

| Token | Role | When to Use |
|-------|------|-------------|
| **primaryFixed** | Fill colour that stays the same tone in light and dark | Elements needing consistent primary recognition across themes |
| **primaryFixedDim** | Stronger, more emphasised tone relative to primaryFixed | Higher-emphasis variant of fixed primary |
| **onPrimaryFixed** | Text and icons on primaryFixed | High-emphasis content on fixed primary fills |
| **onPrimaryFixedVariant** | Lower-emphasis text and icons on primaryFixed | Secondary content on fixed primary fills |
| **secondaryFixed** / **secondaryFixedDim** | Same pattern as primary fixed, for secondary | Consistent secondary recognition across themes |
| **onSecondaryFixed** / **onSecondaryFixedVariant** | Text/icons on secondary fixed fills | Content on fixed secondary fills |
| **tertiaryFixed** / **tertiaryFixedDim** | Same pattern as primary fixed, for tertiary | Consistent tertiary recognition across themes |
| **onTertiaryFixed** / **onTertiaryFixedVariant** | Text/icons on tertiary fixed fills | Content on fixed tertiary fills |

> **Warning:** Do not use fixed colours where contrast is critical, as they do not adapt between themes and may fail contrast requirements in one mode. [1]

---

## Component-to-Token Mapping (Quick Reference)

This table maps each component to its correct M3 colour tokens based on the official component specifications. [2] [3] [4] [5] [6] [7] [8] [9]

| Component | Fill/Background | Text/Icons | Border |
|-----------|----------------|------------|--------|
| **Page background** | surface | onSurface | — |
| **Top app bar (flat)** | surface | onSurface (leading icon, headline), onSurfaceVariant (trailing icon) | — |
| **Top app bar (scrolled)** | surfaceContainer | onSurface, onSurfaceVariant | — |
| **Navigation bar** | surfaceContainer | onSecondaryContainer (active icon), onSurface (active label), onSurfaceVariant (inactive icon/label) | — |
| **Navigation bar indicator** | secondaryContainer | — | — |
| **Navigation drawer** | surfaceContainerLow | onSurfaceVariant (inactive), onSecondaryContainer (active label) | — |
| **Navigation drawer indicator** | secondaryContainer | — | — |
| **Filled card** | surfaceContainerHighest | onSurface | — |
| **Elevated card** | surfaceContainerLow | onSurface | — |
| **Outlined card** | surface | onSurface | outlineVariant |
| **Dialog** | surfaceContainerHigh | onSurface (headline), onSurfaceVariant (body), secondary (icon) | — |
| **Dialog buttons** | — | primary | — |
| **Bottom sheet** | surfaceContainerLow | onSurface | — |
| **Bottom sheet drag handle** | — | onSurfaceVariant | — |
| **Filled button (CTA)** | primary | onPrimary | — |
| **Tonal button** | secondaryContainer | onSecondaryContainer | — |
| **Elevated button** | surfaceContainerLow | primary | — |
| **Outlined button** | transparent | primary | outline |
| **Text button** | transparent | primary | — |
| **FAB** | primaryContainer | onPrimaryContainer | — |
| **Extended FAB** | primaryContainer | onPrimaryContainer (icon + label) | — |
| **Filter chip (unselected)** | — | onSurfaceVariant | outlineVariant |
| **Filter chip (selected)** | secondaryContainer | onSecondaryContainer | — |
| **Assist chip** | — | onSurface (label), primary (icon) | outline |
| **Input chip (unselected)** | — | onSurfaceVariant | outlineVariant |
| **Input chip (selected)** | secondaryContainer | onSecondaryContainer | — |
| **Suggestion chip** | — | onSurfaceVariant | outline |
| **Filled text field** | surfaceContainerHighest | onSurface (input), onSurfaceVariant (label/placeholder), primary (focused label/indicator) | — |
| **Outlined text field** | transparent | onSurface (input), onSurfaceVariant (label/placeholder), primary (focused label/outline) | outline (enabled), primary (focused) |
| **Search bar** | surfaceContainerHigh | onSurface (input), onSurfaceVariant (placeholder) | — |
| **Badge** | error | onError | — |
| **Divider** | — | — | outlineVariant |
| **Snackbar** | inverseSurface | inverseOnSurface (text), inversePrimary (action button) | — |
| **Switch (on)** | primary (track) | onPrimary (handle), onPrimaryContainer (icon) | — |
| **Switch (off)** | surfaceContainerHighest (track) | outline (handle) | outline |
| **Checkbox (selected)** | primary | onPrimary (checkmark) | — |
| **Checkbox (unselected)** | transparent | — | onSurfaceVariant |
| **Radio button (selected)** | — | primary (outer + inner circle) | — |
| **Radio button (unselected)** | — | — | onSurfaceVariant |
| **Progress indicator (active)** | primary | — | — |
| **Progress indicator (track, linear)** | surfaceContainerHighest | — | — |
| **Progress indicator (track, circular)** | secondaryContainer | — | — |
| **Tabs (active)** | — | primary (label + indicator) | — |
| **Tabs (inactive)** | — | onSurfaceVariant | — |
| **Tab container** | surface | — | — |
| **List item** | — | onSurface (headline), onSurfaceVariant (supporting text, leading/trailing icons) | — |
| **Slider (active track)** | primary | — | — |
| **Slider (inactive track)** | surfaceContainerHighest | — | — |
| **Slider (handle)** | primary | — | — |

---

## Pairing Rules Summary

Colours must only be applied in their intended pairs. Using an "on" colour against the wrong background breaks accessibility contrast guarantees. [1]

1. **primary** ↔ **onPrimary** (text/icons on primary fills)
2. **primaryContainer** ↔ **onPrimaryContainer**
3. **secondary** ↔ **onSecondary**
4. **secondaryContainer** ↔ **onSecondaryContainer**
5. **tertiary** ↔ **onTertiary**
6. **tertiaryContainer** ↔ **onTertiaryContainer**
7. **error** ↔ **onError**
8. **errorContainer** ↔ **onErrorContainer**
9. **surface** / all **surfaceContainer*** ↔ **onSurface** or **onSurfaceVariant**
10. **inverseSurface** ↔ **inverseOnSurface** (with **inversePrimary** for actions)
11. **primaryFixed** ↔ **onPrimaryFixed** or **onPrimaryFixedVariant**
12. **secondaryFixed** ↔ **onSecondaryFixed** or **onSecondaryFixedVariant**
13. **tertiaryFixed** ↔ **onTertiaryFixed** or **onTertiaryFixedVariant**

> Text and icons on any surface or surface container should use `onSurface` (high emphasis) or `onSurfaceVariant` (lower emphasis). Never use `onPrimary` on a surface background — it is only valid against `primary`. [1]

---

## Accessibility Contrast Requirements

M3 colour roles are designed to meet WCAG accessibility standards when used in their correct pairings. [1]

| Requirement | Minimum Ratio | Applies To |
|-------------|---------------|------------|
| **Text contrast (normal text)** | 4.5:1 | All "on" colours against their paired background |
| **Large text / UI components** | 3:1 | Interactive boundaries (outline), large headings |
| **Decorative elements** | No minimum | Dividers, decorative borders (outlineVariant) |

The M3 system guarantees these ratios only when tokens are used in their designated pairs. Mixing tokens across pairs (e.g., using `onPrimary` against `secondaryContainer`) voids contrast guarantees.

---

## References

[1]: https://m3.material.io/styles/color/roles "Material Design 3 — Color Roles"
[2]: https://m3.material.io/components/buttons/specs "Material Design 3 — Buttons Specs"
[3]: https://m3.material.io/components/cards/specs "Material Design 3 — Cards Specs"
[4]: https://m3.material.io/components/navigation-bar/specs "Material Design 3 — Navigation Bar Specs"
[5]: https://m3.material.io/components/text-fields/specs "Material Design 3 — Text Fields Specs"
[6]: https://m3.material.io/components/chips/specs "Material Design 3 — Chips Specs"
[7]: https://m3.material.io/components/dialogs/specs "Material Design 3 — Dialogs Specs"
[8]: https://m3.material.io/components/floating-action-button/specs "Material Design 3 — FAB Specs"
[9]: https://m3.material.io/components/snackbar/specs "Material Design 3 — Snackbar Specs"
