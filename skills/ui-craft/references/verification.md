# Verification and reporting

Use the project's existing safe checks and inspect the rendered target when
visual judgment or runtime behavior matters. A passing build does not establish
visual quality or keyboard correctness.

## Bounded build cycle

Inspect the relevant desktop and mobile states in one batched pass. Correct
confirmed problems together, then confirm the affected states once. Stop when
the requested behavior and quality checks pass; a concrete remaining defect may
justify another targeted check. Review-only requests produce findings without
source edits.

Check navigation, input validation, dialogs, focus return, feedback, loading,
empty and error states. Test long realistic content through the actual data
boundary, not by changing the component to manufacture a break. Use `break-ui`
when a requested stress test warrants its fixtures; keep its controls in a
development/prototype surface and respect its report-before-fix boundary.

Exercise narrow layouts, keyboard use, reduced motion, and the project's actual
supported themes. For mobile-specific work, consult `mobile-native` and
distinguish emulation checks from behavior that needs a real phone. Let product
requirements resolve meaningful choices such as truncation versus expansion.

Prefer T3's collaborative preview tools when available, following the runtime's
browser discovery flow. If browser access is unavailable or rejected, keep
unaffected checks moving and label visual/runtime checks `Not verified`.

## Report evidence

For every inspected domain, record the relevant command or interaction and its
result. Use one findings row per root cause with source locations and affected
states; prioritize functional and accessibility failures over cosmetic changes.
Fix shared causes at the appropriate component or token.

`better-interface` can consolidate a screen review across its available owners.
Respect its distinct explicit-only change-review boundary. Mark a missing owner
`Not reviewed`; mark an unavailable check `Not verified`. Approval covers only
the inspected scope and does not imply full coverage of untested surfaces.

For integration evaluations, record the prompt, detected library, loaded skills,
executed commands, tested versions and screenshots. Use the actual agent trace
to substantiate routing; source wording or screenshots alone cannot prove that
the model selected the intended workflow.
