---
name: do
description: "Autonomous execution of a plan, PRD, or context document. Decomposes the input into discrete tasks, dispatches each to a subagent (using TDD workflow for testable code changes, normal execution for config/docs), then runs an automated code review via Codex and iterates fixes until the review passes (up to 5 review cycles). Supports `--skip-review` (no Codex review) and `--only-review` (review + fix loop on the user's existing uncommitted changes, no implementation). Use this skill whenever the user says '/do', asks to 'implement the plan', 'execute the PRD', 'ship this spec', 'run the plan autonomously', wants a plan/PRD/issue translated into working code without hand-holding, or hands over a docs/plans/*.md file and asks you to build it. Also use when the user says something like 'take this and build it', 'do everything in this document', or 'make it happen' while referencing a planning document, or 'just review what I have' / 'run the review loop on my WIP' (use `--only-review`). Trigger even if the user doesn't explicitly say 'do' — the signal is 'I have a spec, go implement it end-to-end with review' or 'run my existing code through the review loop'."
argument-hint: "[docs/plans/<spec>.md | \"inline instruction\"] [--skip-review | --only-review]"
---

# /do — Autonomous plan-to-code executor

## Purpose

Turn a specification (plan, PRD, context, or inline instruction) into merged code, validated by an independent review loop. The user hands over intent; `/do` handles decomposition, implementation, review, and iteration.

## Philosophy

- **The main agent orchestrates; subagents do the work.** Keep the main context clean for coordination and review — delegate implementation to subagents so their heavy token usage doesn't pollute the orchestrator's context.
- **TDD when it pays off, not as dogma.** Testable behavior (services, hooks, pricing, validators, API endpoints, React components with logic) gets the `/tdd` treatment. Config, pure styles, docs, and trivial renames don't — forcing TDD there wastes time.
- **Review is the default, not a suggestion.** An autonomous run without an independent review is a loaded gun. Codex review is the circuit breaker that catches the slop the implementer missed. The only way to disable it is the explicit `--skip-review` flag — that's a deliberate, recorded choice by the human, not a quiet default the orchestrator can flip on its own.
- **Every iteration is a commit.** Before each review, commit the work as a checkpoint. This gives the human a trivial rollback path (`git reset HEAD~N`), a clear audit trail of what changed at each cycle, and makes review oscillation visible in `git log`. Commits are local-only — never pushed.
- **Bounded iteration.** Up to 5 review cycles. If it still fails after 5, something structural is wrong and a human needs to look at it — don't spin forever.

## Input handling

The skill receives a single argument string. First, **extract any flags**, then resolve what remains as the spec.

**Flags** (parsed and removed from the argument before spec resolution):

| Flag | Effect |
|---|---|
| `--skip-review` | Skip Phase 3 (Codex review) and Phase 4 (fix loop). Phase 2 runs as usual, the checkpoint commit happens once, and Phase 5 jumps straight to the final report. Use when the human will review manually, when iterating on a tiny change where Codex is overkill, or when Codex is unavailable. |
| `--only-review` | **Skip the implementation.** Phase 1 (decompose) and Phase 2 (execute tasks) are bypassed — `/do` runs review + fix loop only, on top of what's already in the working tree. Phase 0 inverts: a dirty tree is *required* (that's what gets reviewed), a clean tree is an error. The first checkpoint commit captures the user's pre-existing WIP as "iteration 1" so the fix loop has a baseline. Use when you've implemented something yourself and want `/do`'s review loop as a safety net, or to re-run review on a prior run's output without redoing the work. Incompatible with `--skip-review` (reject the combination — it would do nothing). |

After stripping flags, resolve the remaining argument:

1. **If it looks like a file path (contains `/` or ends with `.md`/`.txt`) AND the file exists** → read it. This is the "spec" mode.
2. **Otherwise** → treat it as inline context. This is the "quick instruction" mode.
3. **If it's empty AND `--only-review` is not set** → ask the user what they want to execute. Don't guess.
4. **If it's empty AND `--only-review` is set** → that's valid. Codex will review the diff on its own merits without a spec to compare against.

Store the resolved spec as `SPEC_CONTENT` for downstream steps (may be empty when `--only-review`). If the input was a file, also remember `SPEC_PATH` so subagents can re-read it themselves instead of receiving the full text. Store the parsed flags as `FLAGS` (e.g., `SKIP_REVIEW = true|false`, `ONLY_REVIEW = true|false`).

**Mutual exclusion.** If both `--skip-review` and `--only-review` are set, reject the combination up front — the two together would skip everything and do nothing. Stop with a short message asking the user to pick one.

Confirm the parsed flags back to the user in the task-breakdown (or review-only) message so they can catch a typo (e.g., `--skipreview` or `--only-revu` silently treated as part of the spec) before execution starts.

## Workflow

### Phase 0 — Pre-flight check

Before anything else, verify the working tree is in a state where autonomous commits won't mix with the human's in-progress work:

```bash
git status --porcelain
```

**Default mode (without `--only-review`):**

- **Clean tree** → proceed.
- **Dirty tree** (uncommitted changes, untracked non-ignored files) → stop and surface to the user:
  > Your working tree has uncommitted changes. `/do` will commit at each iteration — mixing with your WIP is risky. Do you prefer: (a) commit/stash manually first, (b) run anyway and accept that the first commit will include your WIP, (c) cancel?

**`--only-review` mode (logic inverted):**

- **Dirty tree** → proceed. The uncommitted changes *are* the implementation to review — Phase 2.5 will commit them as the iteration-1 baseline before Codex runs.
- **Clean tree** → stop. There's nothing to review. Surface to the user:
  > `--only-review` expects uncommitted changes to review, but your working tree is clean. You may have meant: (a) review a commit that's already made — in that case, `git reset --soft HEAD~1` to move the changes back to the working tree and re-run, (b) review a PR — use `/deep-review` or `gh pr diff` + `/codex`, (c) cancel.

Also record the starting commit SHA (`git rev-parse HEAD`) as `BASE_SHA` — used later for the final report and for computing `git log BASE_SHA..HEAD` to show the iteration trail. In `--only-review` mode, `BASE_SHA` is the commit *before* the user's WIP gets captured as iteration 1, so the trail still reads naturally.

### Phase 1 — Decompose into tasks

**Skip condition.** If `ONLY_REVIEW` was set via `--only-review`, log a one-liner and jump straight to Phase 2.5 (the user's uncommitted WIP becomes the "iteration 1" baseline):

```
[do] --only-review active → Phase 1 (decomposition) and Phase 2 (execution) skipped.
Code to review = your uncommitted working-tree changes.
```

Otherwise:

Read the spec and extract discrete, actionable tasks. Good task sources, in order of preference:

1. A "Fichiers à toucher" / "Files to modify" / "Modules touchés" section → one task per logical grouping (backend / frontend / tests).
2. An "Implementation Decisions" section with numbered or bulleted steps.
3. User stories that each require concrete code changes.
4. If none of the above, ask the model to identify 2–8 tasks by skimming the spec.

For each task, record:
- A short **title** (≤ 10 words).
- A one-paragraph **description** grounded in the spec.
- A **kind**: `tdd` or `normal` (see heuristic below).
- The **files** it's expected to touch (from spec or inferred).
- Any **dependencies** on earlier tasks (e.g., "needs the Go domain fields from task 1").

**TDD vs normal heuristic:**

| Signal | Kind |
|---|---|
| Touches Go services/domain/repository with business logic | `tdd` |
| Touches frontend components with state/logic or hooks | `tdd` |
| Adds/changes API endpoints or handlers | `tdd` |
| Touches pricing, validation, calculation, parsing | `tdd` |
| Pure styling (CSS/Tailwind) | `normal` |
| Config files, routes declaration, translations strings | `normal` |
| Documentation, comments, README changes | `normal` |
| Trivial renames or type-only tweaks | `normal` |
| Migration/SQL schema (test via integration or manual) | `normal` |
| Spec explicitly tags a task `[TDD]` or `[NORMAL]` | use the tag |

When in genuine doubt → prefer `tdd` if the task has observable behavior that would regress silently otherwise; prefer `normal` if adding tests would just mirror the implementation.

Present the task breakdown to the user **once** before execution and get a go/no-go:

```
Here are the N tasks extracted:
1. [TDD] <title> — <files>
2. [NORMAL] <title> — <files>
…
Start sequential execution? (yes / adjust / cancel)
```

Skip this confirmation only if the user explicitly said "full auto" or "don't ask" in their invocation.

### Phase 2 — Execute tasks sequentially

**Skip condition.** If `ONLY_REVIEW` was set, this phase is already bypassed by the Phase 1 short-circuit — jump to Phase 2.5.

Use `TaskCreate` to track each task. Mark `in_progress` when starting, `completed` when the subagent returns successfully. If a task fails, mark it `blocked` and surface the failure to the user before continuing.

For each task, spawn **one** subagent via the `Agent` tool (`subagent_type: general-purpose`), waiting for it to finish before the next:

**TDD subagent prompt template:**

```
You are implementing ONE task from a larger spec. Follow the /tdd workflow
(read .claude/skills/tdd/SKILL.md first) — red/green cycles, one test at
a time, tests focus on observable behavior through public interfaces.

Spec context:
- <if SPEC_PATH set> Read the full spec at <SPEC_PATH>.
- <else> <paste SPEC_CONTENT>.

Your scope (narrow — do NOT touch anything else):
- Title: <task title>
- Description: <task description>
- Files expected: <files>
- Dependencies resolved by earlier tasks: <summary of what earlier tasks produced>

Constraints (from project CLAUDE.md and .context/ rules) you must respect:
- Code, comments, error messages, and identifiers all in English.
- Banned terminology per .context/glossary.md — respect the substitutions
  (read the file if unsure which substitutions apply).
- Handler → Service → Repository architecture.

When done, report back:
1. Which files you touched (paths).
2. Which tests you added and their names.
3. Any spec ambiguity you resolved and how.
4. Any follow-up the next task will need from you.

Do NOT commit. Do NOT open a PR. Just implement and test.
```

**Normal subagent prompt template:** same but drop the `/tdd` reference and instead say:

```
This task is not suited for TDD (it's <why — e.g., pure config / docs /
styling>). Implement directly, verify manually where useful, and keep
the change as surgical as possible.
```

After each subagent returns, spend a beat to sanity-check its summary: did it touch files outside the expected scope? Did it skip the tests it claimed to write? If yes, note it for the review phase.

### Phase 2.5 — Checkpoint commit

Once **all** tasks for the current iteration are done (either the initial Phase 2, or a fix pass from Phase 4), create a checkpoint commit **before** running the review. This is what lets the human roll back one iteration with a single `git reset`, and what makes `git log` a readable audit trail of the autonomous run.

**`--only-review` note.** In this mode, iteration 1 is not "our implementation" — it's the user's pre-existing uncommitted changes. Commit them with the message `"[do] iteration 1/5: baseline (user-provided implementation captured for review)"`. From iteration 2 onwards, the message format is the same as default mode (`fix <N-1 findings>`).

Sequence:

```bash
# Add everything produced by the subagents. Using 'git add -A' is
# acceptable here because Phase 0 verified the tree was clean (or the
# user explicitly opted to include their WIP). Subagents are scoped;
# unrelated files should not appear.
git add -A

# Guard: if nothing staged, skip the commit and log it. This can happen
# if a fix subagent correctly rejected all Codex findings as false
# positives and made no changes.
if git diff --cached --quiet; then
  echo "[do] no changes to commit — skipping checkpoint for iteration N"
else
  git commit -m "$(cat <<'EOF'
[do] iteration N/5: <short summary — "initial implementation" on iter 1, or "fix <N-1 findings>" on fix iters>

Spec: <SPEC_PATH or one-line summary>
Iteration: <N>/5
Tasks: <count completed>
Tests touched: <count>

🤖 Generated with /do skill
EOF
  )"
fi
```

Rules:
- **Never** use `--no-verify`. If pre-commit hooks fail, that's a real signal — stop the loop, surface the failure to the user verbatim, and let them decide. Bypassing hooks to keep the automation moving is exactly how we'd ship broken code.
- **Never** push. Commits stay local. The human merges to `main` (or wherever) manually after the final report.
- **Never** amend. Each iteration is its own immutable commit — that's the whole point of the trail.
- Capture the commit SHA (`git rev-parse HEAD`) and append it to an in-memory `ITERATION_SHAS` list. Used in the final report.

If `git commit` fails, diagnose the cause and handle it differently depending on what went wrong:

**A. Pre-commit hook rejection** (terminology violation, lint error, format issue, etc.)

Most hook failures are deterministic and mechanically fixable — treat them like another mini-review loop with its own small budget, separate from the 5-iteration Phase 3 cap.

Budget: **2 auto-fix attempts** per checkpoint commit (so 3 total commit attempts max: initial + 2 fixes).

For each attempt:

1. Capture the hook's full stderr/stdout verbatim.
2. Spawn a dedicated fix subagent with this prompt:

   ```
   The pre-commit hook just blocked our checkpoint commit for iteration N.
   Your only job is to make the hook pass.

   Hook output (verbatim):
   <paste stderr>

   Rules:
   - Read the hook output carefully. Most of these hooks include the
     remediation inline (e.g., "rule X: use Y instead of Z. Ref: .context/…").
     Follow it literally.
   - Stay within scope. Don't refactor unrelated code, don't change the
     architectural decisions of this iteration. Only touch what the hook
     flags.
   - If the hook complains about tests failing, investigate before
     patching — a failing test can be a real bug in the prior subagent's
     work. Fix the root cause, not the symptom.
   - Do NOT commit yourself. Just apply the minimal edits.
   - When done, report: (1) what the hook flagged, (2) what you changed,
     (3) why you believe the hook will now pass, (4) anything suspicious
     you noticed but did not touch.
   ```

3. Re-run `git add -A && git commit -m "<same checkpoint message>"`.
4. If the commit now succeeds → proceed to Phase 3. Capture the SHA.
5. If it fails again → retry (attempt 2). Use the **new** hook output.
6. If it fails after 2 fix attempts → abort the loop (fall through to case B).

Explicitly **NOT** acceptable during auto-fix:
- Bypassing the hook (`--no-verify`, `--no-gpg-sign`).
- Removing or disabling the hook itself (editing `.git/hooks/`, `settings.json`, `.husky/`, etc.).
- Deleting the test/file the hook is validating to "make it stop complaining".
- Mass reformatting unrelated files to hide a real failure inside the noise.

If an auto-fix subagent returns a report that suggests doing any of those — stop, don't commit, surface to the human.

**B. Unrecoverable commit failure** (auto-fix budget exhausted, merge conflict, missing files, or any non-hook error)

Abort the loop and report to the user:

```
❌ Commit for iteration N blocked.

Cause: <pre-commit hook after 2 fix attempts | merge conflict | other>

Last output:
<paste stderr>

History of commits already successful (can be kept or rolled back):
<git log --oneline BASE_SHA..HEAD>

The skill stops here. Options:
(a) inspect the offending files, fix manually, and re-run
    `/do` indicating that we're resuming at iteration N,
(b) rollback to the previous iteration: git reset --hard <SHA iteration N-1>,
(c) full rollback: git reset --hard <BASE_SHA>.
```

### Phase 3 — Independent review via Codex

**Skip condition.** If `SKIP_REVIEW` was set via `--skip-review`, log a one-liner and jump to Phase 5:

```
[do] --skip-review active → Phase 3 (Codex review) and Phase 4 (fix loop) skipped.
Review responsibility is on the human.
```

Otherwise, once **all** tasks are completed (or, in `--only-review` mode, once the baseline commit has captured the user's WIP; or after each attempt in the review loop), run Codex as an independent reviewer against the working-tree diff.

**No-spec case (`--only-review` without a spec argument).** Swap the `<paste SPEC_CONTENT or reference SPEC_PATH>` block in the Codex prompt for: *"No spec was provided. Review the diff on its own merits — correctness, adherence to project constraints, obvious bugs, regressions, and scope hygiene."* Drop sub-bullet #1 ("Verify the implementation matches the spec's intent and decisions.") from the review checklist since there's nothing to verify against.

**Command template** (bake in the `hooks=[]` workaround — Codex's TOML config parser chokes on JSON hooks files):

```bash
codex exec \
  -c 'hooks=[]' \
  --dangerously-bypass-approvals-and-sandbox \
  -m gpt-5.4 \
  -c model_reasoning_effort=xhigh \
  "Context: <one-paragraph project context from CLAUDE.md>.

Task: Review the staged + unstaged changes produced by an autonomous
implementation of the following spec:

<paste SPEC_CONTENT or reference SPEC_PATH>

The diff is visible via 'git diff' and 'git diff --cached'. Please:

1. Verify the implementation matches the spec's intent and decisions.
2. Check for bugs, wrong column names, wrong API shapes, broken joins,
   missing branches, obvious regressions.
3. Respect project constraints: no Informix schema changes, terminology
   rules from .context/glossary.md, English code + comments + identifiers,
   Handler → Service → Repository.
4. Be EXHAUSTIVE — go through every changed hunk in every file in the diff
   and report every distinct issue you find. Do not stop after the first
   2–3 findings, do not return a 'representative sample', do not collapse
   multiple occurrences of the same problem into a single bullet (list
   each file/line where it occurs). Minor nits, style issues, and dead
   code count too — list them as 'minor'. The goal is full coverage of
   the diff, not a curated highlights reel.
5. Return a STRUCTURED verdict at the end of your output in this exact format:

<verdict>
status: APPROVED | NEEDS_FIXES
summary: <one-line summary>
issues:
- severity: blocker | major | minor
  file: <path>
  line: <number or range>
  description: <what's wrong>
  fix: <concrete suggested change>
- …
</verdict>

The 'issues' list MUST contain every problem you found across the entire
diff — there is no upper bound. If you find 20 issues, list 20. If you
find zero, return an empty list and status APPROVED.

Only emit NEEDS_FIXES if there are blocker or major issues. Minor nits
alone should return APPROVED with the issues listed as recommendations."
```

Run this via `Bash` (long-running — use `run_in_background: true` and poll the output file, or a foreground call with a 5-minute timeout). Capture the full transcript. Extract the `<verdict>…</verdict>` block.

Parse the verdict:
- `status: APPROVED` → exit the loop with success.
- `status: NEEDS_FIXES` → continue to Phase 4.
- No parseable verdict → treat as `NEEDS_FIXES` with the full transcript as the finding, and flag the parser failure to the user.

### Phase 4 — Incremental fixes and re-review (bounded loop)

If the verdict is `NEEDS_FIXES`, spawn **one** fix subagent with a focused prompt. Do **not** wipe the work. Do **not** re-run Phase 2 from scratch. Additive fixes only.

**Fix subagent prompt:**

```
A prior implementation of this spec was reviewed by Codex and found to
have issues. Your job is to fix ONLY the issues listed below, without
regressing the rest of the work.

Spec: <SPEC_PATH or inline>
Current review iteration: <N of 5>

Codex findings to address (in priority order):
<paste the issues list from the verdict>

Constraints:
- Same stack conventions as before (English code/comments, project terminology
  rules from .context/glossary.md, architecture layers).
- Do not rewrite untouched files.
- If you fix behavior, update or add tests so the fix is locked in.
- If a finding is wrong (Codex misread the code), say so explicitly in
  your report instead of forcing a bad fix.

When done, report:
1. Which findings you addressed and how.
2. Which findings you rejected and why.
3. Tests added or updated.
```

After the fix subagent returns, loop back to **Phase 2.5** (checkpoint commit) and then **Phase 3** (re-run review).

Track the iteration count. The cap is **5 full Phase 3 runs total** — which means at most 5 checkpoint commits on top of `BASE_SHA` (initial implementation + up to 4 fix iterations).

### Phase 5 — Final report

Always include the iteration trail so the human can navigate the history:

```bash
git log --oneline <BASE_SHA>..HEAD
```

**On success** (verdict `APPROVED` within 5 iterations, OR `--skip-review` was set and the implementation completed):

```
✅ Execution completed successfully.

Spec: <SPEC_PATH or summary or "no spec (--only-review)">
Mode: <normal | --skip-review | --only-review>
Review: <N/5 Codex iterations | "skipped (--skip-review)">
Tasks completed: <X | "—" if --only-review>
Tests added: <Y>

Commit history (from base to HEAD):
<git log --oneline BASE_SHA..HEAD>

Possible next steps:
- Re-read the global diff: git diff <BASE_SHA>..HEAD
- Squash iterations into a single commit: git reset --soft <BASE_SHA> && git commit
- Open a PR as-is: the commits tell the story of the review
<if --skip-review>
- ⚠️ No automatic review was performed. Remember to go through the diff
  manually before merging (or re-run `/do` without `--skip-review` on the same
  spec if you want Codex to pass over it after the fact).
</if>
<if --only-review>
- Commit 1 captures your original implementation. If you want to merge it with
  Codex's fixes into a single commit: git reset --soft <BASE_SHA> && git commit.
</if>
```

**On failure** (still `NEEDS_FIXES` after the 5th review):

```
❌ Failure after 5 review iterations.

Last Codex verdict:
<paste the last verdict block>

Persistent issues:
<list of issues that never got resolved>

Commit history (from base to HEAD):
<git log --oneline BASE_SHA..HEAD>

Options:
- Manual resume on current HEAD (the last commit contains the best state).
- Go back to an earlier iteration: git reset --hard <SHA of a previous iteration>.
- Cancel everything: git reset --hard <BASE_SHA>.
```

No auto-push. The human owns the merge decision and chooses whether to squash, keep the iteration history, or rollback.

## Safety rails

- **Checkpoint commits are local-only.** `/do` commits between iterations on purpose (rollback + audit trail). It **never** pushes. Remote operations (`git push`, `git push --force`, `gh pr create`, etc.) are strictly out of scope.
- **Never** run destructive git ops (`git reset --hard`, `git checkout --`, `git clean -fd`) inside the loop. Each iteration is additive. If the user wants a clean slate, they'll do it themselves using the SHAs reported at the end.
- **Never** amend or rebase existing commits during the run — each iteration must stay as its own visible commit so the trail is preservable.
- **Never** skip or disable hooks (`--no-verify`, `--no-gpg-sign`, editing `.git/hooks/`, touching `.husky/`, toggling settings) — if a hook fails, try up to 2 automated fix attempts (see Phase 2.5 case A) and otherwise stop and report. A hook that fires is the author of the codebase speaking; listen.
- **Never** loop beyond 5 Codex runs, even if "just one more would do it".
- **Never** flip `--skip-review` on the user's behalf. The flag is opt-in only — even if Codex is failing, slow, or returning useless output, the right move is to stop and surface the problem, not to silently route around the safety net.
- **Never** touch files outside the scope of each subagent's task. Scope creep is caught in review; in aggregate it would pollute the diff and dilute the commits' audit value.
- **Always** surface subagent failures to the user immediately — do not retry silently.
- **Always** keep the human in the loop for the initial task-breakdown confirmation, unless they explicitly opted out.
- **Always** leave a readable trail. The point of per-iteration commits is that someone unfamiliar with the run can reconstruct what happened from `git log` alone.

## Failure modes to watch for

- **Codex config error** (`invalid type: map, expected a sequence in hooks`) → the `-c 'hooks=[]'` override handles it; if it still fails, ask the user to check `~/.codex/config.toml`.
- **Subagent scope creep** (touches files outside its task) → flag in the review phase, Codex usually catches it.
- **Review loop oscillation** (iteration N fixes A but breaks B, iteration N+1 reverses it) → detect by comparing issue lists across iterations; if the same issues bounce back, stop early and report it honestly instead of burning the budget.
- **Spec ambiguity** → a subagent should surface ambiguity in its report rather than guess silently. The orchestrator must propagate that ambiguity to the user, not suppress it.

## Related skills

- `/tdd` — invoked by subagents for testable tasks.
- `/codex` — same CLI tool, invoked here as an independent reviewer.
- `/grill-me`, `/write-a-prd` — upstream skills that produce the specs `/do` consumes.
- `/gsd:quick`, `/gsd:execute-phase` — alternative manual workflow when the user wants more control.
