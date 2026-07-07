---
name: mdpdf
description: Export Markdown and Obsidian notes to polished PDF documents with Pandoc and Typst. Use when converting `.md` files to PDF, rendering Obsidian callouts or embeds, rendering Mermaid diagrams, applying reusable Typst styling, configuring document branding, running PDF export preflight checks, or creating/updating portable Markdown-to-PDF configuration.
---

# mdpdf

## Quick Start

Use the bundled CLI:

```bash
SKILL_DIR=/path/to/mdpdf
python3 "$SKILL_DIR/scripts/mdpdf.py" doctor
python3 "$SKILL_DIR/scripts/mdpdf.py" export input.md --output output.pdf
```

`SKILL_DIR` must point to the installed `mdpdf` skill directory. The CLI resolves bundled Typst templates, Lua filters, and brand assets relative to that directory, so no runner-specific home directory is required.

Legacy shorthand is supported:

```bash
python3 "$SKILL_DIR/scripts/mdpdf.py" input.md --output output.pdf
```

## Installation

This skill is self-contained and runner-agnostic. Install or copy the whole `mdpdf` directory into any skills location supported by your agent runtime, then invoke `scripts/mdpdf.py` by absolute path or through a `SKILL_DIR` variable.

## Workflow

1. Run `doctor` before the first export on a machine or after changing config.
2. Use `export` for a single Markdown/Obsidian file.
3. Use `--print-config` when paths, profile values, or frontmatter behavior are unclear.
4. Render the resulting PDF visually when layout matters.

## Configuration

Read `references/configuration.md` when the task involves profiles, custom paths, branding, or config precedence.

Default behavior is neutral and portable:

- no required vault path;
- output defaults next to the input Markdown file;
- bundled Typst template and Lua filters are resolved relative to this skill;
- organization-specific settings are opt-in through config.

Precedence is:

```text
CLI flags > Markdown frontmatter > config file/profile > environment > neutral defaults
```

## Markdown Support

Read `references/markdown-support.md` when the input uses Obsidian embeds, wiki links, callouts, Mermaid, tables, or page-break comments.

Supported highlights:

- Obsidian image embeds: `![[image.png]]`
- Markdown images with relative or vault paths
- Obsidian callouts through the bundled Pandoc Lua filter
- Mermaid fences rendered to SVG when `npx` is available
- Markdown table normalization before Pandoc
- weak page breaks with `<!-- pdf: pagebreak -->`

## Runtime Requirements

Required:

- Python 3.11+
- Pandoc
- Typst

Optional:

- Node.js/npm with `npx` for Mermaid rendering
- Nix as a fallback provider for `pandoc` and `typst`

If Mermaid is present but `npx` is unavailable, use `--no-render-mermaid`.

## Validation

For skill changes, run:

```bash
SKILL_DIR=/path/to/mdpdf
python3 "$SKILL_DIR/scripts/mdpdf.py" doctor --print-config
python3 "$SKILL_DIR/scripts/mdpdf.py" export "$SKILL_DIR/examples/fixtures/basic.md" --output /tmp/mdpdf-basic.pdf --no-render-mermaid
python3 "$SKILL_DIR/scripts/mdpdf.py" export "$SKILL_DIR/examples/fixtures/obsidian-image.md" --output /tmp/mdpdf-image.pdf --no-render-mermaid
python3 "$SKILL_DIR/scripts/mdpdf.py" export "$SKILL_DIR/examples/fixtures/mermaid.md" --output /tmp/mdpdf-mermaid.pdf
```
