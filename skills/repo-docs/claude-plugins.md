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
├── README.md            repo-level index, not a productpitch
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
- The marketplace lists each plugin separately. There is no 'main' plugin in a library repo; the manager is a peer of the personas, not their parent.

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

For plugins inside a library repo, `homepage` includes the subdirectory path; `repository` points at the library repo root.

Set `version` explicitly on every release. Don't rely on commit-SHA versioning.

## Install commands in README

Always two lines, even though the first is one-time:

```
/plugin marketplace add mischasigtermans/by-mischa
/plugin install <plugin>@by-mischa
```

## Dependency chain in the personas family

```
Persona plugins → Personas manager → Parley → (nothing)
```

Rules:

- Every persona README's 'Requires' section names both the Personas manager and Parley, with links.
- The Personas manager README's 'Requires' section names Parley as required.
- Parley's README never depends on the others. Personas appears in Parley's README only in 'Related', as one consumer of Parley.
- A persona loads its voice and runs its commands even without the Personas manager installed. The manager adds threads, memory, and the dispatcher. Make this trade-off explicit in the persona README.

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
- No bundled-language. The persona is an independent plugin, not 'bundled' with anything.
- No quotes section. Voice lives in CLAUDE.md, not the README.
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

Do not include an `mcpServers` block. The Personas manager registers each persona as a parley peer via hooks. Persona plugins must not bundle parley as their own MCP server.

## Library repo root README

The root README of a library repo (e.g. `claude-personas`) is an index, not a productpitch. It explains:

- What this library contains (manager + N independent plugins).
- Who each plugin is for and what it does, one line each.
- That each plugin is installable separately via the marketplace.
- Links to each plugin's own README.

Keep it tight. No long intro; if a reader wants the pitch for Steve, they click through to `personas/steve-jobs/README.md`.
