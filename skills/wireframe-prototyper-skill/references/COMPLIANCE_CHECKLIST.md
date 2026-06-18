# Compliance Checklist

This checklist is MANDATORY. Do NOT skip it. Do NOT deliver to the user until every check below passes. Go through the entire project screen by screen and verify compliance in detail.

## Step 1: Contexts and tools folder integrity check

- Open every file in `client/src/contexts/` and `client/src/tools/` and confirm they are untouched from the templates.
- The ONLY acceptable changes are the TODOs in `dsPresets.ts` (user's palette added), `routes.ts` (project routes), `screens.ts` (project screens), and `projectConfig.ts` (project name and initials).
- If any other modification is found in the contexts or tools folders, revert it immediately.

## Step 2: Design Rules audit (DESIGN_RULES_REFERENCE.md)

Re-read the full reference file, then check EVERY rule against the implementation:
- [ ] Each UI component is in its own separate file (no multi-component files)
- [ ] Every screen has `min-h-[900px]` on its outermost container
- [ ] Every screen uses `flex flex-col` wrapper
- [ ] Content area uses `flex-1` to fill remaining height (with or without footer)
- [ ] Spacing follows the defined scale consistently
- [ ] Gestalt principles are applied (proximity, alignment, repetition, contrast, figure-ground)
- [ ] Figma Capture mode works: dialogs and dropdowns do NOT auto-dismiss when clicking outside
- [ ] Every dialog has the Figma Capture implementation pattern (checking `isFigmaCapture` before closing)
- [ ] Navigation between screens works in both fidelity modes
- [ ] All navigation links point to valid routes

## Step 3: Hi-Fi mode audit (HIGH_FIDELITY_PROTOTYPE_REFERENCE.md)

Switch to Hi-Fi mode and navigate through EVERY screen. Check:
- [ ] DS tokens are used for ALL colours (no hardcoded hex values in Hi-Fi mode)
- [ ] Every screen calls `useDSSync()` at the top of the component
- [ ] Change a colour in the Color Palette Tool and confirm it propagates to the current screen in real-time
- [ ] Every clickable element has a visible hover state
- [ ] Every image slot has a real generated image (no placeholders, no missing images)
- [ ] Each repeated item (product cards, list items, avatars) has a UNIQUE image
- [ ] Typography uses the chosen project font
- [ ] Border radius is applied consistently
- [ ] Elevation/shadows are used appropriately
- [ ] WCAG contrast passes for all text on all backgrounds

## Step 4: Lo-Fi mode audit (LOW_FIDELITY_WIREFRAME_REFERENCE.md)

Switch to Lo-Fi mode and navigate through EVERY screen. Check:
- [ ] Only black and white colours are used (no greys, no brand colours)
- [ ] All images show crossbox placeholders (X through a rectangle)
- [ ] Text content is represented as black lines/bars, not real text
- [ ] No rounded corners anywhere
- [ ] No hover states on any element
- [ ] Input fields are empty with no placeholder text or hints
- [ ] No shadows or elevation
- [ ] Layout structure matches the Hi-Fi version (same sections, same hierarchy)

## Step 5: Cross-screen navigation test

- Navigate through every screen using the sidebar
- Click every internal link on every screen in both modes
- Confirm no dead links, no broken routes, no navigation errors

## Step 6: Fix all violations

- Fix every issue found during steps 1-5
- After fixing, re-run the checks on the affected screens to confirm the fix
- Do NOT deliver to the user until all checks pass with zero violations
