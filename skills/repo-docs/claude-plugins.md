# Claude Code plugins

Apply this on top of the universal documentation rules whenever the repo contains `.claude-plugin/plugin.json` or `.claude-plugin/marketplace.json`.

## Marketplace

Mischa publishes plugins through one marketplace.

- **Repo:** `mischasigtermans/by-mischa`
- **Marketplace name** in `marketplace.json`: `by-mischa`
- **User install handle:** `<plugin>@by-mischa`

The marketplace catalog lives at `.claude-plugin/marketplace.json` in that repo. Plugin sources use either `github` (for standalone plugin repos) or `git-subdir` (for plugins inside `claude-personas`).

## Repo layouts

### Standalone plugin repo

For coherent single-plugin products (parley, ralph, library):

```
<repo>/
├── .claude-plugin/plugin.json
├── README.md
├── CHANGELOG.md
├── LICENSE
├── docs/                optional, when README would exceed ~80 lines
├── src/                 or whatever the plugin contains
└── dist/                if applicable, committed build artifacts
```

### Library repo (multiple plugins in one repo)

For `claude-personas`:

```
claude-personas/
├── README.md            repo-level index, not a product pitch
├── CHANGELOG.md         repo-level releases
├── LICENSE
├── manager/             the Personas plugin
│   ├── .claude-plugin/plugin.json
│   ├── README.md
│   ├── CHANGELOG.md
│   ├── docs/
│   └── src/, agents/, hooks/, skills/
└── personas/            independent persona plugins, peers of manager
    ├── steve-jobs/
    │   ├── .claude-plugin/plugin.json
    │   ├── README.md
    │   ├── CHANGELOG.md
    │   ├── CLAUDE.md
    │   ├── persona.json
    │   └── context/, rules/, skills/
    ├── taylor-otwell/
    ├── raymond-hettinger/
    └── david-tolnay/
```

Library repo rules:

- Repo root has no plugin.json. The root README is an index.
- Each plugin under the repo is fully independent.
- Each plugin has its own README and CHANGELOG.
- The marketplace lists each plugin separately. A library repo has no 'main' plugin: the manager is a peer of the personas, not their parent.

## plugin.json

```json
{
  "name": "<plugin-name>",
  "version": "0.1.0",
  "description": "<single sentence, matches README tagline>",
  "author": { "name": "Mischa Sigtermans" },
  "homepage": "https://github.com/mischasigtermans/<repo>",
  "repository": "https://github.com/mischasigtermans/<repo>",
  "license": "MIT"
}
```

The README tagline may add ', as one Claude Code plugin' to the description.

For plugins inside a library repo, `homepage` includes the subdirectory path; `repository` points at the library repo root.

Set `version` explicitly on every release. Don't rely on commit-SHA versioning.

## Install commands in README

Always two lines, even though the first is needed only once:

```
/plugin marketplace add mischasigtermans/by-mischa
/plugin install <plugin>@by-mischa
```

## Version badge

A plugin README's version badge reads `version` from `plugin.json` on `main`, so a plugin needs no GitHub Release for it:

```markdown
[![Version](https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/mischasigtermans/<repo>/main/.claude-plugin/plugin.json&query=$.version&label=version&prefix=v)](https://github.com/mischasigtermans/<repo>)
```

For a plugin inside a library repo, the URL takes the plugin's subdirectory (`<repo>/main/<dir>/.claude-plugin/plugin.json`) and the link points at that directory.

## Dependency chain in the personas family

```
Persona plugins → Personas manager → Parley → (nothing)
```

Rules:

- Every persona README's 'Requires' section names both the Personas manager and Parley, with links.
- The Personas manager README's 'Requires' section names Parley as required.
- Parley's README never depends on the others. Personas appears in Parley's README only in 'Related', as one consumer of Parley.
- A persona loads its voice and runs its commands without the Personas manager installed. The manager adds threads, memory, and the dispatcher. State this trade-off in the persona README.

## Persona plugin README

Persona plugins have their own shape.

```markdown
# <Name>

<One-line tagline capturing the voice.>

<2-3 sentences. Who this persona is, what advice they give, what makes them
useful in real work.>

## What <Name> is good at

<3-5 bullets. Concrete capabilities. Each starts with a verb.>

## Example

<Short input → short response. One exchange. Real voice.>

## Installation

\```
/plugin marketplace add mischasigtermans/by-mischa
/plugin install <persona-name>@by-mischa
\```

### Requires

- Claude Code
- [Personas plugin](https://github.com/mischasigtermans/claude-personas/tree/main/manager) for threads and memory
- [Parley plugin](https://github.com/mischasigtermans/parley), used by Personas as transport

## With the Personas plugin

<2-3 sentences explaining the upgrade: durable per-project memory, threaded
conversations, /personas commands. Without it, the persona still works but
each conversation is fresh.>

## What's inside

<Optional terse list of skills, context files, knowledge modules. Skip when
unremarkable.>

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## Credits

- [Mischa Sigtermans](https://github.com/mischasigtermans)
- Philosophy: <Name>, as documented by <key sources>

## License

MIT.
```

Specific rules for persona READMEs:

- No benchmarks section. No accuracy tables, no consistency scores.
- No 'see also' linking to sibling personas. The repo index handles that.
- Don't call the persona 'bundled' with anything. It's an independent plugin.
- No quotes section. Voice lives in CLAUDE.md.
- The 'Requires' section names Personas and Parley explicitly.

## persona.json

```json
{
  "name": "<canonical-persona-name>",
  "displayName": "<Display Name>",
  "aliases": ["short-form", "last-name"],
  "description": "<single sentence>",
  "model": "opus",
  "traits": ["domain", "domain", "domain"]
}
```

Don't include an `mcpServers` block. The Personas manager registers each persona as a parley peer through hooks, so a persona plugin never bundles parley as its own MCP server.

## Library repo root README

The root README of a library repo (e.g. `claude-personas`) is an index. It explains:

- What this library contains (manager + N independent plugins).
- Who each plugin is for and what it does, one line each.
- That each plugin is installable separately via the marketplace.
- Links to each plugin's own README.

Keep it short, with no long intro. A reader who wants the pitch for Steve clicks through to `personas/steve-jobs/README.md`.
