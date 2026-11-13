---
name: solo
description: "Solo (soloterm.com), a terminal harness for agents and dev processes, operated via its MCP server: long-running processes, cross-session scratchpads and todos, Solo workers, locks and timers. Use for work in another repo, work that outlives a session, non-Claude workers and processes that outlive one tool call. Triggers on 'solo', 'in Solo', 'spawn a Solo worker', 'tail the dev server', 'put this in a scratchpad', 'save this as a todo', 'wake me when'."
---

# Solo

Solo runs terminals and agents outside the chat and holds what outlives a session. It's the right tool for:

- Work in another repo: a worker spawned in that repo's Solo project loads that repo's own instructions and skills.
- Work that must survive a session or a restart: todos, scratchpads, timers.
- Non-Claude workers (Codex, Grok) and anything else that runs longer than one tool call.

Don't use Solo for parallelism alone: each worker is a full CLI process with its own MCP stack. Read-only fan-out in your own repo is a native subagent, parallel edits there are an agent team. A single edit, a one-off grep or a command that finishes in seconds stays in Bash and Edit.

## Session bootstrap

Before anything else, in this order:

1. `list_projects`: auto-selects if only one exists.
2. `select_project` if more than one, or pass `project_id` on every project-scoped call. `get_project` reads a project's metadata. Don't create, rename or delete a project on the user's behalf (`create_project`, `rename_project`, `delete_project`): suggest it and let them confirm.
3. `whoami` to see your process_id, actor_id and effective scope. A session Solo launched is normally identified automatically.
4. `identify_session` only when `whoami` can't identify a Solo-managed child process: pass your own `SOLO_PROCESS_ID` as an identity assertion. Never use it to target another process, and never in a session Solo didn't launch: a false identity confuses the process tree.
5. `help` with a topic when you need to look up a capability.

Skip steps that obviously don't apply. Don't bootstrap for a single read-only query.

## Load

| For | Read |
| --- | --- |
| Dev servers, watchers, log tails, solo.yml stacks | `processes.md` |
| Scratchpads, todos, what belongs in auto-memory instead | `state.md` |
| Spawning workers, cross-lab agents, messages, locks, timers | `workers.md` |

## Safety rules

1. Never run `stop_all_commands` or `restart_all_commands` without confirmation. It hits everything in the project.
2. Don't spawn workers that compete for the same files. Split by directory, module or repo. If you can't split, run them one after another.

## Keep this skill fresh

Solo changes fast. On any of these signals, stop and tell the user the skill probably needs an update:

- An `mcp__solo__*` tool is available that this skill doesn't mention
- A tool this skill references comes back as unavailable or errors with InputValidationError
- `help` returns a topic or capability not covered here
- A tool this skill names has changed its name

Suggest the update in one line; don't silently rewrite the skill.

## Reference

- Docs: https://soloterm.com/docs
- MCP tools overview: https://soloterm.com/docs/mcp-tools/overview
- Orchestration: https://soloterm.com/docs/workflows/agent-orchestration
- Agents spawning agents: https://soloterm.com/docs/workflows/agents-spawning-agents
- Scratchpads and todos: https://soloterm.com/docs/workflows/scratchpads-and-todos
- In-session lookup: `help` MCP tool with a topic (e.g. `help(topic="timers")`, `help(topic="coordination")`, `help(topic="solo.yml")`)
