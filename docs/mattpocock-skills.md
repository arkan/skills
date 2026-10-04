# Matt Pocock skills

This collection imports 20 complete skill folders from
[v1.3.1](https://github.com/mattpocock/skills/releases/tag/v1.3.1), commit
[`24fe0ef`](https://github.com/mattpocock/skills/commit/24fe0ef7737efae15c87225755e9f6f5965e4888).
The source paths and version pin live in [`update.sh`](../update.sh).

Each imported folder includes its supporting documents, scripts, templates, and
`agents/openai.yaml`. The skill contents match that upstream snapshot; runtime
compatibility guidance lives here rather than changing the vendored instructions.
The upstream MIT notice is preserved in
[`licenses/mattpocock-skills-LICENSE`](../licenses/mattpocock-skills-LICENSE), and
the PR skill retains its own [`CREDITS.md`](../skills/pr/CREDITS.md).

## Changes in this migration

Thirteen existing skills are updated under their original names. Three use new
canonical names:

| Previous name | Current name |
|---|---|
| `to-prd` | `to-spec` |
| `to-issues` | `to-tickets` |
| `writing-great-skills` | `writing-for-agents` |

Update callers and installed copies to use the new names. The old active folders
are removed, without aliases.

Four skills are added:

- `setup-matt-pocock-skills`: configure the project's tracker, labels, and domain docs.
- `code-review`: review Standards and Spec through independent agents.
- `pr`: write a PR body with a visual summary, evidence, and merge impact.
- `retro`: propose improvements to the agent's environment after a session.

`resolving-merge-conflicts` and `edit-article` are removed because upstream retired
them. There is no designated replacement for either skill. Existing archived
skills remain archived. Optional workflows such as `implement-spec` and
`wayfinder`, and upstream beta/Misc skills, are not imported in this migration.

## Domain glossary migration

The updated skills consume `GLOSSARY.md` and, when several domain contexts exist,
`GLOSSARY-MAP.md`. Projects using the previous domain-document names need to:

1. Inspect `CONTEXT.md` and `CONTEXT-MAP.md` to confirm they are domain glossaries.
2. Rename those domain files to the corresponding `GLOSSARY` names. If a new-name
   file already exists, reconcile its contents before renaming.
3. Update map links, steering-file pointers, and other references to the renamed
   files. Keep ADRs in their existing locations.

An unrelated document named `CONTEXT.md` should retain its name. This library
update does not modify downstream projects or their installed skill copies.
The new domain template is
[`GLOSSARY-FORMAT.md`](../skills/domain-modeling/GLOSSARY-FORMAT.md).

## Invocation and runtime compatibility

User-invoked skills carry `disable-model-invocation: true` in `SKILL.md` and
`policy.allow_implicit_invocation: false` in `agents/openai.yaml`. Model-invoked
skills use the default implicit policy. In particular, `writing-for-agents` is
model-invoked. Setup and retrospective workflows remain explicit user choices.

When an upstream instruction says to call the Skill tool, use the runtime's
supported skill-loading mechanism. If there is no dedicated tool, load the named
skill's `SKILL.md` and the relevant references as the runtime instructs. That
fallback does not make human-only workflows callable by another skill.

`code-review` requires agent dispatch for its independent review axes. Configure
the tracker with `setup-matt-pocock-skills` in each project before using workflows
that need it. Installing the collection does not run project setup.

The updated `tdd` builds one red/green slice at an agreed seam and leaves
refactoring to review. Use it together with `code-review`. Repository permission
rules still govern external publication, tracker updates, and destructive actions.

## Synchronization

Use `bash update.sh --matt-only --dry-run` to inspect the selected file changes,
then `bash update.sh --matt-only` to apply them. The script clones into temporary
storage, verifies the pinned commit, and checks every selected source before
changing any destination. Simulation does not create destination directories.

Synchronization deletes obsolete files inside selected skill folders. Review any
local edits before applying it. Retiring or renaming a skill requires an explicit
folder removal and manifest change; the script does not delete other skill folders.
Without `--matt-only`, the existing other-vendor updates also run.

When changing the upstream version, review the source manifest, update both the
tag and expected commit in `update.sh`, refresh the license if needed, and validate
the whole collection before applying it.
