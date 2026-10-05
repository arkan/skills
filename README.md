# Skills

A collection of agent skills covering planning, development, research, knowledge management, and tooling.

## Installing a skill

All skills can be installed with `npx skills` from this repo. The command fetches the skill folder and drops it into your local skills directory:

```bash
npx skills@latest add arkan/skills
```

## Updating vendored skills

Preview or apply only the pinned Matt Pocock collection:

```bash
bash update.sh --matt-only --dry-run
bash update.sh --matt-only
```

Without `--matt-only`, the script also updates the other configured vendors.
`--dry-run` previews changes without writing to this repository.

See [the Matt Pocock migration notes](docs/mattpocock-skills.md) for the upstream
version, renamed and removed skills, domain glossary migration, and invocation
rules.

## UI workflow

`ui-craft` composes polished interfaces with Untitled UI for new React projects
and preserves the established library in existing projects, including shadcn.
It integrates Jakub Krehel's quality domains and Emil Kowalski's motion guidance.

See [UI skills](docs/ui-skills.md) for the complete installation command, pinned
sources, rule ownership, and runtime compatibility. Installing skills does not
initialize an application, configure MCP, or activate a paid license.

Preview or update only this collection:

```bash
bash update.sh --ui-only --dry-run
bash update.sh --ui-only
```

UI updates preserve unrelated files and refuse to overwrite local changes in
the imported folders or license notices. See the
[evaluation record](docs/ui-skills-evaluation.md) for verification coverage.

Run synchronization tests with:

```bash
python3 -m unittest discover -s tests -v
```
