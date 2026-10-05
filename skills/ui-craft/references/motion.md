# Motion compatibility policy

This policy governs motion inside `ui-craft`. Existing product motion tokens and
the user's brief come first; Emil's `emil-design-eng` supplies defaults when
none exist. Load `animate` for a requested implementation only after resolving
whether motion helps. Load its recipes only for the relevant interaction.

## Resolve competing recipes

Jakub's owners retain authority over their non-motion domains. Inside this
workflow, their exact animation recipes are suggestions to evaluate rather than
a second motion system. In particular:

- Reuse the established press scale instead of alternating between Jakub's
  `0.96` and Emil's `0.97`. An existing responsive press state may need no change.
- Do not globally apply the contextual icon `scale(0.25)` and blur recipe.
  Prefer an existing icon transition; add motion only for a useful state cue.
- Reuse existing easing/duration tokens. Treat the sub-300ms recommendation as
  the normal interaction budget; a larger sheet may justify a longer duration,
  and frequent keyboard actions should respond instantly.
- Keep the active primitive's focus and dismissal semantics. Derive transform
  origin from its actual API, not Base UI attributes copied into React Aria.
- Prefer transform/opacity for movement, but profile claims about compositor
  acceleration instead of treating every upstream statement as a guarantee.

## Component discovery and tools

`animate` tells the agent to invoke `pick-ui-library` for components. Replace
that step with the already selected library adapter. The upstream picker is
intentionally absent and would not govern this workflow even if installed.

Use CSS for simple state transitions. Reuse an existing motion library for
springs, interruption or gestures. Add a dependency only when a required
interaction cannot reasonably use the current tools. Honor reduced motion and
pointer capabilities with the implementation, and retain a static state cue.

## Review and invocation

The routine motion check applies the model-invocable `emil-design-eng`
principles. `review-animations` is a separate explicit-only workflow and runs
only when the user invokes it. The upstream review's rules do not automatically
trigger a second review or override this policy's documented exceptions.

Direct vendor invocations retain their original policies. Explain the missing
picker and motion differences if a user chooses that path; recommend
`ui-craft` for an integrated library-aware workflow. Do not claim that a router
can impose global precedence on independently invoked skills.
