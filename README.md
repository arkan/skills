# Skills

A collection of agent skills (for Claude Code, Claude Desktop, Codex, etc.) covering planning, development, research, knowledge management, and tooling.

## Installing a skill

All skills can be installed with `npx skills` from this repo. The command fetches the skill folder and drops it into your local skills directory:

```bash
npx skills@latest add arkan/skills/<skill-name>
```

For example:

```bash
npx skills@latest add arkan/skills/tdd
npx skills@latest add arkan/skills/amazon-shopping
```

To list everything that's installable:

```bash
npx skills@latest list arkan/skills
```

> Skills nested in a sub-folder (e.g. `obsidian/blog-post-creator`) are installed by referencing the full path: `npx skills@latest add arkan/skills/obsidian/blog-post-creator`.

## Available skills

### Planning & design

| Skill | Role |
|---|---|
| [`write-a-prd`](./write-a-prd) | Build a PRD via interactive interview and codebase exploration, filed as a GitHub issue |
| [`prd-to-plan`](./prd-to-plan) | Turn a PRD into a multi-phase implementation plan using tracer-bullet vertical slices |
| [`prd-to-issues`](./prd-to-issues) | Break a PRD into independently grabbable GitHub issues |
| [`grill-me`](./grill-me) | Get relentlessly interviewed about a plan or design until every branch is resolved |
| [`design-an-interface`](./design-an-interface) | Generate multiple radically different interface designs for a module via parallel sub-agents |
| [`request-refactor-plan`](./request-refactor-plan) | Create a refactor plan with tiny commits, filed as a GitHub issue |
| [`ubiquitous-language`](./ubiquitous-language) | Extract a DDD ubiquitous-language glossary from a conversation, flagging ambiguities |
| [`zoom-out`](./zoom-out) | Step back to give broader context or a higher-level perspective on a section of code |

### Development & code quality

| Skill | Role |
|---|---|
| [`tdd`](./tdd) | Red-green-refactor loop — build features or fix bugs one slice at a time |
| [`do`](./do) | Autonomously execute a plan/PRD: dispatch tasks to subagents, run a Codex review loop until it passes |
| [`triage-issue`](./triage-issue) | Investigate a bug, find the root cause, file a GitHub issue with a TDD-based fix plan |
| [`qa`](./qa) | Interactive QA session — user reports bugs conversationally, agent files them as issues |
| [`github-triage`](./github-triage) | Triage GitHub issues through a label-based state machine with grilling sessions |
| [`improve-codebase-architecture`](./improve-codebase-architecture) | Find architectural improvements — deepen shallow modules, improve testability |
| [`migrate-to-shoehorn`](./migrate-to-shoehorn) | Migrate test files from `as` assertions to `@total-typescript/shoehorn` |
| [`scaffold-exercises`](./scaffold-exercises) | Create exercise directory structures (sections, problems, solutions, explainers) |

### Research & web

| Skill | Role |
|---|---|
| [`deep-research`](./deep-research) | Enterprise-grade research with multi-source synthesis, citation tracking, and credibility scoring |
| [`exa`](./exa) | Web search, URL extraction, and AI-answered queries via the Exa API |
| [`amazon-shopping`](./amazon-shopping) | Search Amazon (any regional domain), verify products, present ranked recommendations |

### Knowledge & writing

| Skill | Role |
|---|---|
| [`gen-wiki`](./gen-wiki) | Compile personal data (journals, notes, messages) into a queryable knowledge wiki |
| [`github-import`](./github-import) | Import GitHub starred repos into an Obsidian vault as individual notes with a `.base` view |
| [`obsidian/blog-post-creator`](./obsidian/blog-post-creator) | Write and iterate on blog posts from idea to publishable draft |
| [`obsidian/coach`](./obsidian/coach) | Life-coaching skill that uses Obsidian notes for personal context |

### Tooling & setup

| Skill | Role |
|---|---|
| [`setup-pre-commit`](./setup-pre-commit) | Set up Husky + lint-staged with Prettier, type checking, and tests |
| [`git-guardrails-claude-code`](./git-guardrails-claude-code) | Add Claude Code hooks that block dangerous git commands before they execute |
| [`write-a-skill`](./write-a-skill) | Create new agent skills with proper structure, progressive disclosure, and bundled resources |
