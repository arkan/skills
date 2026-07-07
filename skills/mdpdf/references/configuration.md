# Configuration

## Discovery

`mdpdf.py` reads the first available config in this order:

1. `--config PATH`
2. nearest `.mdpdf.toml` from the input file upward
3. `MDPDF_CONFIG`
4. `~/.config/mdpdf/config.toml`

Use `--print-config` to inspect the resolved values without exporting.

## Precedence

```text
CLI flags > Markdown frontmatter > config file/profile > environment > neutral defaults
```

Environment variables:

- `MDPDF_CONFIG`
- `MDPDF_PROFILE`
- `MDPDF_VAULT_ROOT`
- `OBSIDIAN_VAULT_PATH`
- `MDPDF_OUTPUT_DIR`

## Generic Config

```toml
[document]
author = ""
language = "fr"
template = "internal"
brand = "neutral"
toc = false
section_breaks = "none"
render_mermaid = true
reproducible = true

[output]
directory = "{source_dir}"
```

## Profile Example

Store this as `.mdpdf.toml` at a project or vault root, then run with `--profile client`.

```toml
[profiles.client.vault]
root = "~/Documents/Notes"

[profiles.client.output]
directory = "{vault}/Resources/Exports/PDF/{year_month}"

[profiles.client.document]
author = "Example Author"
language = "fr"
template = "pro"
brand = "client"
toc = true
section_breaks = "h2-major"
render_mermaid = true
reproducible = true

[profiles.client.contact]
name = "Example Author"
role = "Consultant"
company = "Example Company"
address = "1 Example Street\n75000 Paris - France"
phone = "+33 1 00 00 00 00"
email = "author@example.com"
url = "www.example.com"

[brands.client]
label = "EXAMPLE COMPANY"
logo = "~/Documents/brand/logo.png"
```

## Path Tokens

`output.directory` supports:

- `{vault}`
- `{source_dir}`
- `{source_stem}`
- `{slug}`
- `{year_month}`
- `{date}`

Relative output directories are resolved from the source Markdown directory.

Exports are reproducible by default: no export timestamp is shown and Typst receives a stable creation timestamp. Use `--no-reproducible` or `reproducible = false` when current export timestamps are desired.

## Frontmatter

Supported Markdown frontmatter keys:

- `title`
- `subtitle`
- `author`
- `date`
- `status`
- `confidentiality`
- `version`
- `pdf_version`
- `short_title`
- `pdf_template`
- `pdf_section_breaks`
- `pdf_brand`
- `pdf_audience`
- `pdf_justify_body`
- `lang`
- `toc`
