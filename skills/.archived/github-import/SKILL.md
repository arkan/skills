---
name: github-import
description: "Import GitHub starred repos into the Obsidian vault as individual notes with a .base database view. Fetches stars via gh CLI, creates new notes (with README summary in French, auto-tags) and updates existing notes (stars, forks, dates, topics) in Resources/GitHub-Stars/. Idempotent — safe to run repeatedly. Use this skill when the user wants to sync, import, update, or fetch their GitHub stars, or mentions starred repos, GitHub bookmarks, or gh stars."
argument_hint: "[--all | --count N | --fix-dates | --strip-sections | --help]"
---

# GitHub Stars Import

Import GitHub starred repositories into the vault as individual structured Obsidian notes, with an Obsidian Bases database view for browsing, filtering, and sorting.

## Trigger

`/github-import` — fetch last 30 stars (daily incremental)
`/github-import --all` — fetch all stars (full sync)
`/github-import --count N` — fetch N most recent stars
`/github-import --fix-dates` — fix `repo_updated` on all existing files
`/github-import --strip-sections` — remove Details/Topics sections from all files

## Storage

- Individual notes: `Resources/GitHub-Stars/<Owner>-<Repo>.md`
- Database view: `Resources/GitHub-Stars/GitHub-Stars.base`
- Script: `.claude/skills/github-import/gh_stars.py`
- LLM manifest: `/tmp/gh_stars_manifest.json`

## Architecture

The import is split into two phases to minimize LLM token usage:

1. **Python script** (mechanical) — fetches API data, generates frontmatter/Details/Topics/footer, writes all files, fetches READMEs. Outputs a manifest of repos needing French summaries.
2. **LLM** (intelligence) — reads the manifest, generates French summaries, injects them into `## Resume` sections, and enriches `## Voir aussi` cross-links.

## Workflow

### Phase 1 — Run the Python script

Run the script with the appropriate flags:

```bash
# Incremental (default): last 30
python3 .claude/skills/github-import/gh_stars.py

# Full sync
python3 .claude/skills/github-import/gh_stars.py --all

# Custom count
python3 .claude/skills/github-import/gh_stars.py --count 50

# Fix dates only (no new imports)
python3 .claude/skills/github-import/gh_stars.py --fix-dates

# Strip Details/Topics sections from all files
python3 .claude/skills/github-import/gh_stars.py --strip-sections
```

The script:
1. Fetches stars via `gh` CLI (paginated for `--all`)
2. Fetches GitHub Lists index via GraphQL
3. Classifies new vs existing stars
4. For each **new** star (in parallel, 10 workers):
   - Fetches last commit date on default branch (`/repos/OWNER/REPO/commits?per_page=1`)
   - Fetches and decodes README (truncated to 5000 chars)
   - Generates tags from language + topics using mapping rules
   - Writes the complete `.md` file with `{{RESUME_PLACEHOLDER}}` in the Resume section
5. For each **existing** star (in parallel):
   - Updates frontmatter (stars, forks, license, description, topics, lists, repo_updated, updated_at)
   - Re-derives tags (preserving user-added tags)
   - Does NOT touch Resume, Voir aussi, or footer
6. Creates `.base` file if missing
7. Writes manifest to `/tmp/gh_stars_manifest.json`

Report the script's output to the user, then proceed to Phase 2.

### Phase 2 — LLM generates French summaries

Read `/tmp/gh_stars_manifest.json`. It's an array of objects:
```json
[{
  "file": "owner-repo.md",
  "full_name": "owner/repo",
  "description": "...",
  "language": "Go",
  "readme": "decoded README content (max 5000 chars)"
}]
```

For each entry with a non-null `readme`:
1. Generate a French summary (3-8 sentences) covering: what the project does, key features, target audience, and why it's interesting
2. Replace `{{RESUME_PLACEHOLDER}}` in the file with the summary

For entries where `readme` is null, replace `{{RESUME_PLACEHOLDER}}` with `(README non disponible)`.

**Parallelization**: Split the manifest into batches of ~30 and spawn one Agent per batch (run_in_background=true, mode=bypassPermissions). Each agent:
- Reads its batch from the manifest
- Generates French summaries
- Uses the Edit tool to replace `{{RESUME_PLACEHOLDER}}` in each file
- Reports count of summaries generated

This keeps the main context clean and parallelizes the only LLM-expensive work.

### Phase 3 — Enrich Voir aussi cross-links

After all summaries are injected, enrich `## Voir aussi` for new notes:

For each new star, find related stars among ALL existing notes in `Resources/GitHub-Stars/`:
1. **Same owner**: other repos by the same GitHub owner/org
2. **Same language**: repos in the same primary language (limit to 3)
3. **Shared topics (≥2 in common)**: repos with overlapping GitHub topics

Keep to 3-6 links max per note. Use `[[Owner-Repo]]` wikilink format.

This can be done efficiently by grepping frontmatter fields to build an index, then batch-editing the Voir aussi sections.

### Phase 4 — Report

Display a summary:

```
Import GitHub Stars terminé.
- Stars récupérées : Y
- Nouvelles : X
- Mises à jour : Z
- READMEs résumés : N (nouveaux uniquement)
- Notes créées : X
- Notes mises à jour : Z
```

## Note Format

Each note in `Resources/GitHub-Stars/<Owner>-<Repo>.md`:

```markdown
---
type: github-star
repo_fullname: "owner/repo"
repo_name: "repo"
owner: "owner"
description: "original description"
language: "Language"
stars: N
forks: N
license: "SPDX-ID"
topics: [topic1, topic2]
tags: [github-star, tag1, tag2]
lists: ["List A", "List B"]
homepage: "url"
source: "github_url"
starred_at: YYYY-MM-DD
repo_created: YYYY-MM-DD
repo_updated: YYYY-MM-DD
status: draft
created: YYYY-MM-DD
updated_at: YYYY-MM-DD
---

## Resume

<French summary — 3-8 sentences>

## Voir aussi

- [[Related-Star-1]]
- [[Related-Star-2]]

---
↑ [[GitHub-Stars]] | [[tag1]] | [[tag2]]
```

## Tag Mapping Rules

**Language → tag**: `Go` → `go`, `Python` → `python`, `TypeScript` → `typescript`, `JavaScript` → `javascript`, `Rust` → `rust`, `Java` → `java`, etc. Use lowercase.

**Topics → tags**:
- `cli`, `command-line` → `cli`
- `machine-learning`, `deep-learning`, `llm`, `ai` → `ai`
- `devops`, `ci-cd`, `infrastructure` → `devops`
- `kubernetes`, `docker`, `containers` → `devops`
- `security`, `cryptography` → `security`
- `database`, `sql`, `postgresql` → `database`
- `frontend`, `react`, `vue`, `svelte` → `frontend`
- `backend`, `api`, `rest`, `grpc` → `backend`
- `open-source` → `open-source`
- `startup`, `saas` → `startup`
- Other topics: keep as-is if single lowercase words

Always include `github-star`. 3-8 tags total.

## repo_updated Field

Do NOT use `pushed_at` or `updated_at` from the starred repos API — these reflect activity on ANY branch. The script fetches the last commit date on the default branch via:

```bash
gh api '/repos/OWNER/REPO/commits?per_page=1' --jq '.[0].commit.committer.date'
```

Fallback to `pushed_at` only if the commits API call fails.

## Rules

- The `gh` CLI must be installed and authenticated. If not, tell the user to run `gh auth login`.
- README summaries are in French. Repo descriptions stay in their original language in frontmatter.
- File naming: `<Owner>-<Repo>.md` (keep GitHub's original casing).
- If README fetch fails, use `(README non disponible)`.
- The `.base` file is only created once. It auto-updates via Obsidian's live queries.
- Content language: descriptions stay original, summaries and sections are in French.

## Examples

Input: `/github-import`
→ Runs script for 30 latest stars, then LLM generates summaries

Input: `/github-import --all`
→ Full sync of all stars

Input: `/github-import --count 10`
→ Fetches and processes 10 latest stars

Input: `/github-import --fix-dates`
→ Fixes repo_updated on all existing files (no new imports)

Input: `/github-import --strip-sections`
→ Removes Details/Topics sections from all existing files
