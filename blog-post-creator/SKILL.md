---
name: blog-post-creator
description: Write and iterate on blog posts from idea to publishable draft. Use when the user wants to write, outline, draft, edit, or polish a blog post. Triggers on /blog-post-creator, "write a blog post about...", "I have a blog idea", "help me finish this draft", or "improve this post". Covers the full lifecycle from brainstorming to publishing.
---

# Blog Post Creator

Write, iterate, and polish blog posts.

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `posts_dir` | `Posts/` | Directory where posts are stored |

To override, add to your project's CLAUDE.md: `Posts are stored in Resources/Posts/`.

The skill checks the project CLAUDE.md for a posts directory path. If none found, uses the default.

## Trigger

- `/blog-post-creator <idea or title>` — start a new post from an idea
- `/blog-post-creator edit <filename>` — resume/improve an existing post
- `/blog-post-creator list` — list all posts with their status
- `/blog-post-creator status <filename>` — show current state and next steps

## Post Storage

All posts live in `{posts_dir}` as Markdown files with frontmatter.

### Frontmatter Schema

```yaml
---
type: post
title: "Post Title"
slug: "post-title"
tags: []
lang: fr          # fr or en — match the post's language
status: idea      # idea → outline → draft → review → published
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

### Status Lifecycle

| Status | Meaning |
|--------|---------|
| `idea` | Seed — title and rough concept |
| `outline` | Structure validated, sections defined |
| `draft` | Full content written, needs revision |
| `review` | Polished, ready for final read-through |
| `published` | Done — no further edits expected |

### File Naming

`Title-Of-Post.md` — PascalCase with hyphens.

## Workflow: New Post

Walk through stages sequentially. Each stage **saves the file** so progress is never lost. The user can stop and resume later.

### Stage 1 — Seed

1. Understand the idea: ask 1-2 clarifying questions if the intent is ambiguous (audience, angle, key takeaway). Skip if clear.
2. Detect or ask the target language (French or English).
3. Create the file with frontmatter (`status: idea`) and a `## Notes` section capturing the raw idea, audience, and angle.
4. Save and confirm: "Post cree. On passe au plan ?"

### Stage 2 — Outline

1. Propose an outline: title, sections with 1-line summaries, estimated length.
2. Order sections so each builds on the previous. Flag uncertain dependencies.
3. Present and ask for validation — user may reorder, add, remove, or merge.
4. Once approved, write the outline under `## Outline`, set `status: outline`.

### Stage 3 — Draft

1. Write section by section. After each:
   - Append to the file under its heading
   - Save immediately
   - Show brief summary and ask: "Section suivante, ou tu veux ajuster quelque chose ?"
2. Keep paragraphs tight — one idea each. Clarity over length.
3. User can interrupt to revise, rewrite, or skip ahead.
4. When all sections are drafted, set `status: draft`.

### Stage 4 — Review

1. Full pass on: **flow** (transitions, progression), **clarity** (jargon, overloaded sentences), **hooks** (intro grabs? conclusion lands?), **redundancy** (repeated ideas).
2. Present proposed changes as a numbered list. User approves, rejects, or tweaks each.
3. Apply approved changes, set `status: review`.

### Stage 5 — Polish

1. Final pass: grammar, typos, formatting consistency, link placeholders.
2. Generate meta-description (max 160 chars) and suggest tags if missing.
3. Save, set `status: published`. Confirm: "Post pret a publier."

## Workflow: Edit Existing Post

1. Read the file from `{posts_dir}`.
2. Check `status` to understand where it left off.
3. Present diagnostic: current status, word count, what's done vs missing, suggested next step.
4. Ask: "On reprend a [suggested step], ou tu veux faire autre chose ?"
5. Resume from the appropriate stage.

For targeted edits (rewrite a section, change tone, shorten): apply directly, save, show diff summary.

## Workflow: List Posts

Read all `.md` files in `{posts_dir}`, extract frontmatter, present:

| Post | Status | Lang | Updated |
|------|--------|------|---------|

## Writing Principles

- **Lead with value.** Reader knows within 2-3 sentences what they'll get and why it matters.
- **One idea per paragraph.** Two ideas? Split. Makes posts scannable.
- **Show, don't tell.** Examples, code snippets, anecdotes over "it's important to...".
- **Respect the reader's time.** Every sentence earns its place. Cut filler and hedge words.
- **Match the user's voice.** Mirror tone cues — technical, conversational, or in between.
- **Structure serves comprehension.** Headings, lists, code blocks to break walls of text. Don't over-structure.

## Key Behaviors

- **Save after each stage.** The file is the source of truth.
- **Update `updated` date** in frontmatter on every save.
- **Read before writing.** Always read current file state before editing.
- **Propose, don't impose.** Present options during outline and review, let the user decide.
- **Detect language from context.** French idea → French post. English → English. Ask only if ambiguous.
