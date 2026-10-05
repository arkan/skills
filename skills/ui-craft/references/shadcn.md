# shadcn adapter

After routing identifies shadcn, load the installed official `shadcn` skill.
Its `components.json` discovery trigger does not override the library evidence
used by `ui-craft`.

If the runtime does not execute the skill's dynamic context directive, run its
project-context command explicitly using the project's runner:

```bash
npx shadcn@latest info --json
npx shadcn@latest docs button dialog
```

Read the returned documentation for the selected APIs. Follow the actual
aliases, icon library, Tailwind version and primitive base. A fresh skill
snapshot is not authorization to upgrade the application's dependencies.

Reuse installed components and their built-in variants first. Search the
official registry for additions and inspect proposed changes before accepting
an update to a customized component. Verify added files, dependencies and
imports, including third-party code that hard-codes another project's aliases.

Keep composition, styling and accessibility rules in the official skill rather
than maintaining a competing copy here. If it is not installed, use the live
official documentation, name the missing skill and limit the coverage claim.

- [Official skill](https://ui.shadcn.com/docs/skills)
- [CLI reference](https://ui.shadcn.com/docs/cli)
- [MCP integration](https://ui.shadcn.com/docs/mcp)
