---
name: zero-tech-debt-report
description: Rework a change from the intended end state and generate an HTML architecture report with diagrams, deletions, risks, and verification steps.
user-invocable: true
---

# Zero Tech Debt Report

Rework the change from the intended end state, not from the historical path that produced the current patch.

The goal is to explain the proposed final shape clearly enough that another engineer can understand what should change, what should be deleted, why it is safe, what risks remain, and how to verify it.

## Philosophy

The best architecture is usually the one with:

- fewer concepts
- fewer transitions
- fewer compatibility paths
- clearer ownership
- more direct product intent

Prefer the code that should exist over the code that merely preserves history.

## Steps

1. State the intended end state in one or two sentences.

2. Explain why the current complexity exists.
   Identify whether it comes from:
   - unfinished migrations
   - backward compatibility
   - feature flags
   - abandoned experiments
   - missing domain boundaries
   - performance constraints
   - external contracts
   - organizational ownership

3. Search for real callers before preserving compatibility.
   If a mode, prop, wrapper, route alias, fallback, or compatibility path has no current caller, delete it.

4. Look for duplicated behavior rules, not only duplicated code.
   Pay special attention to permissions, feature flags, route gating, URL state, navigation rules, command naming, and state ownership.

5. Reshape around the final product surface.
   Prefer one clear component or flow over mode flags. Split only when it creates an obvious boundary such as state, layout, controls, or domain commands.

6. Distinguish between:
   - the ideal end-state architecture
   - the recommended implementation path given current constraints

7. Move shared rules to one place.
   Feature flags, permissions, route gating, URL state, and command naming should not be duplicated across pages or hidden in view components.

8. Identify ownership before and after the refactor:
   - state ownership
   - navigation ownership
   - permission ownership
   - side-effect ownership

9. Verify the intended flow.
   Test the new behavior and any deleted assumptions that affect navigation, permissions, routing, persisted state, or external contracts.

10. Summarize what was deleted and why it is safe.

## Output

Generate an HTML report that explains the proposed zero-tech-debt rework.

The report should include:

1. Executive summary
   - Intended end state
   - Main simplification
   - What gets deleted
   - Expected impact
   - Confidence level

2. Current shape
   - Short description of the existing complexity
   - Why the complexity exists
   - Diagram of current flow/component architecture
   - Current ownership of state, navigation, permissions, and side effects

3. Proposed shape
   - Explanation of the final product/architecture surface
   - Diagram of proposed flow/component architecture
   - Proposed ownership of state, navigation, permissions, and side effects

4. Deletions
   - Compatibility paths, flags, wrappers, aliases, fallbacks, duplicated rules, or dead abstractions to remove
   - Why each deletion is safe
   - Items that need verification before deletion

5. Ideal end state vs implementation path
   - Ideal end-state architecture
   - Recommended implementation path
   - Constraints that prevent a full clean-slate refactor immediately

6. Migration / implementation plan
   - Small ordered steps
   - Files or areas likely affected
   - Safe intermediate states
   - Rollback notes where relevant

7. Risk assessment
   - What could break
   - Unknowns
   - External dependencies
   - Rollback difficulty
   - Areas requiring staged rollout

8. Verification checklist
   - UX flow
   - permissions
   - routing
   - persisted state
   - tests
   - deleted assumptions
   - external contracts

9. Final scorecard
   - Complexity removed
   - New concepts introduced
   - Estimated maintenance impact
   - Confidence level

## Diagram rules

- Use Mermaid diagrams inside the HTML report to explain current vs proposed architecture, flow, or state transitions.
- Prefer simple diagrams over exhaustive ones.
- Every diagram must support a decision in the report.
- Quote Mermaid node labels by default, especially labels that contain routes, API paths, URLs, method names, punctuation, or placeholders.
  - Use `NodeId["POST /users/{username}/reset-password"]`.
  - Do not use `NodeId[POST /users/{username}/reset-password]`.
- Treat the following characters as requiring quoted labels in Mermaid: `{}`, `()`, `[]`, `/`, `#`, `:`, `?`, `&`, `.`, `+`, `-`, and backticks.
- Do not place route placeholders such as `{id}` or `{username}` unquoted inside labels. Mermaid parses `{` as diagram syntax, not plain text.
- Prefer stable ASCII node IDs (`RequestReset`, `AdminRoute`, `TokenStore`) and put human-readable text only in quoted labels.

## Mermaid verification

HTML parsing is not enough. Before reporting success:

1. Extract every `<pre class="mermaid">...</pre>` block from the generated HTML.
2. Parse each block with Mermaid using the same major version loaded by the report.
3. If any block fails, fix the diagram before returning.
4. A report is not valid if Mermaid renders `Syntax error in text`.

Useful validation pattern:

```js
const blocks = [...html.matchAll(/<pre class="mermaid">([\s\S]*?)<\/pre>/g)].map((match) => match[1]);
for (const block of blocks) {
  await mermaid.parse(block);
}
```

## Complexity budget

Do not increase:

- number of abstractions
- number of runtime concepts
- number of configuration points
- number of component boundaries
- number of ownership boundaries

unless the reduction in product or domain complexity clearly justifies it.

## Rules

- Optimize for the code that should exist, not the smallest diff from the old shape.
- Delete dead compatibility paths instead of making them better.
- Prefer deleting branches, modes, and compatibility layers over introducing new abstractions that preserve them.
- Do not invent a generic framework for one feature.
- Keep the refactor scoped to what makes the final shape coherent.
- Prefer names that describe product intent over implementation history.
- Look for duplicated behavior rules, not only duplicated code.
- Do not delete compatibility paths that are public API, persisted URLs, data migrations, external integrations, or customer-facing contracts unless the removal is explicitly intended.
- When unsure whether a path is still used, mark it as “needs verification” instead of deleting it.
- Avoid introducing layered architecture, factories, registries, adapters, strategy patterns, or generic orchestration unless the current system already demonstrates multiple real use cases requiring them.
- The report should be practical, concise, and implementation-oriented.
- The HTML should be self-contained and readable in a browser.
- Mermaid diagrams should be embedded as Mermaid code blocks or initialized through Mermaid CDN.
