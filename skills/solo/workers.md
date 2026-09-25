# Workers and Coordination

## Lead + worker orchestration

This is the headline workflow. Solo owns all parallel work: it persists, supports cross-lab agents, and shows up in the user's IDE.

Phases (skip phases that don't apply, don't skip phases that do):

1. **Interview** — one lead agent asks one question at a time until it can write a plan. Don't spawn workers before you understand the goal.
2. **Plan** — `scratchpad_write` the orchestration plan. Concise but self-contained: workers must not need to re-ask the lead for background.
3. **Todos** — `todo_create` per lane with `todo_set_blockers` for dependencies. Verification todos blocked by implementation. Integration todos blocked by worker handoffs.
4. **Dispatch** — `list_agent_tools` to see what's installed. `spawn_agent` for worker agents on *independent, unblocked* lanes only (`spawn_process` is for non-agent processes like dev servers; don't mix them up). Each worker gets a narrow prompt: objective, scratchpad reference, owned files, what NOT to touch, handoff expectations. Keep reusable worker briefs in a scratchpad so you don't retype them.
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
- General coding agents for bounded repo edits

Child agents don't inherit judgment from the parent. Each one needs a narrow assignment, explicit context boundaries, and concrete handoff expectations.

## Model choice per worker

Solo has one Claude Code tool, `Claude Code`, and it starts on the default model of the user's Claude Code config. Pick the model per launch: `spawn_agent(..., extra_args=["--model", "sonnet"])`. Well-specified implementation lanes go to Sonnet; lanes that need judgment (contract design, measurements someone will decide on) keep the default. Put the model in the process name when it isn't the default, so the process list says what is running.

## Slash commands in a worker

A worker can't invoke an MCP prompt such as `/mcp__laravel-boost__laravel-code-simplifier` itself: those are typed by a user. Have the brief tell the worker to stop with a fixed last line (`READY FOR SIMPLIFIER`) and type the command into its session with `send_input`. Project skills (`/sync-docs`) it can run through its own Skill tool.

Long text never goes through `send_input`: the TUI drops the head of a long paste, and a 1 kB brief arrives as its last line. Put the brief in a scratchpad or a file and send one line that points at it.

Lanes sharing one checkout commit by pathspec, and a pathspec commit takes the whole file as it stands. A file every lane appends to (an enum, `routes/web.php`, a lang file) gets one owner per round, or the lead commits it once every lane's hunk is in. Append-only edits at the end keep the hunks apart.

`send_input` to a busy worker surfaces inside the tool result of whatever command it was running, and a careful worker treats that as injected text and ignores it. Send only to an idle worker, or interrupt first with `send_input(bytes=[27])` and then type, and say in the message that the interrupt was yours.

## Coordination primitives

- **Messages** — questions, handoffs and answers to a worker or another session go through native `SendMessage` to its `ListAgents` name, with `notify_when_idle` instead of polling. `rules/orchestration.md` holds the rule; `send_input` stays for typing a slash command into an idle worker.

- **Locks** — `lock_acquire` on shared resources before editing, `lock_release` when done. `lock_status` to see who holds what. Use when more than one agent could plausibly touch the same area. Solo also has todo-level locks (`todo_lock`) signaling active work on a specific todo.
- **Timers** — `timer_set` for "ping back in N minutes." `timer_fire_when_idle_any` to wake the lead as soon as any worker goes idle. `timer_fire_when_idle_all` when integration must wait for the whole batch. `timer_pause` / `timer_resume` / `timer_cancel` / `timer_list` for housekeeping. A worker waiting on a long shell command reads as idle, and an idle timer on an already-idle process is refused as `already_satisfied`: read the output before treating idle as done, and watch such a worker with `timer_set` instead.
- **KV store** — `kv_set` / `kv_get` / `kv_list` / `kv_delete` for small project-scoped JSON state (run counters, last-seen values, config flags). Reach for it rarely; usually a scratchpad section or todo comment is better. Disabled by default; if KV tools aren't visible, the user hasn't enabled them.

