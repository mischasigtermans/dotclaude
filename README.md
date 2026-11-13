# DotClaude

My personal Claude Code setup, shared so you can see how I work with it and borrow what's useful.

This isn't a template to clone wholesale. The voice rules, project paths, and bio reference me specifically. Read the parts that interest you, copy patterns into your own setup. It holds how I work in every project and nothing about any one of them.

## Layout

- **CLAUDE.md**: the agent. How it talks, how it codes. Always on.
- **rules/**: context that loads on its own. Most load every session; `ui.md` and `laravel.md` carry `paths:` frontmatter and load only when Claude reads a matching file.
- **[skills](https://github.com/mischasigtermans/skills)**: behaviour for a class of task, loaded when the ask matches or when I type the slash command. They live in their own repo, as the `development` and `writing` plugins.
- **hooks/**: what prose can't enforce. My most frequent corrections were things CLAUDE.md already said, so the recurring ones are hooks.
- **evals/**: scenarios that run CLAUDE.md against a small repo and grade what Claude does with it.

Rules enter context when loaded; skill names and descriptions enter discovery context, with bodies loaded on invocation. Hooks run outside model context but their messages enter it.

## Rules

- **[`projects.md`](rules/projects.md)**: where my projects live, so Claude checks those paths first when I name one.
- **[`rtk.md`](rules/rtk.md)**: a hook rewrites shell commands through rtk; which output it condenses and how to bypass it.
- **[`orchestration.md`](rules/orchestration.md)**: which tier parallel work runs at (inline, subagents, an agent team, Workflow, Solo), how sessions talk to each other, who commits and who pushes, and that whoever delegates collects.
- **[`second-opinions.md`](rules/second-opinions.md)**: when to ask a persona, a peer project, a [Parley](https://github.com/mischasigtermans/claude-parley) gathering or a panel of agents unprompted, and the gates every review question carries.
- **[`ui.md`](rules/ui.md)**: the bar every UI change meets without being asked. Mobile-first, dark variants, Flux controls, design guidelines for anything new, and what a page has to show before I look.
- **[`laravel.md`](rules/laravel.md)**: Pint on the Laravel preset, never `--dirty` or `--blade`, Flux Pro activation, what to leave unchecked at `boost:install`, and the Herd and Laravel Cloud traps I've hit. Loads on any PHP file, so a new project needs no setup.

## Skills

Two packages share one source repo and one marketplace:

- **development:** finish, handoff, sync-docs, repo-docs, ui, motion, design-pack, solo, panel, laravel-forge and cloud-database. For Claude Code, with the sharpen gate.
- **writing:** sharpen and mail. For Desktop and Code, without hooks. Development depends on Writing.

This machine uses `development@local` and `writing@local`, with package sources under `~/Github/mischasigtermans/skills/plugins/`. Claude Code reads a plugin from a local directory marketplace in place, so an edit there reaches new sessions at once and an open session after `/reload-plugins`. To try a checkout without installing it, pass both package directories with `--plugin-dir`.

To install them from the marketplace:

```text
/plugin marketplace add mischasigtermans/by-mischa
/plugin install development@by-mischa
/plugin install writing@by-mischa
```

Desktop needs only Writing. `development:ui` is the craft skill; `development:design-pack` fetches the [ui.sh](https://ui.sh) design guidelines through its MCP server and needs an account there.

## Hooks

| Hook | Event | What it does |
| --- | --- | --- |
| [`rtk-rewrite.sh`](hooks/rtk-rewrite.sh) | PreToolUse Bash | Rewrites commands through rtk for smaller output |
| [`bash-guard.py`](hooks/bash-guard.py) | PreToolUse Bash | Denies `git add -A`/`.`, `commit -a`, commit trailers, `--no-verify`, a `core.hooksPath` override, any `git tag` that writes, `pint --dirty` and `--blade`, `pkill` or `killall` on a test runner, `herd secure` |
| [`config-protect.py`](hooks/config-protect.py) | PreToolUse Edit/Write | Denies edits to Pint, PHPStan, Prettier and ESLint config: fix the code, not the linter |
| [`ui-gate.py`](hooks/ui-gate.py) | PreToolUse Edit/Write | Sends `rules/ui.md` with the first UI edit when no UI file was read (the path rule didn't load) |
| [`memory-gate.py`](hooks/memory-gate.py) | PreToolUse Edit/Write | Denies feedback memories (a rule belongs in the repo's guideline, or here when it's how I work everywhere) and status in project memories |
| [`scope-gate.py`](hooks/scope-gate.py) | PreToolUse Edit/Write | Reminds edits to the setup and plugin skills to check scope, once per home session or per distinct edit from a project. Retrying passes; it does not validate the text. Local tool-managed skills are excluded |
| [`php-format.py`](hooks/php-format.py) | PostToolUse, Stop | Notes edited PHP files (never Blade); at Stop runs Pint on them and PHPStan, blocks on errors |
| [`dash-lint.py`](hooks/dash-lint.py) | PostToolUse Edit/Write | Flags em dashes, en dashes and middle dots in copy |

`bash hooks/tests/run.sh` pipes fake payloads through every hook and asserts on the output. All hooks fail open: an internal error never blocks a tool call.

## Evals

`evals/` tests the instructions the way a suite tests code. Each of its 15 scenarios hands a fresh Claude session a small repo and a request, then grades what it did: which files a commit holds, whether a comment was added, whether a number came out as 17.000.

```bash
python3 evals/run.py probe
python3 evals/run.py run --batch today --arms none,current
python3 evals/run.py report --batch today
```

`probe` is one cheap run that proves a session sees only the text under test. `none` runs without instructions and `current` with `CLAUDE.md` and `rules/orchestration.md`; a file in `evals/variants/` adds a wording to compare. A rule that passes without instructions isn't doing anything. A rule that fails with them needs other words or a hook.

Runs use your own Claude account and count against its limits. Three runs of every scenario on Opus cost about $5,50 at list price. The checks cover the text alone: hooks, plugins and MCP servers stay out of a run.

## Plugins, tools and MCP servers

`settings.json` enables the plugins; they install from their own marketplaces. My plugins include: [Development](https://github.com/mischasigtermans/skills) (Code skills and the sharpen gate), [Writing](https://github.com/mischasigtermans/skills) (prose and mail), [Personas](https://github.com/mischasigtermans/claude-personas) (advisors like Taylor Otwell and Steve Jobs), [Parley](https://github.com/mischasigtermans/claude-parley) (projects and personas consult each other, alone or in a gathering), [Library](https://github.com/mischasigtermans/claude-library) (search my past Claude chats and sessions) and [Ralph](https://github.com/mischasigtermans/claude-ralph) (an autonomous build loop). From others: Laravel's [agent-skills](https://github.com/laravel/agent-skills) (`laravel`, `laravel-cloud`, `laravel-lsp`), Firecrawl as the web layer, [OpenSEO](https://github.com/every-app/open-seo), Claude Security, Security Guidance, the Rust and Swift language servers, and the built-in `cc-plugin-you-should-know`.

[clauset](https://github.com/mischasigtermans/clauset) runs several Claude Code accounts on this one `~/.claude`: every account shares these settings, rules, hooks and plugins, and `clauset switch` moves a running session to another account when the one it runs on nears its limit. The status line and two of the hooks in `settings.json` call it.

One more SessionStart hook registers each session with the Rex terminal app through its `rex` CLI. Without Rex it does nothing.

MCP servers live in `~/.claude.json`, outside this repo.

## Borrow one

A rule drops in with a one-liner:

```bash
curl -fsSL https://raw.githubusercontent.com/mischasigtermans/dotclaude/main/rules/orchestration.md -o ~/.claude/rules/orchestration.md
```

A hook needs its file and its entry in `settings.json`. The status line needs `npx ccstatusline` set to show the context-percentage widget alone, since the wrapper reads its whole output as one number, and clauset for the account name.

## What stays out

The `.gitignore` is a whitelist: anything not listed stays out. No `settings.local.json`, plugin caches, memory, project data, logs, tokens or session history, and no skills: mine live in the plugin, and what a tool installs or a licence keeps private stays local. To add a file, whitelist it explicitly.

Public instructions hold reusable preferences and methods. Project decisions belong in their own guidelines; local routing and private context stay ignored. [`scope-gate.py`](hooks/scope-gate.py) reminds the author to check that boundary. The shell guard covers common direct commands and wrappers; it is not a complete shell parser or a security sandbox.

## Further reading

- [Every setting in my Claude Code config, explained](https://mischa.sigtermans.me/thought/my-claude-code-settings)
- [How I saved 4.7 billion tokens with a Claude Code hook](https://mischa.sigtermans.me/thought/how-i-saved-billions-of-tokens-with-a-claude-code-hook)
- [How I set up my Claude Code status line](https://mischa.sigtermans.me/thought/how-i-set-up-my-claude-code-status-line)
- [I stopped running agent teams and moved everything to Solo](https://mischa.sigtermans.me/thought/i-stopped-running-agent-teams-and-moved-to-solo): the reasoning behind the Solo tier in `orchestration.md`
- [How I made my Claude Code projects call each other](https://mischa.sigtermans.me/thought/how-i-made-my-claude-code-projects-call-each-other)
- [Taylor is still immortal, but now he remembers](https://mischa.sigtermans.me/thought/taylor-is-still-immortal-but-now-he-remembers)
- [My simplified Ralph loop setup for Claude Code](https://mischa.sigtermans.me/thought/my-simplified-ralph-loop-setup-for-claude-code)

## Credits

- [Mischa Sigtermans](https://github.com/mischasigtermans)
- The rules in CLAUDE.md on changes that trace to the request, the minimum implementation and a check for every step come from [Andrej Karpathy's notes on LLM coding](https://x.com/karpathy/status/2015883857489522876), via [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills).
- The hook set and its tests take their shape from [affaan-m/ECC](https://github.com/affaan-m/ECC).
- `rtk-rewrite.sh` is the hook [rtk](https://github.com/rtk-ai/rtk) generates.

## License

MIT. See [LICENSE](LICENSE). `hooks/rtk-rewrite.sh` is rtk's generated hook, under rtk's Apache License 2.0.
