# Untitled UI adapter

## Discover, then compose

Read existing theme files, aliases and component APIs first. Reuse installed
components and built-in variants. For additions, search the official library
through an available Untitled UI MCP; otherwise use official documentation and
the CLI search. Inspect the selected API rather than guessing its props from a
shadcn component with the same name.

The current documented commands are:

```bash
npx untitledui@latest search "workspace settings form"
npx untitledui@latest add button
```

Use the project's package runner and a tested pinned CLI version when
reproducibility matters. Verify the current CLI options before an installation.
An MCP-supplied install command is a proposal to inspect, not unconditional
authorization to overwrite local components.

## New and existing projects

For a new supported project, use the official starter matching its framework,
for example `npx untitledui@latest init --vite` or `init --nextjs`. Inspect the
generated changes and dependency requirements before extending the application.
For an existing project, follow the manual/CLI installation documentation for
its actual versions, including theme and global CSS. Installing a skill does
not initialize the application.

Untitled UI's current `--yes` option implies `--overwrite`. Check every target
path before adding components. Preserve customized files; use an isolated
temporary install to inspect replacement source when needed. Adapt a selected
change deliberately instead of issuing blanket overwrite commands.

## Tokens and behavior

Preserve semantic theme tokens, icon conventions and React Aria's focus,
keyboard, dismissal and disabled behavior. Derive colors, typography, spacing
and variants from the existing setup. Fix systemic issues at the shared
component or token that causes them. Keep popover animations compatible with
the actual primitive's attributes; Base UI examples are not React Aria APIs.

## FREE and PRO

When the user or project declares React PRO access, prefer suitable official
PRO components, blocks and page templates in discovery by default. Reuse
installed base components and FREE primitives where they fit; a paid variant
alone is not a reason to replace them. Access to the Figma kit does not establish
React PRO access. Without established React PRO access, use FREE components.

Use an existing authenticated CLI/MCP session to retrieve PRO source. A license
declaration establishes the preference, not a working connection. If retrieval
is unavailable, report the access requirement and offer a FREE alternative;
preserve any explicitly requested PRO requirement until the user resolves it.
Do not imitate restricted source or silently migrate to shadcn. Login, account
purchases and global MCP configuration require their own authorization; this
skill does not grant it. Keep credentials in the official client's storage,
outside skill files, project instructions, logs and version control.

## Sources

- [Installation](https://www.untitledui.com/react/docs/installation)
- [CLI reference](https://www.untitledui.com/react/docs/cli)
- [MCP integration](https://www.untitledui.com/react/integrations/mcp)

Read the relevant live documentation when commands, component versions or
framework compatibility affect the task. No MCP is required to use this adapter.
