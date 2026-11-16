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
- The repo's last retro: `python3 ~/.claude/skills/retro/retro.py ledger read --repo <root>` ends on its `last_run`. None, or older than two weeks: say so in the reply, in one line.

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
Traps found this session that no hook, test or guideline already covers, one line each.
```

A gotcha an earlier handoff already carried goes through `finish`'s lesson step, and the briefing says where it landed.

## 3. Reply with the prompt

One line, ready to paste:

```
Read ~/.claude/handoffs/<repo>-<YYYY-MM-DD>-<topic>.md first. Continue with <the first open item>.
```
