# Routing and ownership

## Identify the established library

Use evidence from the target surface's imports, component sources, theme and
configuration schema, supported by `package.json` dependencies. A
`components.json` filename alone is insufficient: Untitled UI and shadcn both
use it. React Aria alone is also insufficient because other libraries use it.

- Existing Untitled UI: follow the Untitled UI adapter.
- Existing shadcn: load its official skill through the shadcn adapter.
- Deliberately mixed project: follow the target surface's library and shared
  conventions. Avoid importing a second primitive or icon family for a missing
  component before checking the active library.
- New compatible React project: prefer Untitled UI unless the brief chooses
  another library. Resolve FREE/PRO access through the Untitled UI adapter.
  Check the current official installation requirements before
  initialization; existing dependencies do not authorize an upgrade.
- Other stack or established library: preserve its native conventions. The
  React adapters do not prescribe a migration.

Ask only when evidence conflicts in a way that affects the implementation.
Report the chosen library and the evidence before modifying components.

## Task routing

| Task | Route |
| --- | --- |
| Build a surface | Direction, active adapter, touched quality domains, verification |
| Refine a surface | Preserve identity and behavior; correct confirmed problems |
| Review a screen | Read-only domain inspection, consolidated findings with coverage |
| Review a diff or branch | Respect `better-interface`'s explicit-only `interface-review` boundary; if unavailable, report the limitation and perform the requested scoped review directly without claiming that workflow ran |
| Implement useful motion | Local motion policy, then model-invocable Emil guidance |
| Explore competing UI directions | Use the existing `prototype` only when authorized by its invocation policy; otherwise present the concrete choice without launching a prototype workflow |

`review-animations` is explicit-only. Offer it for a focused motion audit and
run it only when the user asks. `pick-ui-library`, `interface-review`, and other
unselected upstream workflows are not dependencies of this integration.
`animate`'s component-selection step is replaced by the active adapter here.

## Quality authority

The user brief and project instructions govern scope. Preserve the selected
library's APIs, tokens and accessible behavior. Correct confirmed functional or
accessibility failures even when they are inherited. Jakub's domains own layout,
type, copy, color, accessibility and static polish; the local motion policy owns
animation conflicts. Translate fixes into existing tokens rather than imposing
an unrelated identity or redesigning a shared component for a cosmetic preference.

These rules govern `ui-craft`. Directly invoked imported skills keep their
upstream policies and may disagree. If another owner is independently loaded
during this workflow, reconcile its suggestions here before applying changes.
