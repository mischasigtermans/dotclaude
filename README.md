# DotClaude

My personal Claude Code setup. Public for two reasons: I want to redeploy it on a new machine, and others might find ideas worth borrowing.

This isn't a template to clone wholesale. The voice rules, project paths, and bio reference me specifically. Read the parts that interest you, copy patterns into your own setup.

## Philosophy

Three layers, three roles.

- **CLAUDE.md**: the agent. How it talks, how it codes. Always on.
- **rules/**: always-on add-ons. Auto-load every session. Use for context that should always be present (project paths, tools, coordination patterns).
- **skills/**: trigger on intent. Load only when matched against the user's message. Use for behavior that activates for specific tasks (writing copy, deploying, reviewing).

The split keeps the always-on context lean. Rules pay the token cost every session, skills only when invoked. Anything the agent should know all the time goes in rules. Anything that only matters for a class of task goes in skills.

## Layout

```
.
├── CLAUDE.md               # Communication, coding discipline, hard rules
├── settings.json           # Env vars, hook config, status line, plugin enablement
├── statusline-wrapper.sh   # Status line composition
├── statusline-command.sh   # Git info for the status line
├── hooks/
│   └── rtk-rewrite.sh      # Token-saving Bash hook
├── rules/
│   ├── bear.md             # How I format and tag notes in Bear
│   ├── projects.md         # Where my projects live
│   ├── rtk.md              # rtk hook usage
│   └── team-workflow.md    # When to use agent teams
└── skills/
    ├── counselors/         # External, see below
    ├── devnomads-api/      # Operate DevNomads infrastructure via the dn client
    ├── docs/               # House style for READMEs, CHANGELOGs, and repo boilerplate
    ├── laravel-forge-cli/  # Operate Forge servers and sites via the forge CLI
    ├── solo/               # Operate the Solo terminal harness via its MCP server
    └── ui/                 # External, see below
```

## My rules

- **[`rules/bear.md`](rules/bear.md)**: how I format and tag notes in [Bear](https://bear.app). Tag placement, the tag taxonomy (ventures, ideas, personal, meetings, tooling, reading), when to migrate a note verbatim vs rewrite it, and how to escape inline hashtags so they don't pollute the tag tree. Always-on because note edits happen mid-task, not in a dedicated session. The taxonomy examples are genericised here; the live venture set is discovered at runtime via `bearcli tags`.

- **[`rules/projects.md`](rules/projects.md)**: where my projects live (`~/Github`, `~/Github/mischasigtermans`, `~/Sites`). So Claude checks those paths first when I name a project.

- **[`rules/rtk.md`](rules/rtk.md)**: how to use the rtk tool. Reminds Claude that a hook is rewriting commands, and what to do when output looks empty or filtered.

- **[`rules/team-workflow.md`](rules/team-workflow.md)**: when to use Claude Code's team-of-agents feature, and when not to. Always-on because the decision happens upfront before any work starts. Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (already set in this repo's `settings.json`).

Voice rules used to live in `rules/writing-style.md`. They've been folded into [`CLAUDE.md`](CLAUDE.md) under 'How you write', since writing happens incidentally inside other tasks (drafting a README mid-build, naming a function, writing a commit message) and the agent definition is the right place for an always-on style.

## My skills

- **[`skills/docs/`](skills/docs/SKILL.md)**: how my repos document themselves. Triggers on writing or restructuring READMEs, CHANGELOGs, `.github/` files, commit messages, or release tagging. Detects the ecosystem from the repo (Claude Code plugin, Laravel package, app) and loads the matching conventions. The skill is the source of truth; individual repos catch up to it, not the other way around.

- **[`skills/laravel-forge-cli/`](skills/laravel-forge-cli/SKILL.md)**: how to operate Laravel Forge servers via the `forge` CLI. Triggers on deploy, prod logs, env pull/push, restart-php-fpm, and similar ops verbs. Saves me from re-explaining the CLI shape every time and keeps Claude from improvising with `curl` for things the CLI does cleanly.

- **[`skills/devnomads-api/`](skills/devnomads-api/SKILL.md)**: how to operate DevNomads (infrapod.nl) infrastructure via its HTTP API. Ships a small `dn` bash client that wraps the raw endpoints with bearer auth and a y/N prompt on anything that moves traffic or power. Triggers on reboots, proxy repoints, DNS zone edits, and container deploys. This is the infra layer below the app, where forge and SSH take over. Account-specific IDs and tokens live outside the repo so the skill stays publishable.

- **[`skills/solo/`](skills/solo/SKILL.md)**: how to operate [Solo](https://soloterm.com), my terminal harness, via its MCP server. Covers long-running processes (dev servers, watchers, log tails), cross-session scratchpads and todos, lead-plus-worker orchestration with cross-lab agents, and coordination primitives (locks, timers, KV). My default for parallel work over Claude Code teams, since Solo persists and shows up in the IDE.

## Borrow one

Single-file rules and skills drop in with a one-liner. Example for `team-workflow`:

```bash
curl -fsSL https://raw.githubusercontent.com/mischasigtermans/dotclaude/main/rules/team-workflow.md -o ~/.claude/rules/team-workflow.md
```

Same pattern for any other rule. For a skill, swap `rules` for `skills` in both the URL and the target path, and create the skill directory first:

```bash
mkdir -p ~/.claude/skills/laravel-forge-cli && curl -fsSL https://raw.githubusercontent.com/mischasigtermans/dotclaude/main/skills/laravel-forge-cli/SKILL.md -o ~/.claude/skills/laravel-forge-cli/SKILL.md
```

Multi-file skills like `docs` and `devnomads-api` (which ships its own `dn` client) don't fit a one-liner. Clone the repo and copy the directory: `git clone https://github.com/mischasigtermans/dotclaude /tmp/dc && cp -r /tmp/dc/skills/docs ~/.claude/skills/`.

## External dependencies

Some skills and rules in this repo reference external tools. Install them separately if you want those capabilities.

- **rtk**: token-saving CLI proxy for shell command output. Referenced by `rules/rtk.md`. [rtk-ai/rtk](https://github.com/rtk-ai/rtk).
- **counselors**: multi-agent code review via parallel AI agents, by [Aaron Francis](https://x.com/aarondfrancis). Referenced by `skills/counselors/`. [aarondfrancis/counselors](https://github.com/aarondfrancis/counselors).
- **ui.sh**: paid UI exploration skill, managed remotely, by [Adam Wathan](https://x.com/adamwathan) and [Steve Schoger](https://x.com/steveschoger). Referenced by `skills/ui/`. [ui.sh](https://ui.sh).

Without these tools installed, the related skill or rule has no effect. Nothing else breaks.

## What is NOT in this repo

By design, this repo uses a `.gitignore` whitelist. Everything not explicitly listed is ignored.

That means no `settings.local.json`, no plugin caches, no memory files, no project data, no logs, no API keys, no tokens, no session history. The repo carries the parts that are reproducible across machines and worth sharing: agent definition, settings, hooks, status line, rules, and skills. Nothing more.

The plugins enabled in `settings.json` install separately from their own repositories or marketplaces. The settings file flips them on, but you need them installed for the toggles to do anything. Three I built and wrote about: [Personas](https://mischa.sigtermans.me/thought/taylor-is-still-immortal-but-now-he-remembers), [Parley](https://mischa.sigtermans.me/thought/how-i-made-my-claude-code-projects-call-each-other), [Ralph](https://mischa.sigtermans.me/thought/my-simplified-ralph-loop-setup-for-claude-code). Plus language servers.

If you want to add a new file or directory, edit `.gitignore` to whitelist it explicitly. Do not disable the whitelist.

## Further reading

- [My Claude Code settings](https://mischa.sigtermans.me/thought/my-claude-code-settings): the broader picture, env vars, and philosophy.
- [How I saved billions of tokens with a Claude Code hook](https://mischa.sigtermans.me/thought/how-i-saved-billions-of-tokens-with-a-claude-code-hook): why rtk, and how the hook works.
- [How I set up my Claude Code status line](https://mischa.sigtermans.me/thought/how-i-set-up-my-claude-code-status-line): the reasoning behind the statusline scripts.

## Credits

Several coding rules in CLAUDE.md (Surgical changes, Simplicity, Success criteria) are downstream of [Andrej Karpathy's notes on LLM coding](https://x.com/karpathy/status/2015883857489522876), distilled via [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills/tree/main).

## License

MIT. See [LICENSE](LICENSE).

