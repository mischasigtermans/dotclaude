---
name: handoff
description: "Hand the session's work to a fresh session: a briefing with the state, and a one-line prompt that points at it. Use when the context is filling up, when the user asks for a prompt for a new session, or says 'overdracht', 'handoff', 'prompt voor nieuwe sessie', 'sessie zit vol'."
---

# Handoff

The next session starts with zero context. The briefing is everything it knows; the prompt only points at it.

## Where the briefing goes

Always write it to `~/.claude/handoffs/<repo>-<YYYY-MM-DD>-<topic>.md`. That path sits outside every repo, so it's never committed, and any session on this machine can read it. If this work already has a briefing, update that file.

## 1. Check the state first

- `git status` and `git log --oneline @{upstream}..HEAD` in every repo this session touched.
- The suites' last result, from a run, not from memory.
- `ListAgents` for other sessions in the same trees.
- The open work this session owns.

## 2. Write the briefing

Under these headings:

```
## Goal
## State
Commits made, not pushed. Uncommitted files, each with its owner (this work or another session).
## Verified
Suites with counts, screenshots looked at, flows run.
## Open
Each open item and what blocks it.
## Other sessions
Who works in which tree, by `ListAgents` name and repo.
## Gotchas
Traps found this session, one line each.
```

Don't repeat a gotcha from an earlier handoff. Move it into the repo's own guideline or `CLAUDE.md`, and say in the briefing where it went.

## 3. Reply with the prompt

One line, ready to paste:

```
Read ~/.claude/handoffs/<repo>-<YYYY-MM-DD>-<topic>.md first. Continue with <the first open item>.
```
