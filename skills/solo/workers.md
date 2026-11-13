# Workers and Coordination

## Lead + worker orchestration

This is Solo's main workflow. Solo owns parallel work outside the lead's repo: it persists, runs agents from other labs (Codex, Grok) and shows up in the user's IDE.

Run every phase that applies and skip the rest:

1. **Interview**: one lead agent asks one question at a time until it can write a plan. Don't spawn workers before you understand the goal.
2. **Plan**: `scratchpad_create` the orchestration plan. Keep it short and self-contained, so no worker has to ask the lead for background.
3. **Todos**: `todo_create` per lane, one worker's share of the work, with `todo_set_blockers` for dependencies. Block verification todos on implementation and integration todos on worker handoffs.
4. **Dispatch**: `list_agent_tools` to see what's installed. `spawn_agent` for worker agents, only on lanes that are independent and unblocked (`spawn_process` is for non-agent processes like dev servers; don't mix them up). `working_dir` starts the worker in an existing folder, such as a sibling worktree, and `prompt` sends its first message: the answer's `prompt_delivery` says `delivered` or `pending`. Each worker gets a narrow prompt: objective, scratchpad reference, owned files, what not to touch, handoff expectations. Keep reusable worker briefs in a scratchpad so you don't retype them.
5. **Monitor**: watch process state. `get_process_output` / `search_output` to read the output itself, not a summary. `timer_set` / `timer_fire_when_idle_any` / `timer_fire_when_idle_all` to wake on worker idle.
6. **Maintain**: keep scratchpad and todos current as workers discover new context. Update blocked/unblocked. Comment on todos as state changes.
7. **Integrate**: one lane at a time. Inspect the actual diff. Run focused verification. Then unblock the next lane.
8. **Cleanup**: before `close_process` on a worker, capture its handoff (changed files, tests, blockers, risk) in `todo_comment_create`: once the process is gone, its chat history is gone. Inspect nested subagents before closing the parent.

**Anti-patterns:**
- Spawning workers before the interview is done
- Asking a worker to 'solve the whole problem'
- Trusting a worker's summary instead of reading its output
- Treating chat scrollback as the orchestration record instead of the scratchpad

## Cross-lab specialists

`list_agent_tools` shows which agent CLIs the user has configured. Spawn the right tool per lane, not per session.

- Planning-heavy lead → fast implementation worker (Codex)
- Code-focused lead → docs, test or review worker from another lab
- Long-context review on a sprawling diff → whichever model has the bigger window
- General coding agents for bounded repo edits

A Claude worker spawned into a directory Claude Code hasn't trusted on this machine waits at the 'trust this folder' dialog, with 'No, exit' preselected. Solo holds every message to it until the dialog is answered: `prompt_delivery` and `get_process_status` show `pending` with the reason `program_blocked`. The answer is the user's: hand them the step, or close the worker and give the lane to the repo's own idle session.

Every line to a Codex or Grok worker goes through `send_input` (Messages, below). Read the screen before the first line and after every turn:

- Codex can open its update dialog at start, with '1. Update now' preselected and 'enter continue, esc skip' as its keys: any line ending in Enter, `2` included, runs `npm install -g @openai/codex`. Start a Codex worker without `prompt`: Solo holds a first message for the dialogs it knows, and its changelog doesn't name this one. Send `bytes=[27]` (Escape) alone, then read the screen again.
- At its rate-limit warning Codex offers to switch to a smaller model. Answer to keep the model the lane was given, with `intent: "interaction"` (Messages, below).
- Grok asks to trust every folder it hasn't seen. That answer is the user's.
- A Grok turn can end right after a context compaction with 'No prompt to retry', the work unfinished. Send a line that tells it to continue the same assignment.

Child agents don't inherit judgment from the parent. Each one needs a narrow assignment, explicit context boundaries, and concrete handoff expectations.

## Model choice per worker

`list_agent_tools` can list more than one Claude Code tool (one per account, where the user runs several). Pick the one that fits the lane. A Claude tool starts on the default model of the Claude Code config it runs under; set the model per launch: `spawn_agent(..., extra_args=["--model", "sonnet"])`. Well-specified implementation lanes go to Sonnet; lanes that need judgment (contract design, measurements someone will decide on) keep the default. Put the model in the process name when it isn't the default, so the process list says what's running.

## Slash commands in a worker

A worker can't invoke an MCP prompt such as `/mcp__laravel-boost__laravel-code-simplifier` itself: a user types those. Have the brief tell the worker to stop with a fixed last line (`READY FOR SIMPLIFIER`) and type the command into its session with `send_input`. A skill, such as `sync-docs` or one of the project's own, it runs through its own Skill tool.

A brief goes in a scratchpad or a file, and the message is one line that points at it: the worker can read it again after a compaction, and so can whoever resumes the lane. A message of a dozen lines does arrive whole, as one turn.

Lanes sharing one checkout commit by pathspec, and a pathspec commit takes the whole file as it stands. A file every lane appends to (an enum, `routes/web.php`, a lang file) gets one owner per round, or the lead commits it once every lane's hunk is in. Append-only edits at the end keep the hunks apart.

## Coordination primitives

- **Messages**: questions, handoffs and answers to a Claude worker or another Claude session go through native `SendMessage` to its `ListAgents` name, with `notify_when_idle` instead of polling. Codex and Grok workers don't appear in `ListAgents`, so every line to them goes through `send_input`; for a Claude worker, `send_input` is only for typing a slash command. Text you send arrives as `[Solo MCP input from <actor> (process #N)]` and then your text, so a worker can tell it from the user's typing. `send_input` to a busy worker surfaces inside the tool result of whatever command it was running, and a careful worker treats that as injected text and ignores it. Send only to an idle worker, or interrupt first with `send_input(bytes=[27])` and then type, and say in the message that the interrupt was yours. A line you send is a message: Solo queues it behind timers and holds it while the user types. An answer to a dialog on the worker's screen is `intent: "interaction"`, or raw `bytes` for a key: sent as a message it waits in the queue and answers nothing. Before sending a line again, read `get_process_status`, which lists the pending and recent deliveries to that process. A delivered line was typed into the terminal, which isn't a turn that started, so read the screen as well, and never resend on silence alone. A worker reads what was sent to it with `get_process_input_log`, and narrows who may type into it with `set_process_mcp_input_policy`, each on its own process only; `get_process_status` shows the policy.
- **Locks**: `lock_acquire` on shared resources before editing, `lock_release` when done. `lock_status` to see who holds what. Use them when more than one agent could touch the same area. Solo also has todo-level locks (`todo_lock`) that signal active work on one todo.
- **Timers**: `timer_set` for 'ping back in N minutes'. `timer_fire_when_idle_any` to wake the lead as soon as any worker goes idle. `timer_fire_when_idle_all` when integration must wait for the whole batch. `timer_pause` / `timer_resume` / `timer_cancel` / `timer_list` for housekeeping. `verbatim: true` delivers the body without Solo's timer header, so a body such as `/compact` runs as a slash command in the worker. A worker waiting on a long shell command reads as idle, and an idle timer on an already-idle process is refused as `already_satisfied`: read the output before treating idle as done, and watch such a worker with `timer_set` instead.
- **KV store**: `kv_set` / `kv_get` / `kv_list` / `kv_delete` for small project-scoped JSON state (run counters, last-seen values, config flags). Reach for it rarely; a scratchpad section or todo comment usually fits better. It's off by default: if the KV tools aren't visible, the user hasn't enabled them.
