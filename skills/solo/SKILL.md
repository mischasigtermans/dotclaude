---
name: solo
description: "Solo (soloterm.com), Mischa's terminal harness, operated via its MCP server: long-running processes, cross-session scratchpads and todos, Solo workers, locks and timers. Triggers on 'solo', 'in Solo', 'spawn a Solo worker', 'tail the dev server', 'put this in a scratchpad', 'save this as a todo', 'wake me when'. See rules/orchestration.md for when Solo is the right tier at all."
---

# Solo

Mischa's terminal harness. See `~/.claude/rules/orchestration.md` for when Solo is the right tier at all.

## Session bootstrap

Before anything else, in this order:

1. `list_projects` — auto-selects if only one exists
2. `select_project` if more than one, or pass `project_id` on every call
3. `identify_session` if this session was launched by Solo (uses `SOLO_PROCESS_ID` to associate the MCP session with its Solo-managed process)
4. `whoami` to confirm process_id, actor_id, and effective scope
5. `help` (with a topic) when you need to look up a capability

Project CRUD lives in `create_project` / `rename_project` / `delete_project` / `get_project`. Don't create or delete a project on the user's behalf; suggest it and let them confirm.

Skip steps that obviously don't apply. Don't bootstrap for a single read-only query.

## Load

| For | Read |
| --- | --- |
| Dev servers, watchers, log tails, solo.yml stacks | `processes.md` |
| Scratchpads, todos, what belongs in auto-memory instead | `state.md` |
| Spawning workers, cross-lab agents, locks, timers | `workers.md` |

## Safety rules

1. **Never `stop_all_commands` or `restart_all_commands` without confirmation.** It hits everything in the project.
2. **Capture worker handoffs before `close_process`.** Once the process is gone, its chat history is gone. The handoff must already be in a todo comment or scratchpad section.
3. **Don't spawn workers that compete for the same files.** Split by directory, module, or repo. If you can't split, run sequentially.
4. **Don't mirror TaskCreate and Solo todos.** Pick the right tool once, stick with it. Mirroring guarantees drift.
5. **Don't `scratchpad_delete` or `todo_delete` on the user's behalf.** Archive instead (`scratchpad_archive`, mark todo complete).
6. **`identify_session` only when actually launched by Solo.** Bogus identification confuses the process tree.
7. **Don't use Solo todos as a replacement for auto-memory.** Project facts go in memory; task work goes in todos.
8. **Don't `delete_project` on the user's behalf.** It is destructive and project-wide. Suggest and confirm.

## Keep this skill fresh

Solo iterates fast. If you notice any of these signals, stop and tell Mischa the skill probably needs an update:

- An `mcp__solo__*` tool is available that this skill doesn't mention
- A tool this skill references comes back as "no longer available" or errors with InputValidationError
- `help` returns a topic or capability not covered here
- Tool names change shape (e.g. a rename like `bind_session_process` → `identify_session`)

Suggest the update; don't silently rewrite the skill. A one-line "Solo's toolset has drifted — want me to refresh `~/.claude/skills/solo/SKILL.md`?" is enough.

## When NOT to use Solo

- Single-file edit, one-off grep, command that finishes in seconds — Bash and Edit are fine.
- In-conversation throwaway parallelism where nothing needs to persist: native read-only subagents are fine.
- Storing stable user/project facts — auto-memory, not scratchpads.

## Reference

- Docs: https://soloterm.com/docs
- MCP tools overview: https://soloterm.com/docs/mcp-tools/overview
- Orchestration: https://soloterm.com/docs/workflows/agent-orchestration
- Agents spawning agents: https://soloterm.com/docs/workflows/agents-spawning-agents
- Scratchpads and todos: https://soloterm.com/docs/workflows/scratchpads-and-todos
- In-session lookup: `help` MCP tool with a topic (e.g. `help(topic="timers")`, `help(topic="coordination")`, `help(topic="solo.yml")`)
