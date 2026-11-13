# Durable State

Scratchpads, todos, and when each beats auto-memory.

## Scratchpads vs auto-memory

They hold different things. Keep them apart.

- **Auto-memory** (`~/.claude/projects/.../memory/`): stable facts about the user, the project and external references that the code can't tell you. Rules go in CLAUDE.md or the repo's guidelines and status goes in a todo, never in memory. Memory survives every session, and its facts never go in a scratchpad or a todo.
- **Solo scratchpad**: task-scoped working memory for the current piece of work, when it must outlive compaction or a worker agent must read it.

Write a scratchpad when an investigation has more than ~3 findings, a plan has more than ~3 steps, the work goes to a worker, or the work might resume in a future session.

Use these headings, since agents scan them:

```
## Goal
## Current understanding
## Relevant files and commands
## Decisions
## Open questions
## Next actions
```

Tools:
- `scratchpad_create`: a new pad; it can't overwrite one
- `scratchpad_write`: full write of an existing pad, revision-guarded
- `scratchpad_edit`: targeted edit without rewriting the whole pad
- `scratchpad_append` / `scratchpad_append_section`: append raw or under a specific heading
- `scratchpad_read` / `scratchpad_tail`: read the whole pad or only the latest entries
- `scratchpad_find`: search one pad for literal text without returning the whole document
- `scratchpad_list`, `scratchpad_add_tags`, `scratchpad_archive`

Prefer `scratchpad_edit` / `scratchpad_append_section` over rewriting the whole pad. Don't `scratchpad_delete` unless the user asks: archive instead.

## Todos vs TaskCreate

Don't mirror them: mirroring guarantees drift. Pick one per piece of work.

- **TaskCreate** (Claude Code harness): an in-session checklist that dies when the session ends. Use it for 'do these 4 things right now'.
- **Solo todos**: survive sessions and support blockers, locks, comments and tags. The user sees them in their IDE. Use them for anything that must outlive this conversation or be picked up by another agent.

Todos own:
- A concrete objective
- A scratchpad reference (heading or link), not duplicated context
- Blockers via `todo_set_blockers` / `todo_add_blocker`: turn a flat list into an orchestration plan
- Tags for lanes (`todo_add_tag`)
- Comments for handoffs (`todo_comment_create`): changed files, tests run, remaining risk
- Locks (`todo_lock`) while actively working; release on handoff

Blockers and locks are project-scoped. `todo_transfer` keeps comments and completion state but clears blockers and locks.

Don't `todo_delete` unless the user asks: mark the todo complete instead.
