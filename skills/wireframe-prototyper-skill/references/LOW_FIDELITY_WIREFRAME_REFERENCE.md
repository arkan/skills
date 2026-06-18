# Low-Fidelity Wireframe Reference

> **Prerequisite:** Read and follow all rules in `DESIGN_RULES_REFERENCE.md` first. The rules below are additional requirements specific to Low-Fidelity mode.

---

## Colors

- Only two colors allowed: `#FFFFFF` (white) and `#000000` (black).
- No shadows, no gradients, no color tints.
- Borders are 1px solid black only.

## Images

- Images render as crossbox placeholders (a rectangle or square with an X drawn corner-to-corner).
- Circular placeholders (for avatars, profile pictures) must also have a cross inside.
- Never use real images, colored backgrounds, or icons inside placeholders.

## Text

- Body text renders as black lines (variable width bars) — NOT actual text.
- Only the following show real text: titles, headings, button labels, navigation items, tab labels, and section headers.
- All other descriptive text (paragraphs, descriptions, helper text, captions) must be represented as horizontal black bars of varying widths.

## Shapes & Corners

- No rounded corners anywhere — all shapes have sharp 90-degree corners.
- The only exception is circles (`border-radius: 50%`) for circular elements (avatars, round buttons, status dots).
- No `border-radius` values between 0 and 50%.

## Input Fields

- Input fields must NOT display placeholder/hint text or black lines inside the field box.
- Input fields are rendered as empty bordered rectangles with sharp corners — completely empty inside.

## Interactivity

- No hover states — all UI is single-state, static.
- No transitions, no animations, no visual feedback on interaction.
- Navigation between screens still works (clicking buttons/links navigates to the target screen), but there is no visual hover/active indication.

## Component Styling

- All components branch on `isLofi` from `useFidelityMode()` and render their black-and-white, sharp-cornered, no-shadow variant.
- Dialogs follow the same Lo-Fi rules: black/white only, no rounded corners, no shadows, no hover states.
