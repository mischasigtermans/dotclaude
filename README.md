# DotClaude

My personal Claude Code setup. Public for two reasons: I want to redeploy it on a new machine, and others might find ideas worth borrowing.

This isn't a template to clone wholesale. The voice rules, project paths, and bio reference me specifically. Read the parts that interest you, copy patterns into your own setup.

## Philosophy

Three layers, three roles.

- **CLAUDE.md**: the agent. How it talks, how it codes. Always on.
- **rules/**: always-on add-ons. Auto-load every session. Use for context that should always be present (style, tools, coordination patterns).
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
│   ├── projects.md         # Where my projects live
│   ├── rtk.md              # rtk hook usage
│   ├── team-workflow.md    # When to use agent teams
│   └── writing-style.md    # Voice for any user-facing copy
└── skills/
    ├── counselors/         # External, see below
    ├── laravel-forge-cli/  # Operate Forge servers and sites via the forge CLI
    └── ui/                 # External, see below
```

## My rules

- **[`rules/projects.md`](rules/projects.md)**: where my projects live (`~/Github`, `~/Github/mischasigtermans`, `~/Sites`). So Claude checks those paths first when I name a project.

- **[`rules/rtk.md`](rules/rtk.md)**: how to use the rtk tool. Reminds Claude that a hook is rewriting commands, and what to do when output looks empty or filtered.

- **[`rules/team-workflow.md`](rules/team-workflow.md)**: when to use Claude Code's team-of-agents feature, and when not to. Always-on because the decision happens upfront before any work starts. Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (already set in this repo's `settings.json`).

- **[`rules/writing-style.md`](rules/writing-style.md)**: voice rules for any user-facing text. Word swaps, number formatting, banned engagement-bait closers. Lives in rules instead of skills because writing happens incidentally inside other tasks (drafting a README mid-build, naming a function, writing a commit message), and a skill that needs an explicit trigger gets missed in those cases. The rule pays a small token cost every session; the skill paid zero cost when I remembered to invoke it and full cost in voice drift when I didn't.

## My skills

- **[`skills/laravel-forge-cli/`](skills/laravel-forge-cli/SKILL.md)**: how to operate Laravel Forge servers via the `forge` CLI. Triggers on deploy, prod logs, env pull/push, restart-php-fpm, and similar ops verbs. Saves me from re-explaining the CLI shape every time and keeps Claude from improvising with `curl` for things the CLI does cleanly.

## Borrow one

Single-file rules and skills drop in with a one-liner. Example for `writing-style`:

```bash
curl -fsSL https://raw.githubusercontent.com/mischasigtermans/dotclaude/main/rules/writing-style.md -o ~/.claude/rules/writing-style.md
```

Same pattern for any other rule. For a skill, swap `rules` for `skills` in both the URL and the target path, and create the skill directory first:

```bash
mkdir -p ~/.claude/skills/laravel-forge-cli && curl -fsSL https://raw.githubusercontent.com/mischasigtermans/dotclaude/main/skills/laravel-forge-cli/SKILL.md -o ~/.claude/skills/laravel-forge-cli/SKILL.md
```

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

