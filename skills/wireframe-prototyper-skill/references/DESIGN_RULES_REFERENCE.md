# Design Rules Reference (Common)

These rules apply to **both** Low-Fidelity Wireframe mode and High-Fidelity Prototype mode.

---

## Component-First Approach

1. Create all UI components first before implementing any screens.
2. Each UI component MUST be in its own separate file — one component per file. Never combine multiple components into a single file.
3. All screens must use the design system components — no ad-hoc styling that bypasses the DS.

## App Shell & Tooling

4. Use the AppShell template exactly as provided (sidebar, top controls toolbar, fidelity mode switch, screen size display, color palette tool, Figma Capture, fullscreen mode, help button, screen navigation).
5. Include the fullscreen mode entry toast and the screen-size toast displayed in fullscreen when resized.
6. The `screens` array in AppShell must reference `ROUTES` constants, not string literals.

## Color System

7. Follow `references/M3_COLOR_ROLES_REFERENCE.md` for all color token assignments.
8. The Color Picker Panel updates screen colors in real-time via the DesignSystemContext.
9. The AppShell (sidebar, toolbar, and canvas background) has FIXED styling that MUST NEVER change — regardless of the applied design system colors, fonts, or any other customization. The AppShell is the prototyping tool's chrome, NOT part of the website being designed. Never use `DS.*` tokens, `var(--ds-*)` variables, or any design system color/font in AppShell code. All AppShell styling is already hardcoded in the `AppShell.tsx` template — do NOT modify it.
10. All generated or selected palettes MUST pass WCAG AA contrast checks. The Color Picker Panel must show contrast ratios and warn/block non-compliant combinations.

## Routes & Navigation

11. Define all screen routes in a separate `routes.ts` file.
12. Add working navigation/interactions between screens in BOTH fidelity modes. Buttons, links, cards, and CTAs that logically navigate to another screen must use `wouter` `Link` or `useLocation` to redirect to the target screen route. This applies equally to Lo-Fi and Hi-Fi modes.

## Spacing & Layout

13. Define a spacing scale at the project level (recommended: 4, 8, 12, 16, 24, 32, 48, 64px) and use only these values.
14. Maintain consistent padding within cards, sections, and containers across all screens.
15. Use consistent gap values in grids and flex layouts.

### Minimum Screen Height (900px)

16. Every generated screen MUST have a minimum height of **900px** (`min-h-[900px]`).
17. Use a flexbox column layout as the screen's outermost wrapper so content stretches to fill the minimum height.
18. **If the screen has a footer:** The main content area above the footer MUST use `flex-1` (or `flex-grow`) to fill all remaining vertical space. The footer stays at the bottom.
19. **If the screen has NO footer:** The main content area MUST use `flex-1` to fill the entire remaining height of the screen.

**Implementation pattern (with footer):**
```tsx
<div className="flex flex-col min-h-[900px]">
  <NavigationBar />
  <div className="flex-1">
    {/* Main content — stretches to fill remaining height */}
  </div>
  <Footer />
</div>
```

**Implementation pattern (without footer):**
```tsx
<div className="flex flex-col min-h-[900px]">
  <NavigationBar />
  <div className="flex-1">
    {/* Main content — stretches to fill full remaining height */}
  </div>
</div>
```

## Gestalt Principles

20. **Proximity** — Related items have smaller gaps than unrelated groups.
21. **Similarity** — Same-type components (all cards, all buttons, all inputs) look identical across screens.
22. **Continuity** — Elements on the same logical level share the same left/right/center alignment.
23. **Closure** — Complete visual forms; avoid orphaned or dangling elements.
24. **Figure-Ground** — Clear content hierarchy; primary content stands out from secondary.

## Figma Capture Mode

25. Figma Capture mode prevents dialogs and dropdown menus from auto-dismissing when clicking outside them. This allows the user to take screenshots of open dialogs/dropdowns without them closing.
26. Dialogs and dropdown menus are placed in the `client/src/dialogs/` directory, separate from screens.
27. Each dialog component should be importable and renderable within any screen that needs it.
28. Dialogs follow the same fidelity rules as screens.

**Implementation pattern for every dialog:**
```tsx
const { figmaCaptureMode } = useFidelityMode();
const handleOpenChange = (v: boolean) => { if (v || !figmaCaptureMode) onOpenChange(v); };

<Dialog open={open} onOpenChange={handleOpenChange} modal={!figmaCaptureMode}>
  <DialogContent
    noOverlay={figmaCaptureMode}
    onPointerDownOutside={(e) => { if (figmaCaptureMode) e.preventDefault(); }}
    onInteractOutside={(e) => { if (figmaCaptureMode) e.preventDefault(); }}
  >
    {/* content */}
  </DialogContent>
</Dialog>
```

**Implementation pattern for custom dropdowns (non-Dialog):**
```tsx
const { figmaCaptureMode } = useFidelityMode();
useEffect(() => {
  const handleClickOutside = (e) => {
    if (figmaCaptureMode) return; // Don't dismiss
    if (!ref.current?.contains(e.target)) setOpen(false);
  };
  document.addEventListener("mousedown", handleClickOutside);
  return () => document.removeEventListener("mousedown", handleClickOutside);
}, [isOpen, figmaCaptureMode]);
```

## File Structure

```
client/src/
├── layout/
│   └── AppShell.tsx          ← Main shell (from template, fixed colors)
├── contexts/
│   ├── FidelityModeContext.tsx
│   ├── DesignSystem.ts
│   └── DesignSystemContext.tsx
├── panels/
│   └── ColorPickerPanel.tsx  ← WCAG checks included
├── components/
│   ├── ActionButton.tsx
│   ├── TextInputField.tsx
│   ├── ImagePlaceholder.tsx  ← Crossbox in Lo-Fi, fake images in Hi-Fi
│   ├── TextPlaceholder.tsx
│   ├── NavigationBar.tsx
│   ├── Footer.tsx
│   └── ... (other DS components)
├── screens/
│   ├── Home.tsx
│   └── ... (one file per screen, with inter-screen navigation)
├── dialogs/
│   └── ... (dialogs and custom dropdown menus)
├── routes.ts
├── App.tsx
└── main.tsx
```
