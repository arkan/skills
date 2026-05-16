---
name: zero-tech-debt-report
description: Rework a change from the intended end state and generate an HTML architecture report with diagrams, risks, migration guidance, architecture invariants, and PRD handoff information.
user-invocable: true
---

# Zero Tech Debt Report

Rework the change from the intended end state, not from the historical path that produced the current patch.

The goal is to explain the proposed final shape clearly enough that another engineer or LLM can understand:

- what should change
- what should be deleted
- why it is safe
- what risks remain
- what ownership model should exist
- what migration path should be followed
- what must never be reintroduced

The report must be usable both as:
- a human architecture review document
- a machine-readable handoff for PRD and implementation generation

## Philosophy

The best architecture is usually the one with:

- fewer concepts
- fewer transitions
- fewer compatibility paths
- clearer ownership
- more direct product intent

Prefer the code that should exist over the code that merely preserves history.

Historical implementation constraints are not architectural truth.

## Refactoring stance

Assume that significant refactoring is acceptable when required to reach a coherent end-state architecture.

Do not optimize for:
- minimal diffs
- preserving historical structure
- incremental compatibility
- keeping obsolete abstractions alive

It is acceptable to:
- move responsibilities across layers
- redesign ownership boundaries
- collapse obsolete abstractions
- rewrite confusing flows
- replace transitional architectures
- remove compatibility systems entirely
- simplify APIs aggressively

when doing so produces a substantially clearer and more maintainable final architecture.

The target is not "minimal disruption".

The target is:
- conceptual clarity
- coherent ownership
- direct product intent
- reduced long-term maintenance cost
- elimination of accidental complexity

Transitional complexity is acceptable only when it directly enables migration toward the approved final architecture.

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
   Pay special attention to:
   - permissions
   - feature flags
   - route gating
   - URL state
   - navigation rules
   - command naming
   - loading ownership
   - side-effect ownership

5. Reshape around the final product surface.
   Prefer one clear component or flow over mode flags.
   Split only when it creates an obvious boundary such as:
   - state
   - layout
   - controls
   - domain commands

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
   - loading lifecycle ownership

9. Define architecture invariants.
   Explicitly state the rules that must remain true after the refactor.

10. Verify the intended flow.
    Test the new behavior and any deleted assumptions that affect:
    - navigation
    - permissions
    - routing
    - persisted state
    - external contracts
    - migration safety

11. Summarize what was deleted and why it is safe.

## Language

The report language must match the language used in the conversation.

Examples:
- If the conversation is in French, generate the report in French.
- If the conversation is in English, generate the report in English.
- If the conversation switches languages, prefer the dominant language used for architecture and implementation discussions.

All sections must follow the selected language consistently, including:
- headings
- explanations
- diagrams labels
- migration steps
- PRD handoff
- risk assessment
- verification checklist

## Output

Generate a self-contained HTML report that explains the proposed zero-tech-debt rework.

The report should include:

# 1. Executive summary

- Intended end state
- Main simplification
- What gets deleted
- Expected impact
- Confidence level

# 2. Current shape

- Short description of the existing complexity
- Why the complexity exists
- Diagram of current flow/component architecture
- Current ownership of:
  - state
  - navigation
  - permissions
  - side effects
  - loading lifecycle

# 3. Proposed shape

- Explanation of the final product/architecture surface
- Diagram of proposed flow/component architecture
- Proposed ownership of:
  - state
  - navigation
  - permissions
  - side effects
  - loading lifecycle

# 4. Deletions

- Compatibility paths, flags, wrappers, aliases, fallbacks, duplicated rules, or dead abstractions to remove
- Why each deletion is safe
- Items that need verification before deletion

Explicitly identify:
- things intentionally removed forever
- concepts that must not be reintroduced

# 5. Architecture invariants

Define the architectural rules that must remain true after implementation.

Examples:
- one source of truth for permissions
- one navigation flow
- no runtime mode switching
- no duplicated loading ownership
- no compatibility aliases

# 6. Ideal end state vs implementation path

- Ideal end-state architecture
- Recommended implementation path
- Constraints preventing a full clean-slate refactor immediately
- Accepted intermediate migration states

# 7. Migration / implementation plan

- Small ordered steps
- Files or areas likely affected
- Safe intermediate states
- Rollback notes where relevant
- Dependencies between migration steps

# 8. Risk assessment

- What could break
- Unknowns
- External dependencies
- Rollback difficulty
- Areas requiring staged rollout
- Assumptions requiring validation

# 9. Verification checklist

- UX flow
- permissions
- routing
- persisted state
- tests
- deleted assumptions
- external contracts
- migration cleanup completion

# 10. PRD handoff

Provide structured information that another LLM can directly convert into a PRD.

Include:
- User-facing problem
- Product goal
- User stories candidates
- UX expectations
- Approved implementation decisions
- Approved ownership model
- Architecture invariants
- Explicit anti-goals
- Required deletions
- Migration constraints
- Testing expectations
- Out of scope
- Open questions

# 11. Final scorecard

- Complexity removed
- New concepts introduced
- Estimated maintenance impact
- Confidence level

## Diagram rules

- Use Mermaid diagrams inside the HTML report to explain current vs proposed architecture, flow, state transitions, or ownership changes.
- Prefer simple diagrams over exhaustive ones.
- Every diagram must support a decision in the report.
- Diagrams should emphasize simplification, ownership clarity, or removal of compatibility paths.

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
- Prefer a larger coherent refactor over a smaller change that preserves architectural debt.
- Delete dead compatibility paths instead of making them better.
- Prefer deleting branches, modes, and compatibility layers over introducing new abstractions that preserve them.
- Do not invent a generic framework for one feature.
- Keep the refactor scoped to what makes the final shape coherent.
- Prefer names that describe product intent over implementation history.
- Look for duplicated behavior rules, not only duplicated code.
- Do not delete compatibility paths that are:
  - public API
  - persisted URLs
  - data migrations
  - external integrations
  - customer-facing contracts
  unless the removal is explicitly intended.
- When unsure whether a path is still used, mark it as "needs verification" instead of deleting it.
- Avoid introducing:
  - layered architecture
  - factories
  - registries
  - adapters
  - strategy patterns
  - generic orchestration
  unless the current system already demonstrates multiple real use cases requiring them.
- The report should be practical, concise, and implementation-oriented.
- The HTML should be readable directly in a browser.
- Mermaid diagrams should be embedded as Mermaid code blocks or initialized through Mermaid CDN.
- Do not mix languages inside the report unless explicitly requested.

## Anti-goals

Do not:
- preserve compatibility paths without verified callers
- introduce new wrappers around deprecated behavior
- add runtime mode switching where ownership can be explicit
- duplicate permissions or navigation logic
- spread loading ownership across multiple layers
- reintroduce concepts explicitly removed by the proposal
- optimize for minimizing the diff at the expense of architecture clarity
