# DotClaude

My personal Claude Code setup, shared so you can see how I work with it and borrow what's useful.

This isn't a template to clone wholesale. The voice rules, project paths, and bio reference me specifically. Read the parts that interest you, copy patterns into your own setup. It holds how I work in every project and nothing about any one of them.

## Layout

- **CLAUDE.md**: the agent. How it talks, how it codes. Always on.
- **rules/**: context that loads on its own. Most load every session; `ui.md` and `laravel.md` carry `paths:` frontmatter and load only when Claude reads a matching file.
- **skills/**: behaviour for a class of task, loaded when the ask matches or when I type the slash command.
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

Thirteen skills, each a folder in `skills/` with a `SKILL.md`. Claude loads one when the ask matches its description, or when I type its name.

| Skill | What it does |
| --- | --- |
| [finish](skills/finish/SKILL.md) | Takes a finished change through one round before its commit: simplify, review twice, docs, format, tests, a look at the UI, a report |
| [handoff](skills/handoff/SKILL.md) | Writes a briefing for a fresh session and the one-line prompt that points at it |
| [sync-docs](skills/sync-docs/SKILL.md) | Finds where the docs, guidelines and copy have drifted from the code, with `file:line` evidence, and fixes on my word |
| [repo-docs](skills/repo-docs/SKILL.md) | My standard for READMEs, changelogs, commit messages, versions and `.github` files |
| [sharpen](skills/sharpen/SKILL.md) | Names each AI pattern in a draft, quotes the line and gives the fix, then rewrites on my word. On Claude's own copy it fixes without asking |
| [mail](skills/mail/SKILL.md) | Drafts, replies and forwards in Apple Mail: a plain body, anything with accents or formatting as an attachment, and a check of the draft before it goes |
| [ui](skills/ui/SKILL.md) | Craft for surfaces, typography and feel, which library to pick, and how to review an interface |
| [motion](skills/motion/SKILL.md) | Names an effect, finds what should animate, reviews animation code and plans motion work |
| [design-pack](skills/design-pack/SKILL.md) | Fetches the ui.sh design guidelines through its MCP server and says how to work with them |
| [solo](skills/solo/SKILL.md) | Operates Solo: long-running processes, scratchpads and todos, workers, locks and timers |
| [panel](skills/panel/SKILL.md) | Runs independent reviewers on Claude, Codex or Grok who cross-examine each other and sign one report |
| [laravel-forge](skills/laravel-forge/SKILL.md) | Deploys, logs, environment files and service commands through the Forge CLI |
| [cloud-database](skills/cloud-database/SKILL.md) | Copies a Laravel Cloud database between environments and guards against its two traps: the wrong direction, and orphan tables that break the next migrate |

To take one, copy its folder into your own `~/.claude/skills/`, or let the [skills CLI](https://github.com/vercel-labs/skills) do it:

```bash
npx skills add mischasigtermans/dotclaude --skill sharpen
```

A skill brings no tools of its own. solo and panel need [Solo](https://soloterm.com), laravel-forge the `forge` CLI, cloud-database the `cloud` CLI and `mysql`, mail the macuse Apple Mail connector, and design-pack a [ui.sh](https://ui.sh) account with its MCP server connected. finish uses the `laravel@laravel` plugin for its simplify step, and Personas with Parley for its review.

sharpen and mail don't need Claude Code. Claude Desktop takes them as uploaded skills.

On my machine `skills/` also holds what tools put there: clauset's two skills, the one from Rex, and the skills Claude syncs from claude.ai. Those stay out of the repo.

## Hooks

| Hook | Event | What it does |
| --- | --- | --- |
| [`rtk-rewrite.sh`](hooks/rtk-rewrite.sh) | PreToolUse Bash | Rewrites commands through rtk for smaller output |
| [`bash-guard.py`](hooks/bash-guard.py) | PreToolUse Bash | Denies `git add -A`/`.`, `commit -a`, commit trailers, `--no-verify`, a `core.hooksPath` override, any `git tag` that writes, `pint --dirty` and `--blade`, `pkill` or `killall` on a test runner, `herd secure` |
| [`config-protect.py`](hooks/config-protect.py) | PreToolUse Edit/Write | Denies edits to Pint, PHPStan, Prettier and ESLint config: fix the code, not the linter |
| [`ui-gate.py`](hooks/ui-gate.py) | PreToolUse Edit/Write | Sends `rules/ui.md` with the first UI edit when no UI file was read (the path rule didn't load) |
| [`memory-gate.py`](hooks/memory-gate.py) | PreToolUse Edit/Write | Denies feedback memories (a rule belongs in the repo's guideline, or here when it's how I work everywhere) and status in project memories |
| [`scope-gate.py`](hooks/scope-gate.py) | PreToolUse Edit/Write | Reminds edits to the setup and plugin skills to check scope, once per home session or per distinct edit from a project. Retrying passes; it does not validate the text. Local tool-managed skills are excluded |
| [`sharpen-gate.py`](hooks/sharpen-gate.py) | Stop | Sends Claude through the sharpen skill once it wrote 150 or more words of prose to `.md`, `.mdx` or `.txt` files in a turn |
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

`settings.json` enables the plugins; they install from their own marketplaces. My plugins include: [Personas](https://github.com/mischasigtermans/claude-personas) (advisors like Taylor Otwell and Steve Jobs), [Parley](https://github.com/mischasigtermans/claude-parley) (projects and personas consult each other, alone or in a gathering), [Library](https://github.com/mischasigtermans/claude-library) (search my past Claude chats and sessions) and [Ralph](https://github.com/mischasigtermans/claude-ralph) (an autonomous build loop). From others: Laravel's [agent-skills](https://github.com/laravel/agent-skills) (`laravel`, `laravel-cloud`, `laravel-lsp`), Firecrawl as the web layer, [OpenSEO](https://github.com/every-app/open-seo), Claude Security, Security Guidance, the Rust and Swift language servers, and the built-in `cc-plugin-you-should-know`.

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

The `.gitignore` is a whitelist: anything not listed stays out. No `settings.local.json`, plugin caches, memory, project data, logs, tokens or session history, and of the skills only my own: what a tool installs or syncs stays local. To add a file, whitelist it explicitly.

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
- sharpen started from [Peter Yang](https://github.com/petergyang)'s [no-ai-slop](https://github.com/petergyang/no-ai-slop). ui and motion started from the skills [Emil Kowalski](https://github.com/emilkowalski) and [Jakub Krehel](https://github.com/jakubkrehel) published. The text and the examples here are written new.
- `rtk-rewrite.sh` is the hook [rtk](https://github.com/rtk-ai/rtk) generates.

## License

MIT. See [LICENSE](LICENSE). `hooks/rtk-rewrite.sh` is rtk's generated hook, under rtk's Apache License 2.0.
