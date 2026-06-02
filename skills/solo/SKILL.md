---
name: solo
description: "Operate Solo (soloterm.com), Mischa's default terminal harness, via its MCP server. Use for managing long-running processes (dev servers, watchers, log tails), spawning cross-lab worker agents (Codex, Gemini, etc.), persisting context across sessions via scratchpads and todos, and coordinating with locks and timers. Trigger on 'solo', 'spawn an agent', 'kick off X in parallel', 'tail the dev server', 'put this in a scratchpad', 'save this as a todo', 'lock the file', 'wake me when', or whenever work needs durable cross-session state, output kept out of the chat buffer, or non-Claude workers. Default to Solo for orchestration over Claude Code teams; teams remain the fallback for purely in-conversation parallelism."
---

# Solo

Solo is Mischa's default IDE. It owns long-running processes, persists scratchpads and todos across sessions, and orchestrates worker agents from any lab. All capabilities are exposed via the `mcp__solo__*` tool family.

## Session bootstrap

Before anything else, in this order:

1. `list_projects` — auto-selects if only one exists
2. `select_project` if more than one, or pass `project_id` on every call
3. `identify_session` if this session was launched by Solo (uses `SOLO_PROCESS_ID` to associate the MCP session with its Solo-managed process)
4. `whoami` to confirm process_id, actor_id, and effective scope
5. `help` (with a topic) when you need to look up a capability

Project CRUD lives in `create_project` / `rename_project` / `delete_project` / `get_project`. Don't create or delete a project on the user's behalf; suggest it and let them confirm.

Skip steps that obviously don't apply. Don't bootstrap for a single read-only query.

## Process management over Bash backgrounding

If a command outlives one tool call (dev server, watcher, log tail, queue worker), put it in Solo, not in `Bash(run_in_background: true)`.

- `spawn_process` / `start_process` — start it
- `wait_for_bound_port` — block until the server is actually listening
- `get_process_output` — read recent output
- `search_output` with a regex — find specific lines without dumping the whole buffer
- `clear_output` before a fresh run so old logs don't confuse you
- `restart_process` / `stop_process` / `close_process` — lifecycle
- `get_process_ports` / `services_list` — what's listening where

Solo keeps the process visible in the user's IDE between sessions. Bash backgrounding doesn't.

**Output hygiene:** never read the full buffer when a `search_output` regex would do. The user has to scroll past everything you read.

## Scratchpads vs auto-memory

These don't overlap. Don't let them.

- **Auto-memory** (`~/.claude/projects/.../memory/`) — stable facts about the user, project, feedback, references. Survives every session.
- **Solo scratchpad** — task-scoped working memory for *this* piece of work that needs to outlive compaction or be read by a worker agent.

When to write a scratchpad: investigation has more than ~3 findings, plan has more than ~3 steps, work will be handed to a worker, work might resume in a future session.

Structure (use these headings — agents scan them):

```
## Goal
## Current understanding
## Relevant files and commands
## Decisions
## Open questions
## Next actions
```

Tools:
- `scratchpad_write` — full write, revision-guarded
- `scratchpad_edit` — targeted edit without rewriting the whole pad
- `scratchpad_append` / `scratchpad_append_section` — append raw or under a specific heading
- `scratchpad_read` / `scratchpad_tail` — read full content or just the latest entries
- `scratchpad_find` — search across pads in the project
- `scratchpad_list`, `scratchpad_add_tags`, `scratchpad_archive`

Prefer `scratchpad_edit` / `scratchpad_append_section` over rewriting the whole pad. Don't `scratchpad_delete` unless the user asks.

## Todos vs TaskCreate

Don't mirror them. Pick one per piece of work.

- **TaskCreate** (Claude Code harness) — in-session checklist. Dies when the session ends. Use for "do these 4 things right now."
- **Solo todos** — survive sessions, support blockers, locks, comments, tags. Visible in the user's IDE. Use for anything that must outlive this conversation or be picked up by another agent.

Todos own:
- A concrete objective
- A scratchpad reference (heading or link), not duplicated context
- Blockers via `todo_set_blockers` / `todo_add_blocker` — turn a flat list into an orchestration plan
- Tags for lanes (`todo_add_tag`)
- Comments for handoffs (`todo_comment_create`) — changed files, tests run, remaining risk
- Locks (`todo_lock`) while actively working; release on handoff

Blockers and locks are project-scoped. `todo_transfer` preserves comments and completion state but clears them.

## Lead + worker orchestration

This is the headline workflow. Default to Solo for parallel work over Claude Code teams — Solo persists, supports cross-lab agents, and shows up in the user's IDE.

Phases (skip phases that don't apply, don't skip phases that do):

1. **Interview** — one lead agent asks one question at a time until it can write a plan. Don't spawn workers before you understand the goal.
2. **Plan** — `scratchpad_write` the orchestration plan. Concise but self-contained: workers must not need to re-ask the lead for background.
3. **Todos** — `todo_create` per lane with `todo_set_blockers` for dependencies. Verification todos blocked by implementation. Integration todos blocked by worker handoffs.
4. **Dispatch** — `list_agent_tools` to see what's installed. `spawn_agent` for worker agents on *independent, unblocked* lanes only (`spawn_process` is for non-agent processes like dev servers; don't mix them up). Each worker gets a narrow prompt: objective, scratchpad reference, owned files, what NOT to touch, handoff expectations. Reusable worker briefs belong in prompt templates (`create_prompt_template` / `list_prompt_templates` / `get_prompt_template` / `update_prompt_template` / `export_prompt_templates`) so you don't retype them.
5. **Monitor** — watch process state. `get_process_output` / `search_output` to read real output, not just summaries. `timer_set` / `timer_fire_when_idle_any` / `timer_fire_when_idle_all` to wake on worker idle.
6. **Maintain** — keep scratchpad and todos current as workers discover new context. Update blocked/unblocked. Comment on todos as state changes.
7. **Integrate** — one lane at a time. Inspect the actual diff. Run focused verification. Then unblock the next lane.
8. **Cleanup** — before `close_process` on a worker, capture handoff (changed files, tests, blockers, risk) in `todo_comment_create`. Inspect nested subagents before closing the parent.

**Anti-patterns:**
- Spawning workers before the interview is done
- Asking a worker to "solve the whole problem"
- Letting two workers edit the same files
- Trusting a worker's summary instead of reading its output
- Treating chat scrollback as the orchestration record — it isn't, the scratchpad is

## Cross-lab specialists

`list_agent_tools` first. Spawn the right tool per lane, not per session.

- Planning-heavy lead → fast implementation worker (Codex)
- Code-focused lead → docs/test/review worker (Gemini, Amp, OpenCode)
- Long-context review on a sprawling diff → whichever model has the bigger window
- Custom team agents → general coding agents for bounded repo edits

Child agents don't inherit judgment from the parent. Each one needs a narrow assignment, explicit context boundaries, and concrete handoff expectations.

## Coordination primitives

- **Locks** — `lock_acquire` on shared resources before editing, `lock_release` when done. `lock_status` to see who holds what. Use when more than one agent could plausibly touch the same area. Solo also has todo-level locks (`todo_lock`) signaling active work on a specific todo.
- **Timers** — `timer_set` for "ping back in N minutes." `timer_fire_when_idle_any` to wake the lead as soon as any worker goes idle. `timer_fire_when_idle_all` when integration must wait for the whole batch. `timer_pause` / `timer_resume` / `timer_cancel` / `timer_list` for housekeeping.
- **KV store** — `kv_set` / `kv_get` / `kv_list` / `kv_delete` for small project-scoped JSON state (run counters, last-seen values, config flags). Reach for it rarely; usually a scratchpad section or todo comment is better. Disabled by default; if KV tools aren't visible, the user hasn't enabled them.

## Safety rules

1. **Never `stop_all_commands` or `restart_all_commands` without confirmation.** It hits everything in the project.
2. **Capture worker handoffs before `close_process`.** Once the process is gone, its chat history is gone. The handoff must already be in a todo comment or scratchpad section.
3. **Don't spawn workers that compete for the same files.** Split by directory, module, or repo. If you can't split, run sequentially.
4. **Don't mirror TaskCreate and Solo todos.** Pick the right tool once, stick with it. Mirroring guarantees drift.
5. **Don't `scratchpad_delete` or `todo_delete` on the user's behalf.** Archive instead (`scratchpad_archive`, mark todo complete).
6. **`identify_session` only when actually launched by Solo.** Bogus identification confuses the process tree.
7. **Don't use Solo todos as a replacement for auto-memory.** Project facts go in memory; task work goes in todos.
8. **Don't `delete_project` or `delete_prompt_template` on the user's behalf.** Both are destructive and project-wide. Suggest and confirm.

## Keep this skill fresh

Solo iterates fast. If you notice any of these signals, stop and tell Mischa the skill probably needs an update:

- An `mcp__solo__*` tool is available that this skill doesn't mention
- A tool this skill references comes back as "no longer available" or errors with InputValidationError
- `help` returns a topic or capability not covered here
- Tool names change shape (e.g. a rename like `bind_session_process` → `identify_session`)

Suggest the update; don't silently rewrite the skill. A one-line "Solo's toolset has drifted — want me to refresh `~/.claude/skills/solo/SKILL.md`?" is enough.

## When NOT to use Solo

- Single-file edit, one-off grep, command that finishes in seconds — Bash and Edit are fine.
- In-conversation throwaway parallelism where nothing needs to persist — Claude Code teams are fine.
- Storing stable user/project facts — auto-memory, not scratchpads.

## Reference

- Docs: https://soloterm.com/docs
- MCP tools overview: https://soloterm.com/docs/mcp-tools/overview
- Orchestration: https://soloterm.com/docs/workflows/agent-orchestration
- Agents spawning agents: https://soloterm.com/docs/workflows/agents-spawning-agents
- Scratchpads and todos: https://soloterm.com/docs/workflows/scratchpads-and-todos
- In-session lookup: `help` MCP tool with a topic (e.g. `help(topic="timers")`, `help(topic="coordination")`, `help(topic="solo.yml")`)
