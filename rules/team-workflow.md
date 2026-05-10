# Team workflow

Use teams for parallel work. Never raw `run_in_background: true` agents.

## Start a team when

- 2+ non-overlapping pieces of work exist (different files, repos, or layers).
- Research feeds implementation, and the output of one is input to another.
- Frontend and backend can move in parallel.
- Sequential dependencies the task graph can express (`addBlockedBy`).

## Don't start a team for

- A single-file fix.
- A single grep, read, or lookup.
- Anything one Edit or Bash call would handle.

## Lifecycle

```
1. TeamCreate → team + shared task list
2. TaskCreate × N → all tasks, with dependencies via addBlockedBy
3. Agent spawn × N → each gets team_name and a name
4. Teammates claim unblocked tasks, TaskUpdate to completed
5. SendMessage between teammates when coordination needs it
6. All tasks complete and verified → send shutdown_request to each teammate
7. Teammates go idle → TeamDelete
```

## Gotchas

- **No two teammates edit the same file.** Split by repo or directory.
- **Idle is normal.** Teammates idle after every turn. Wake with a message.
- **Shutdown before TeamDelete.** Send `{"type": "shutdown_request"}` to each.
- **Don't duplicate work.** If you delegate, don't also do it yourself.
- **One focus per agent.** Don't overload with multiple concerns.
- **Background agents can't be coordinated.** That's why teams exist.
