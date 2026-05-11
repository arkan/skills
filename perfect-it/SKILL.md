---
name: perfect-it
description: Stress-tests strategies, plans, designs, architectures, and uncertain answers until every material loophole is fixed or explicitly blocked. Use when the user says /perfect-it, "are you 100% confident", "perfect it", asks to find loopholes, asks for a higher-confidence strategy, or when the agent is not fully confident in its own strategy or answer.
---

# Perfect It

## Quick start

When invoked, answer this question before proceeding:

> Am I 100% confident in this strategy?

If the answer is not strictly yes, run the loophole loop below. Do not claim 100% confidence unless the confidence gate passes.

## Core rule

The target is strict 100% confidence. This does **not** permit fake certainty. If 100% cannot be reached with available evidence, say `NOT 100% CONFIDENT`, list the blockers, and specify the evidence or work required to reach 100%.

## Loophole loop

Repeat until the confidence gate passes or a blocker remains:

1. **Restate the strategy**
   - Define the exact strategy, scope, success criteria, non-goals, and failure modes.
   - Convert vague claims into falsifiable checks.

2. **Find loopholes adversarially**
   - Enumerate ways the strategy could fail: hidden assumptions, edge cases, missing requirements, security/privacy risks, data integrity issues, operational risks, UX risks, dependency/version risks, cost/performance risks, and rollback risks.
   - For code or repo work, inspect the relevant files instead of relying on memory.
   - For library/API claims, verify against authoritative current docs when behavior matters.

3. **Fix properly**
   - For each material loophole, change the strategy so the loophole is impossible, detected mechanically, or explicitly accepted with rationale.
   - Prefer simple, enforceable fixes over documentation-only promises.

4. **Verify with evidence**
   - Run the strongest available checks: tests, typechecks, linters, code search, docs lookup, reproduction, invariants, examples, or peer/subagent review.
   - Record the evidence. If a check cannot run, record why and treat it as a confidence blocker unless immaterial.

5. **Re-score confidence**
   - If any material loophole, unverified critical assumption, or unresolved contradiction remains, confidence is not 100%; loop again.

## Confidence gate

Only output `100% CONFIDENT` when all are true:

- Success criteria are explicit and testable.
- All material loopholes found so far are fixed, made impossible, or proven irrelevant.
- Critical assumptions are backed by evidence, not vibes.
- Verification has run successfully, or skipped checks are proven immaterial.
- The revised strategy is simpler or at least not more fragile than the original.

Otherwise output `NOT 100% CONFIDENT` and the shortest path to reach 100%.

## Output format

Use `REPORT_TEMPLATE.md` for substantial work. For short answers, use:

```md
Confidence: 100% CONFIDENT | NOT 100% CONFIDENT

Strategy:
- ...

Loopholes found:
- ...

Fixes applied:
- ...

Evidence:
- ...

Remaining blockers:
- None | ...

Final strategy:
- ...
```

## Validation

For report files, run:

```bash
python ~/.agents/skills/perfect-it/scripts/check-report.py path/to/report.md
```
