---
name: apply-approved-architecture
description: Implement an approved architecture proposal while removing obsolete compatibility paths and preserving the intended final shape.
user-invocable: true
---

# Apply Approved Architecture

Implement the approved architecture proposal faithfully.

Do not drift back toward the historical implementation shape during coding.

The implementation must preserve the intended end state, not the easiest local diff.

## Steps

1. Read the approved architecture proposal completely before modifying code.

2. Identify:
   - intended ownership boundaries
   - deletions already approved
   - temporary migration constraints
   - areas marked "needs verification"

3. Implement the final shape directly whenever safe.
   Avoid temporary wrappers, adapters, aliases, compatibility props, or duplicated flows unless explicitly required by the migration plan.

4. Delete obsolete paths immediately after replacement.
   Do not leave dead compatibility layers behind.

5. Keep migration states coherent.
   Intermediate states must still have:
   - clear ownership
   - valid navigation
   - consistent permissions
   - understandable state flow

6. Avoid architecture drift during implementation.
   Do not introduce:
   - unnecessary abstractions
   - generic frameworks
   - registries
   - factories
   - layered indirection
   unless explicitly justified by multiple real use cases.

7. Preserve product intent.
   Prefer code that matches the user-facing behavior and domain language described in the proposal.

8. Verify:
   - routing
   - permissions
   - persisted state
   - feature flags
   - tests
   - deleted assumptions

## Rules

- The approved architecture is the source of truth.
- Prefer deletion over compatibility preservation.
- Prefer direct flows over configurable flows.
- Prefer explicit ownership over shared implicit state.
- Keep the implementation aligned with the proposed diagrams and ownership model.
- Do not reintroduce concepts removed by the proposal.
- Do not preserve dead APIs, props, routes, wrappers, or flags.
- Keep diffs coherent and migration-oriented.
- Stop and report if implementation constraints invalidate the approved architecture assumptions.
