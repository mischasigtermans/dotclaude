---
name: lead
description: "Lead a batch of prepped work: interview the user once, keep a role file, hand each issue to a worker, check what comes back and commit it. Use when the user makes a session the lead or executor of a set of issues or findings (from an audit, a panel, research or a backlog), says 'become the lead', 'you become executor', 'take the lead on these', 'have agents fix these issues', 'push the work to agents', 'neem de leiding', 'laat agents dit oppakken', or when a session picks up a role file a lead wrote. One delegated task needs no skill; reviewers reading one subject are `panel`."
---

# Lead

One session decides what's worked next, hands each piece to a worker, checks what comes back and commits it. The user answers their questions once, at the start, and reads one overview per stretch after that.

Workers are Solo workers. Load `solo` and read its `workers.md` before the first spawn: it holds the spawn, message, timer and model mechanics.

## 1. Check the work is prepped

A worker starts with zero context and can't ask the research that found its issue. An issue is ready for a lane when it states:

- the problem, with its trace as `file:line`;
- how to show it: a failing test, or acceptance a test can check;
- the remedy, or the decision the user already took;
- what is out of scope.

An issue that lacks one gets shaped first, by you or by the project's own shaping skill. Where shaping means choosing its scope, that choice goes into the interview. An issue with a decision of the user's still open goes into the interview, not to a worker. A finding nobody has reproduced waits for the interview's answer on those.

Then cut the work into lanes. A lane is one worker's share: one issue, or a few on the same files.

- Every running lane owns files no other running lane touches. Two issues on the same file run one after the other, or share a lane and land as one commit.
- Files every lane needs lines in (a status file, a decisions log, a changelog, an enum, the routes) are yours. A lane hands their lines back as text: a pathspec commit takes a whole file, so one owner keeps the hunks apart.
- A triage a subagent wrote is unverified: check each path against the tree before it enters a brief.

## 2. Keep a role file

`~/.claude/handoffs/<repo>-<YYYY-MM-DD>-lead.md`, from `role-file.md`. It's the role's memory across a compaction, a `/clear`, an account switch or a takeover, written for a session with zero context.

- **Goal** holds the user's sentence that made you lead, quoted and dated. Every brief quotes it as its go.
- **State** and **Open** are rewritten whole each time a lane lands or an answer arrives. Never append: the session that takes over trusts this file, and a line that was true an hour ago misleads it more than a missing one.
- State per issue lives in the project's work tracker when it has one: the claim, the handback as a comment, in review with the sha. The file then holds what the tracker can't: the answers, the order, the lanes, how a lane runs. A project without a tracker gets a Solo todo per lane (`solo`'s `state.md`). Pick one home per fact; mirrored state drifts.

## 3. Interview the user

Before the first worker. Explain the options in the reply, then ask through the question form, recommended option first. Write each answer into the role file when its form returns, in the user's words, and as a comment on the issue it settles.

The standing questions, up to four to a form:

1. **Order**: what runs first, and what beside it.
2. **Workers**: how many at once, on which accounts, and whether each gets a worktree of its own.
3. **Push**: who pushes. Yours only when they say so here.
4. **Review**: how deep before a commit, and for which kind of change.
5. **Unreproduced findings**: build only what a failing test shows, or first let a seat from another lab try to reproduce each.
6. **Reporting**: what they see, and when.
7. **Unattended**: may it run without them, and what stops it.

This skill sets no defaults for the first five. Recommend from what the project shows, such as the tracker's priorities, the accounts' usage and its own review rule, and say why in the reply.

Then the decisions the issues hold open: money, anything that goes outside by itself, legal text, scope. One form each, with what is sent or spent, to whom and when. Read every issue in scope for these first, so the user is asked once.

Skip what the role file, the project's guidelines or an earlier answer already settles. A question that comes up later is put fresh, with a recommended default, and the lanes that don't hang on it carry on.

## 4. Write the briefs

Two kinds of file, both from `lane-brief.md`:

- **Lane rules**, one file for every worker: what it may not do, how it tests, what it hands back.
- **A brief per lane**: the go, the finding, done when, its files, what isn't its.

The start line is one line that names both. A worker reads them again after a compaction, and a fix to the lane rules reaches every lane that starts after it.

Check every path and line in a brief against the tree at the commit the lane starts from. A worker in another project doesn't read this project's memory, so a trap you know goes in the lane rules.

## 5. Run a pilot, then waves

One lane alone, end to end: spawn, handback, review, gate, commit. Pick one that is self-contained and passes every gate the round has, so it rehearses the whole route. Fix what it shows wrong in the lane rules before a second lane starts.

Then waves, up to the count the user gave. Read the accounts' usage before each wave.

- **Spawn** in the repo's own Solo project and directory, so the worker loads that repo's instructions. Name the process after its issue.
- **Model**: per `workers.md`. A lane on a smaller model that hands back 'not reproduced' or proposes another remedy goes to the larger model, never to a retry.
- **A seat that reproduces a finding**, where the user chose one, comes from another lab (`panel`'s reviewer tools): a read that isn't anchored on the finder's. A project's rule on which labs may read its material wins.
- **Wake** on `timer_fire_when_idle_any`, with a body that names the worker, the marker and the next step. Idle isn't done: read the screen and the issue.

## 6. From handback to commit

You commit each issue. The worker's green run isn't yours: `HEAD` moved with every lane that landed since, and the review comes before the commit. A worker in a checkout it shares never commits. One in a worktree of its own may commit on its lane branch as its handback, and you land that.

One lane at a time:

1. Read the diff itself, new files included: `git diff` leaves out an untracked one. Check its paths against the lane's files.
2. Where the finding came with a reproducing test of its own, run that test against the diff too, or have the session that holds it run it when it needs that session's sandbox. The worker wrote its test from the finding; this one is independent of the fix.
3. The review round at the depth the user chose (`finish`).
4. The gate on the integrated state: a clone or export of today's `HEAD` plus this diff, with the project's required checks.
5. Write the lines for the shared files, then commit by explicit pathspec: one commit per issue, or one for a lane's issues that share a file.
6. Set the issue in review with the sha and its gate notes: a migration, a changed job payload, a command to run after the deploy.
7. Close the worker once its handback is on the issue and the commit is verified. Remove its clone or worktree.

The range goes to whoever holds the push: every sha with its issue and gate notes.

You're the serial step, so keep your share thin. What a worker can settle before it hands back, it does: the simplifier on its files, the formatter, the full suite in its own clone, the doc lines as text. Your review then reads a final diff once.

## 7. Report and stop

One overview per stretch of work, unless the user chose otherwise: what was committed, what was dropped as not reproduced, what waits on them with each open point as one question, and a screenshot of every screen a fix changes. No message per lane.

Unattended work stops a lane at the stops the user gave. The defaults to offer: an account past the share of its window they name, a suite still red after one retry, a fix that needs a file outside its lane, anything that needs their decision. Park the stopped lane with its reason on the issue; the others carry on.

## 8. Hand the role on

Rewrite State, then give the prompt: `Read <role file> first. Continue with <the next lane>.`

A session that takes the role over reads the file whole, asks what the interview left unanswered, and tells the other sessions it's the lead now. A timer delivers to one process, so a new process sets the role's timers again.

After the first wave, and every week or two the role runs, run `retro` on the repo.
