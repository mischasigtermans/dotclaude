---
name: handoff
description: Hand the session's work to a fresh session: a Solo scratchpad with the state, and a two-line prompt that points at it. Use when the context is filling up, when Mischa asks for a prompt for a new session, or says 'overdracht', 'handoff', 'prompt voor nieuwe sessie', 'sessie zit vol'.
---

# Handoff

The next session starts with zero context. The scratchpad is its whole briefing; the prompt only points at it.

## 1. Check the state first

- `git status` and `git log --oneline origin/main..HEAD` in every repo this session touched.
- The suites' last result, from a run, not from memory.
- `ListAgents` and Solo's process list for other sessions in the same trees.
- The Solo todos this work owns.

## 2. Write the scratchpad

In the project's Solo scratchpad for this work (update it; create one only when none exists), under these headings:

```
## Goal
## State
Commits made, not pushed. Uncommitted files, each with its owner (this work or another session).
## Verified
Suites with counts, screenshots looked at, flows run.
## Open
Each open item with its Solo todo id and what blocks it.
## Other sessions
Who works in which tree, by Solo process or todo, never by session name alone.
## Gotchas
Traps found this session, one line each.
```

A gotcha that already appeared in an earlier handoff doesn't go in again: it goes into the repo's own guideline or `CLAUDE.md` now, per 'When I correct you' in `~/.claude/CLAUDE.md`, and the handoff says where.

## 3. Reply with the prompt

Two lines, ready to paste:

```
Read solo://proj/<id>/scratchpad/<slug> first. Continue with <the first open item>.
```
