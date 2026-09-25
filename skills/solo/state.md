# Durable State

Scratchpads, todos, and when each beats auto-memory.

## Scratchpads vs auto-memory

These don't overlap. Don't let them.

- **Auto-memory** (`~/.claude/projects/.../memory/`): stable facts about the user, the project and external references that the code can't tell you. Never rules (those go to CLAUDE.md, rules/ or the repo guideline) and never status (that's a todo). Survives every session.
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

