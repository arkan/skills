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

Run synchronization tests with:

```bash
python3 -m unittest discover -s tests -v
```
