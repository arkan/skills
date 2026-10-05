---
name: ui-craft
description: Build, refine, or review frontend interfaces with the project's component library, coherent visual design, and verified interactions. Prefer Untitled UI for new React projects, including PRO when licensed; preserve established libraries. Not for backend-only work.
---

# UI Craft

Use this workflow to compose a complete interface with the selected library and
apply the relevant quality owners. Local compatibility policy governs this
workflow; imported skills used independently retain their upstream behavior.

## Workflow

1. **Resolve the surface and library.** Read project instructions, dependencies,
   configuration and the target component's imports. Follow
   [routing](references/routing.md) before loading any library skill.
   Completion: name the surface, library, existing visual conventions and
   whether this is a build, refinement, or read-only review.
2. **Establish direction.** Read `DESIGN.md` when present and inspect the existing
   surface. Preserve its identity for refinement. For new work, state the page's
   purpose, hierarchy, density, type and palette in a compact direction grounded
   in the brief. An available frontend-design or Impeccable skill may help when
   relevant; neither is required. Completion: the layout serves the actual task
   and its loading, empty, success and error states are accounted for.
3. **Compose official components.** Load only the active adapter:
   [Untitled UI](references/untitled-ui.md) or [shadcn](references/shadcn.md).
   Reuse installed components and tokens before adding new ones. Other established
   libraries keep their native APIs. Completion: imports resolve, interactions
   work and accessible library behavior survives composition.
4. **Apply the relevant owners.** Load the installed `better-layout`,
   `better-typography`, `better-colors`, `better-writing`, `better-accessibility`
   and `better-ui` owners for the domains touched by the task. Consult their
   references only for a relevant issue. For motion, load
   [motion policy](references/motion.md) before Emil or Jakub's recipes.
   Completion: confirmed problems have a correction in the project's own idiom,
   with one owner per underlying rule.
5. **Verify and report.** Follow [verification](references/verification.md).
   For a read-only screen review, `better-interface` can consolidate the inspected
   domains. For a build, apply authorized corrections, then confirm the affected
   states once. Completion: report the actual checks, uncovered domains and any
   unresolved product decision; review-only work leaves source unchanged.

Missing owners reduce coverage. Name them and continue with the available
owners and documented project conventions; do not claim their domains were
reviewed. Preserve factual copy and business rules, surfacing ambiguity when it
changes correctness.
