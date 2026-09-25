# DotClaude

My personal Claude Code setup. Public for two reasons: I want to redeploy it on a new machine, and others might find ideas worth borrowing.

This isn't a template to clone wholesale. The voice rules, project paths, and bio reference me specifically. Read the parts that interest you, copy patterns into your own setup.

## Layout

- **CLAUDE.md**: the agent. How it talks, how it codes. Always on.
- **rules/**: context that loads on its own. Most load every session; `ui.md` and `laravel.md` carry `paths:` frontmatter and load only when Claude reads a matching file.
- **skills/**: behaviour for a class of task, loaded when the ask matches or when I type the slash command.
- **hooks/**: what prose can't enforce. My most frequent corrections were things CLAUDE.md already said, so the recurring ones are hooks.

Rules pay their token cost every session, skills only when invoked, hooks never.

## Rules

- **[`projects.md`](rules/projects.md)**: where my projects live, so Claude checks those paths first when I name one.
- **[`rtk.md`](rules/rtk.md)**: a hook rewrites shell commands through rtk; which output it condenses and how to bypass it.
- **[`orchestration.md`](rules/orchestration.md)**: which harness parallel work runs through (inline, subagents, Workflow, Solo), how sessions talk to each other, and that whoever delegates collects.
- **[`second-opinions.md`](rules/second-opinions.md)**: when to ask a persona, a peer project or a [Parley](https://github.com/mischasigtermans/claude-parley) gathering unprompted, and the gates every review question carries.
- **[`ui.md`](rules/ui.md)**: the bar every UI change meets without being asked. Mobile-first, dark variants, Flux controls, ui.sh guidelines for anything new.
- **[`laravel.md`](rules/laravel.md)**: Pint on the Laravel preset, never `--dirty` or `--blade`, Flux Pro activation, and what to leave unchecked at `boost:install`. Loads on any PHP file, so a new project needs no setup.

## Skills

| Skill | What it does |
| --- | --- |
| [`ui`](skills/ui/SKILL.md) | Builds and refines UI with the ui.sh guidelines, fetched live: new UI, variants, responsive, dark mode, components, Tailwind cleanup, craft |
| [`motion`](skills/motion/SKILL.md) | Anything that moves: name it, find it, review it, plan it |
| [`sharpen`](skills/sharpen/SKILL.md) | Diagnoses AI-slop in a draft, rewrites on my word; self-checks Claude's own copy |
| [`repo-docs`](skills/repo-docs/SKILL.md) | House style for READMEs, CHANGELOGs, commits, versioning and repo boilerplate |
| [`finish`](skills/finish/SKILL.md) | The round a change makes before it's committed: simplify, review, format, test, look |
| [`handoff`](skills/handoff/SKILL.md) | Hands a full session to a fresh one through a Solo scratchpad |
| [`solo`](skills/solo/SKILL.md) | Operates [Solo](https://soloterm.com), my terminal harness, via its MCP server |
| [`team-update`](skills/team-update/SKILL.md) | A 'Shipped' update from what actually landed |
| [`laravel-forge`](skills/laravel-forge/SKILL.md) | Operates Forge servers and sites via the `forge` CLI |
| [`cloud-database`](skills/cloud-database/SKILL.md) | Copies a Laravel Cloud database between environments without the two traps |
| [`devnomads`](skills/devnomads/SKILL.md) | Operates DevNomads infrastructure via `dncli` |
| [`bear`](skills/bear/SKILL.md) | How I format and tag notes in Bear |
| [`mail`](skills/mail/SKILL.md) | Composing Apple Mail drafts without mojibake |

The ui skill holds no ui.sh content. It fetches it from the ui.sh MCP server at run time, so it needs a ui.sh licence and its MCP server to work.

## Hooks

| Hook | Event | What it does |
| --- | --- | --- |
| [`rtk-rewrite.sh`](hooks/rtk-rewrite.sh) | PreToolUse Bash | Rewrites commands through rtk for smaller output |
| [`bash-guard.py`](hooks/bash-guard.py) | PreToolUse Bash | Denies `git add -A`/`.`, `commit -a`, commit trailers, `--no-verify`, tag creation, `pint --dirty` |
| [`config-protect.py`](hooks/config-protect.py) | PreToolUse Edit/Write | Denies edits to Pint, PHPStan, Prettier and ESLint config: fix the code, not the linter |
| [`ui-gate.py`](hooks/ui-gate.py) | PreToolUse Edit/Write | Sends `rules/ui.md` with the first UI edit when no UI file was read (the path rule didn't load) |
| [`memory-gate.py`](hooks/memory-gate.py) | PreToolUse Edit/Write | Denies feedback memories (a rule belongs in CLAUDE.md, `rules/` or the repo guideline) and status in project memories |
| [`php-format.py`](hooks/php-format.py) | PostToolUse, Stop | Notes edited PHP files (never Blade); at Stop runs Pint on them and PHPStan, blocks on errors |
| [`dash-lint.py`](hooks/dash-lint.py) | PostToolUse Edit/Write | Flags em dashes, en dashes and middle dots in copy |
| [`sharpen-gate.py`](hooks/sharpen-gate.py) | Stop | After 150+ words of prose in files or drafts, sends Claude through `sharpen` before it stops |

`bash hooks/tests/run.sh` pipes fake payloads through every hook and asserts on the output. All hooks fail open: an internal error never blocks a tool call.

## Plugins and MCP servers

`settings.json` enables the plugins; they install from their own marketplaces. Four I built: [Personas](https://github.com/mischasigtermans/claude-personas) (advisors like Taylor Otwell and Steve Jobs), [Parley](https://github.com/mischasigtermans/claude-parley) (projects and personas consult each other, alone or in a gathering), [Library](https://github.com/mischasigtermans/claude-library) (search my past Claude chats and sessions) and [Ralph](https://github.com/mischasigtermans/claude-ralph) (an autonomous build loop). From others: Laravel's [agent-skills](https://github.com/laravel/agent-skills) (`laravel`, `laravel-cloud`), Firecrawl as the web layer, Codex, Cloudflare, Claude Security and language servers.

MCP servers live in `~/.claude.json`, outside this repo.

## Borrow one

Single-file rules and skills drop in with a one-liner:

```bash
curl -fsSL https://raw.githubusercontent.com/mischasigtermans/dotclaude/main/rules/orchestration.md -o ~/.claude/rules/orchestration.md
```

Multi-file skills and the hooks need the directory: `git clone https://github.com/mischasigtermans/dotclaude /tmp/dc && cp -r /tmp/dc/skills/motion ~/.claude/skills/`. Hooks also need their entry in `settings.json`.

## What stays out

The `.gitignore` is a whitelist: anything not listed stays out. No `settings.local.json`, plugin caches, memory, project data, logs, tokens or session history, and no claude.ai-synced skills. To add a file, whitelist it explicitly.

## Further reading

- [My Claude Code settings](https://mischa.sigtermans.me/thought/my-claude-code-settings)
- [How I saved billions of tokens with a Claude Code hook](https://mischa.sigtermans.me/thought/how-i-saved-billions-of-tokens-with-a-claude-code-hook)
- [How I set up my Claude Code status line](https://mischa.sigtermans.me/thought/how-i-set-up-my-claude-code-status-line)
- [I stopped running agent teams and moved everything to Solo](https://mischa.sigtermans.me/thought/i-stopped-running-agent-teams-and-moved-to-solo)
- [How I made my Claude Code projects call each other](https://mischa.sigtermans.me/thought/how-i-made-my-claude-code-projects-call-each-other)
- [Taylor is still immortal, but now he remembers](https://mischa.sigtermans.me/thought/taylor-is-still-immortal-but-now-he-remembers)
- [My simplified Ralph loop setup for Claude Code](https://mischa.sigtermans.me/thought/my-simplified-ralph-loop-setup-for-claude-code)

## Credits

- Surgical changes, Simplicity and Success criteria in CLAUDE.md come from [Andrej Karpathy's notes on LLM coding](https://x.com/karpathy/status/2015883857489522876), via [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills).
- The ui skill runs on [ui.sh](https://ui.sh) by [Adam Wathan](https://x.com/adamwathan) and [Steve Schoger](https://x.com/steveschoger).
- `motion/` and `ui/feel.md` consolidate [Emil Kowalski](https://emilkowal.ski)'s [skills](https://github.com/emilkowalski/skills) (MIT); `ui/libraries.md` is his `pick-ui-library`.
- `ui/surfaces.md`, `ui/typography.md` and parts of `motion/standards.md` come from [Jakub Krehel](https://jakub.kr)'s [make-interfaces-feel-better](https://github.com/jakubkrehel/make-interfaces-feel-better).
- `sharpen/` is [petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop), restructured to analyse first.
- The hook set and its tests take their shape from [affaan-m/ECC](https://github.com/affaan-m/ECC).

## License

MIT. See [LICENSE](LICENSE).
