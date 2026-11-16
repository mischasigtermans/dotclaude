# Lane briefs

Two files under `~/.claude/handoffs/`: the lane rules, shared by every worker of the round, and one brief per lane. The start line names both:

```
You are a lane for <issue> under the lead (Solo process <id>, ListAgents name <name>): no commit, no push. Read <lane rules file>, then <lane brief file>, and work from them.
```

## The lane rules

`<repo>-<YYYY-MM-DD>-lane-rules.md`. Fill in the project's own commands and paths; drop a line that doesn't apply.

```
# Lane rules for a worker in `<repo directory>`

You are one lane of several. A session called the lead (in `<directory>`, the one that started you) decides the work, reads what you hand back, and commits it. <The user>, <date>: '<the go, verbatim>'

## The hard rules

1. No commit, no push, no stash, no branch. You edit files and hand back.
2. Touch only the files your brief names as yours. Need another? Stop and say which and why in your handback.
3. Never edit <the shared files>. Every lane needs lines in them and a commit takes a whole file. Write their lines as text in your handback, each with its file and section.
4. Never touch <a dirty file that belongs to someone else>.
5. Report to the lead only, as a comment on your issue, and ask it there too. Not the user, not another session.
6. Nothing on production.

## The work

1. Call `ListAgents`: its first line names this session. Claim your issue with that name, <the way this tracker takes a claim>, and open every handback with it, so the lead can message you. Read the issue whole. No access to the tracker: say so in your chat and stop.
2. Read the repository's guidelines and the rule files for the paths you edit. They come first; this file only adds how a lane hands back.
3. Write the failing test first, with fixture data of your own. Run it and see it fail for the reason the issue states.
4. Fix the cause, with the smallest coherent change.
5. A finding you can't show with a failing test: stop and hand back 'not reproduced', with what you tried.
6. A suite still red after one retry, or a question only the user can answer: stop and hand back what you have, with the question and the answer you'd recommend.

## Testing

- <Where you edit and where a run happens: a clone or worktree of your own for every run, never the shared tree. How to make it, and how your edits reach it.>
- <The checks, in order: static analysis, the formatter on your own paths, your tests, the whole suite.>
- <The traps: a symlinked dependency, a shared database, a suite another session runs.>
- Before the handback, run <the project's simplifier> on the files you changed, with no behaviour change, and run the checks again on what it touched. The lead's review reads the diff you hand back, so it is the final one.

## The handback

A comment on your issue, in this order:

1. Paths: every file you changed or added, one per line, a new one marked 'new'.
2. The test: its file and name, the failure it showed before the fix in one line of output, and that it passes now.
3. Suite: the counts of the full run, the static analysis result, where you ran it and the sha you started from.
4. Doc lines: the text for the shared files, each with its file and section, or 'none' and why.
5. Gate notes for the push: a migration, a job that changed what it serializes, a new stored value, a command to run after the deploy. 'None' if none.
6. Left open: what you saw and didn't fix, what you'd ask the user, what the fix doesn't cover.

Set nothing on the issue's state: the lead moves it. Say `HANDBACK DONE` in your chat and stop. Leave your clone in place.
```

A worker in a worktree of its own swaps rule 1, and 'no commit' in the start line, for: commit on your lane branch by explicit pathspec, one commit, no trailers, never push. Its handback then names the sha.

## A lane's brief

`<repo>-<YYYY-MM-DD>-<issue>.md`. It holds only what is this lane's.

```
# Lane brief: <issue>, <what changes, in one phrase>

Read `<lane rules file>` first. This file holds only what is <issue>'s.

## The go

<The user>, <date>, to the lead: '<the go, verbatim>' The lead put <issue> in <the pilot | this wave>.

## The finding

<What is wrong, with its trace as `file:line`, and the commit it was found at where the record gives one. Where the full record and the finder's reproducing test are. Read that test for its shape; write your own.>

## Done when

1. <Each a state a test can check: what holds after the fix.>
2. <What must stay as it is.>
3. <The cases the tests show, named.>

## The call that is yours

<Only when the remedy leaves a choice: what to choose between, what must keep working, and that the handback states the choice and why.>

## A trap

<Only when the lead knows one: a default in the test setup, a path that moved, a run an earlier lane lost.>

## Your files

<The paths this lane may edit, and where new tests go. A caller that has to change with them: name it in the handback before editing it.>

## Not yours

<The neighbouring issues and their files; the shared files.>

## Start

Claim <issue>, read it and the record above, then begin with the failing test.
```
