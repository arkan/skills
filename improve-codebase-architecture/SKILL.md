---
name: improve-codebase-architecture
description: Find deepening opportunities in a codebase, informed by the project's domain language and recorded architectural decisions. Use when the user wants to improve architecture, find refactoring opportunities, consolidate tightly-coupled modules, or make a codebase more testable and AI-navigable.
---

# Improve Codebase Architecture

Surface architectural friction and propose **deepening opportunities** — refactors that turn shallow modules into deep ones. The aim is testability and AI-navigability.

## Glossary

Use these terms exactly in every suggestion. Consistent language is the point — don't drift into "component," "service," "API," or "boundary." Full definitions in [LANGUAGE.md](LANGUAGE.md).

- **Module** — anything with an interface and an implementation (function, class, package, slice).
- **Interface** — everything a caller must know to use the module: types, invariants, error modes, ordering, config. Not just the type signature.
- **Implementation** — the code inside.
- **Depth** — leverage at the interface: a lot of behaviour behind a small interface. **Deep** = high leverage. **Shallow** = interface nearly as complex as the implementation.
- **Seam** — where an interface lives; a place behaviour can be altered without editing in place. (Use this, not "boundary.")
- **Adapter** — a concrete thing satisfying an interface at a seam.
- **Leverage** — what callers get from depth.
- **Locality** — what maintainers get from depth: change, bugs, knowledge concentrated in one place.

Key principles (see [LANGUAGE.md](LANGUAGE.md) for the full list):

- **Deletion test**: imagine deleting the module. If complexity vanishes, it was a pass-through. If complexity reappears across N callers, it was earning its keep.
- **The interface is the test surface.**
- **One adapter = hypothetical seam. Two adapters = real seam.**

This skill is _informed_ by the project's domain model and recorded decisions. The domain language gives names to good seams; recorded decisions document seams that should not be re-litigated. See [CONTEXT-FORMAT.md](../domain-model/CONTEXT-FORMAT.md) and [ADR-FORMAT.md](../domain-model/ADR-FORMAT.md) for the canonical formats.

## Adapt to your repo

Different projects organize domain knowledge and architectural decisions differently. Before doing anything else, build a **mapping table** for the current repo by scanning a small set of conventional locations.

### Concepts to locate

| Concept | What it is | Why this skill needs it |
|---------|-----------|--------------------------|
| **Domain glossary** | Authoritative list of business terms (Order, Subscription, Publisher, …). | Names every deepened module gets. Drives the vocabulary in candidate write-ups. |
| **Architecture entry point** | A high-level orientation file (overview, substrate, README) explaining how the codebase is laid out. | Lets the skill prioritise where to explore. |
| **Architecture decisions (ADRs)** | Files recording load-bearing technical decisions. | Skill must not re-litigate them. Conflicts are surfaced explicitly. |
| **Anti-patterns / forbidden patterns** | Patterns the project bans. | A candidate proposing a banned pattern is a bug, not a suggestion. |
| **Boundaries / ownership** | Files declaring what may not be modified (legacy code, generated code, security-sensitive paths). | Skill must not propose deepenings inside no-touch zones. |
| **Architecture patterns / layering** | Layering rules, dependency direction, module structure. | Frames what a "good" deepening looks like for this repo. |
| **Plans directory** | Where multi-file refactoring plans get written. | Where the skill writes follow-up plans for accepted candidates. |

### Discovery procedure

Run this once per repo, then cache the mapping in your working memory for the conversation. Look for the following, in order:

1. **Glossary** — try `CONTEXT.md`, `.context/glossary.md`, `docs/glossary.md`, `domain-model/CONTEXT.md`. First hit wins.
2. **Architecture entry point** — try `.context/substrate.md`, `docs/architecture.md`, `ARCHITECTURE.md`, `.context/architecture/overview.md`.
3. **ADRs** — try `docs/adr/`, `.context/decisions/`, `docs/decisions/`, `adr/`. Read the README/index of the directory if present.
4. **Anti-patterns** — try `.context/anti-patterns.md`, `docs/anti-patterns.md`. Often inlined in a CONTRIBUTING or AGENTS file.
5. **Boundaries** — try `.context/boundaries.md`, `CODEOWNERS`, top-level `AGENTS.md` / `CLAUDE.md` for "do not modify" sections.
6. **Architecture patterns** — try `.context/architecture/patterns.md`, `docs/patterns.md`, top-level architecture doc.
7. **Plans directory** — try `docs/plans/`, `docs/rfcs/`, `.planning/`. If none exists, default to `docs/plans/YYYY-MM-DD-{slug}.md`.

If a concept isn't found, proceed silently. Don't flag absences upfront, and don't propose creating these structures unless a side effect in step 3 below makes one genuinely necessary.

### Pre-declared mappings

A repo can short-circuit the discovery procedure by declaring its mapping table directly in `CLAUDE.md` / `AGENTS.md` (or any always-loaded instructions file). When such a table is present, treat it as authoritative and skip steps 1–7 above.

## Process

### 1. Explore

Build the mapping table from the previous section, then read the located files in this order:

1. The **architecture entry point** — gives orientation.
2. The **glossary** — provides the vocabulary for every candidate.
3. The **architecture patterns** — frames what good seams look like here.
4. The **ADR index** — skim titles and statuses; read full ADRs only when a candidate touches their territory.
5. The **boundaries** — note no-touch zones so candidates never propose work inside them.

If any of these files don't exist, proceed silently — don't flag their absence or suggest creating them upfront.

Then use the Agent tool with `subagent_type=Explore` to walk the codebase. Don't follow rigid heuristics — explore organically and note where you experience friction:

- Where does understanding one concept require bouncing between many small modules?
- Where are modules **shallow** — interface nearly as complex as the implementation?
- Where have pure functions been extracted just for testability, but the real bugs hide in how they're called (no **locality**)?
- Where do tightly-coupled modules leak across their seams?
- Which parts of the codebase are untested, or hard to test through their current interface?

Apply the **deletion test** to anything you suspect is shallow: would deleting it concentrate complexity, or just move it? A "yes, concentrates" is the signal you want.

### 2. Present candidates

Present a numbered list of deepening opportunities. For each candidate:

- **Files** — which files/modules are involved
- **Problem** — why the current architecture is causing friction
- **Solution** — plain English description of what would change
- **Benefits** — explained in terms of locality and leverage, and also in how tests would improve

**Use the project glossary vocabulary for the domain, and [LANGUAGE.md](LANGUAGE.md) vocabulary for the architecture.** If the glossary defines "Subscription," talk about "the Subscription intake module" — not "the FooBarHandler," and not "the Subscription service."

**Respect boundaries**: never propose a candidate that requires modifying paths the boundaries file marks read-only. If the friction lives there, name it but flag it as out-of-scope.

**Respect anti-patterns**: never propose a candidate whose solution matches a documented anti-pattern. If the current code _is_ an anti-pattern, the candidate is reframed as removing it.

**ADR conflicts**: if a candidate contradicts an existing ADR, only surface it when the friction is real enough to warrant revisiting the ADR. Mark it clearly (e.g. _"contradicts ADR-007 — but worth reopening because…"_). Don't list every theoretical refactor an ADR forbids.

Do NOT propose interfaces yet. Ask the user: "Which of these would you like to explore?"

### 3. Grilling loop

Once the user picks a candidate, drop into a grilling conversation. Walk the design tree with them — constraints, dependencies, the shape of the deepened module, what sits behind the seam, what tests survive.

Side effects happen inline as decisions crystallize. Use the paths from your mapping table:

- **Naming a deepened module after a concept not in the glossary?** Add the term to the glossary file from the mapping table. Match the existing format (table row, definition list, etc.) — same discipline as `/domain-model` (see [CONTEXT-FORMAT.md](../domain-model/CONTEXT-FORMAT.md)). Create the file lazily if it doesn't exist.
- **Sharpening a fuzzy term during the conversation?** Update the glossary file right there.
- **User rejects the candidate with a load-bearing reason?** Offer an ADR, framed as: _"Want me to record this as an ADR so future architecture reviews don't re-suggest it?"_ Only offer when the reason would actually be needed by a future explorer to avoid re-suggesting the same thing — skip ephemeral reasons ("not worth it right now") and self-evident ones. Write the ADR into the ADR directory from the mapping table, following the existing numbering scheme (3-digit, 4-digit, etc.) and updating the directory's README/index if one exists. See [ADR-FORMAT.md](../domain-model/ADR-FORMAT.md).
- **Candidate accepted and ready for execution?** Write a follow-up plan into the plans directory from the mapping table, using the directory's existing filename convention (e.g. `docs/plans/YYYY-MM-DD-{slug}.md`).
- **Want to explore alternative interfaces for the deepened module?** See [INTERFACE-DESIGN.md](INTERFACE-DESIGN.md).

**Documentation language**: match the project. If the existing glossary, ADRs, and plans are in French (or any other language), write your additions in the same language. Architectural vocabulary from [LANGUAGE.md](LANGUAGE.md) (module, seam, adapter, leverage, locality) stays in English regardless — those are project-neutral terms.
