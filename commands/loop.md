---
description: "Run one autonomous loop iteration toward a durable goal"
agent: build
---

# Autonomous loop iteration

You are running one iteration of a durable autonomous work loop.

User arguments:

```text
$ARGUMENTS
```

## State files

Use these files as the loop's durable state:

- `.opencode-goal/goal.md` — authoritative goal, constraints, non-goals, and done criteria.
- `.opencode-goal/progress.md` — current checklist, decisions, validation history, and next step.
- `.opencode-goal/DONE` — completion marker. Create only when all done criteria are met and validation passes.
- `.opencode-goal/BLOCKED` — blocker marker. Create only when user input or external access is required.

## Startup protocol

1. If `$ARGUMENTS` is non-empty and no active goal exists, create `.opencode-goal/goal.md` from the arguments and initialize `.opencode-goal/progress.md` with a concise checklist.
2. If `$ARGUMENTS` starts with `new:` or `reset:`, archive the current `.opencode-goal` directory into `.opencode-goal/archive/<timestamp>/` when practical, then start a new goal from the remaining arguments.
3. If `$ARGUMENTS` is non-empty and an active goal already exists, treat the arguments as additional constraints or corrections. Update the goal/progress files instead of silently replacing the goal.
4. If `.opencode-goal/DONE` exists, report the completed status and stop.
5. If `.opencode-goal/BLOCKED` exists, report the blocker and stop unless the arguments explicitly resolve or reset the blocker.
6. If no goal exists and `$ARGUMENTS` is empty, ask for the goal and stop.

## Strategy confidence checkpoint

Before implementing any code or content change for the active goal, create or update the strategy section in `.opencode-goal/progress.md`.

The strategy must include:

- the current plan,
- assumptions,
- known risks,
- validation evidence needed,
- explicit acceptance criteria.

Then ask yourself this exact question:

> Are you factually 100% confident in this strategy, given the repository state, available evidence, and stated goal? If not, find all possible loopholes, suggest proper fixes, update the strategy, and run this confidence loop again until you are factually 100% confident in the new strategy.

Run the confidence loop as an adversarial review before implementation:

1. Look for loopholes, hidden assumptions, missing validation, edge cases, scope creep, destructive risks, and simpler alternatives.
2. If any issue is found, update `.opencode-goal/progress.md` with the issue and the strategy fix.
3. Re-check the revised strategy with the same question.
4. Do not implement until the strategy is supported by concrete repository evidence, docs, tests, or explicit user requirements.
5. If factual 100% confidence is impossible with available evidence, do not pretend. Write the residual uncertainty and either:
   - perform the smallest research or validation step needed, or
   - write `.opencode-goal/BLOCKED` if user input or external access is required.

## Excellence bar

Every decision must target the ideal long-term solution for the repository, not a short-term workaround.

The selected strategy, code, patterns, and final architecture must be A+++ quality:

- top-notch and scalable by default,
- aligned with the best proven patterns for this codebase,
- maintainable by future agents and humans,
- mechanically validated where practical,
- free of hacks, brittle shortcuts, temporary patches, and decisions likely to be regretted later.

Do not trade long-term correctness for speed. If the ideal scalable solution is unclear, use the strategy confidence checkpoint to find the missing evidence. If the goal cannot be achieved without compromising this bar, write `.opencode-goal/BLOCKED` and explain the trade-off instead of implementing a compromise.

### Boil the ocean

Within the active goal, ship the complete permanent solution. Search before
building. Test before shipping. Document what matters. Do not defer dangling
threads when tying them off is within reach. Do not present a workaround when
the real fix exists. If the complete solution is blocked by missing input,
credentials, external access, or destructive-risk approval, write
`.opencode-goal/BLOCKED` instead of compromising.

## Work protocol

1. Read the durable state files and inspect the current repository state.
2. Complete the strategy confidence checkpoint before implementation.
3. Maintain an explicit todo list for the active goal. Keep unfinished todos visible while work remains so auto-continuation can keep running.
4. Pick the next smallest useful step toward the goal.
5. Make only scoped changes required for that step.
6. Run the relevant validation commands for the changed area.
7. If validation fails, fix the failure before starting unrelated work.
8. Update `.opencode-goal/progress.md` with:
   - what changed,
   - validation commands and results,
   - strategy confidence updates when the plan changed,
   - current checklist state,
   - next recommended step.

## Continuation rule

If auto-continue is enabled and unfinished todos remain, do not stop after
completing a validated milestone. Immediately continue with the next available
todo by starting its strategy confidence checkpoint.

A completed milestone is not a valid reason to yield while another unblocked
todo can begin. The loop should only yield with unfinished work when continuing
now is unsafe, impossible, or explicitly requires user input/review.

## Stop conditions

Stop only when one of these is true:

- Complete: all done criteria are satisfied and validation passes. Write `.opencode-goal/DONE` with a concise final summary.
- Blocked: a missing decision, credential, external dependency, destructive-risk approval, or unavailable environment prevents progress. Write `.opencode-goal/BLOCKED` with the exact blocker and the smallest user action needed.
- More work remains and yielding is necessary: leave unfinished todos and a clear next step in `.opencode-goal/progress.md`, then respond concisely. This stop condition is only allowed when auto-continue is disabled, context/time budget requires yielding, validation cannot be completed now, or the next step needs user input/review. Do not use this after a validated milestone when auto-continue is enabled and another unblocked todo can start immediately.

## Guardrails

- Do not expand scope beyond the goal.
- Do not accept hacks, brittle shortcuts, or knowingly suboptimal architecture.
- Do not declare completion based only on superficial progress.
- Do not commit, push, delete large directories, or run destructive commands unless the user explicitly requested it.
- Prefer boring, reversible changes.
- Keep the repository as the source of truth: important state must be written to files, not only chat.
