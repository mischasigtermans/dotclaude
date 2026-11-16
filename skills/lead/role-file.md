# The role file

`~/.claude/handoffs/<repo>-<YYYY-MM-DD>-lead.md`. A `handoff` briefing with an interview, a lane procedure, an order and a lane table added. Copy the headings; a section with nothing in it says 'None'.

```
# The lead: <the work, in one phrase>

Written <date and time> by the session in `<directory>` (Solo process <id> in project <id>). Update this file as the state moves.

A session that takes this role over: read this file whole, ask what 'Answers' leaves open, then tell <the sessions under 'Other sessions'> the lead is now you, with your `ListAgents` name and Solo process id.

## Goal

<The user>, <date>: '<the sentence that made this session lead, verbatim>'

So this session:

- decides which issue is worked next, from <the tracker's project or the list>;
- dispatches each to a Solo worker in <the repo's Solo project and directory>;
- commits what comes back, one issue per commit, after its own gate.

It does not <push | touch production | ...>. <Who does, and how the range reaches them.>

## Interview

<The questions still to ask, numbered, each with its recommended default. Empty once asked.>

### Answers

<One numbered line per answer: the option picked or the words typed, quoted; the date; what it means for a lane. An answer given outside the form goes here too.>

## How a lane runs

<This project's own version of the skill's steps, as far as it differs or needs a name:>

- Where the briefs live, and the lane rules file.
- Where a worker tests: a clone, a worktree, the commands, the traps.
- The gate: the commands, in order.
- The commit: message format, the shared files and their sections.
- The issue's states, and what the pusher needs with a range.

## State

<Rewritten whole each time a lane lands or an answer arrives.>

- Per repo: `HEAD`, its upstream, commits made and not pushed with their issues.
- Dirty files, each with its owner or 'owner unknown'.
- Running lanes: issue, worker (process id, `ListAgents` name), model, account, the sha it started from.
- Accounts: usage, with the time it was read.

## Order

<What runs in which order, and why where it isn't obvious.>

## Lanes

| Lane | Issues | Owns | Waits on |
|---|---|---|---|
| <name> | <keys> | <files> | <nothing, an earlier lane, an answer, a fact> |

Where a lane stands (running, handed back, committed at a sha, parked) is on its issue. Without a tracker, a State column here holds it.

Held back, each with what it waits on.

## Verified

<What this session checked itself, with the command and the time. A worker's or a peer's word is marked as theirs.>

## Open

<Only what is open now, each with who it waits on.>

## Other sessions

<Who works in which tree, by Solo process id and `ListAgents` name: the pusher, the finder, the repo's own session.>

## Gotchas

<Traps no hook, test or guideline already covers, one line each. One a worker can hit also goes in the lane rules.>

## Sources

<Where the findings, the research and the project's gate rules are.>
```
