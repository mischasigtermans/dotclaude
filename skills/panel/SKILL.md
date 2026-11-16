---
name: panel
description: "Run independent Solo reviewers across Claude, Codex or Grok, cross-examine findings and produce a joint report. Use for a requested multi-agent panel or re-check of its fixes."
---

# Panel

Independent reviewers read one subject, check each other, and end with one report they all sign. The report is final only when every reviewer signs it without reservation. A disagreement that survives stands under Contested, with both sides in words each side would sign, never as a dissent footnote.

Workers are Solo workers. Load `solo` and read its `workers.md` before the first spawn: it holds the `send_input`, trust-prompt and idle-timer traps.

## Review gates

Every brief carries these four, verbatim:

- Report a finding only above 80% confidence.
- Each finding cites the exact line, names the input and the bad outcome, and was checked against the callers and tests.
- Defend the severity. A style preference is not a bug.
- Zero findings is a valid review. Don't manufacture findings to look rigorous.

## 1. Intake

Ask two things with AskUserQuestion, after explaining each option in the reply:

- **Labs** (multi-select): Codex, Grok, Claude. Recommend Codex and Grok: reviewers of one lab confirm each other's findings more readily than another lab's, so a second lab shows a split one lab hides. A project rule on which labs may read its material wins: check the project's guidelines and memory before you offer a lab.
- **Reviewers per lab**: 1, 2 (recommended), 3. Two per lab separates what a lab agrees on from what one reviewer saw.

Decide the rest yourself and state it in the plan:

- **In place or snapshot.** `list_processes` on the subject's Solo project. An agent building there means a snapshot (section 3). None means the reviewers read the subject in place, read-only, and you run `git status --short` after every round.
- **Subagents.** When the subject is more than one context window can read in full (a whole app, a standard with annexes), the brief lets each reviewer spawn its own CLI's subagents for context: Codex `multi_agent`, Grok's subagents, Claude's Agent tool. Never a Solo process from a worker: each is a full CLI with its own MCP stack.
- **What they investigate.** The user's ask, plus what you would look for yourself, split into areas. Each reviewer starts in a different area, so they read in different orders.
- **Earlier runs.** A subject with a run in `~/.panels/<project>/` before: read its joint report and its review of the fixes. The brief names each fixed finding with its commit; reviewers re-check it only where the source changed since, and don't report it again.

## 2. The run folder

`~/.panels/<project>/<yyyy-mm-dd>-<slug>/`. Never the session scratchpad: that sits under `/private/tmp` and goes with the session, and a review of the fixes later needs the round files. Never inside a repo or an agent's config folder either: a CLI takes the instruction files of the repo it starts in as its own, whatever home folder it got.

```
briefs/                     one file per round, from briefs.md
context/                    plans, todos, schema dump, in-flight diff
UPDATES.md                  snapshot runs only: what changed under the reviewers, newest at the bottom
round-1/ round-2/ round-3/  <name>.md per reviewer
round-2b/ round-3b/         coverage (<name>.md, <name>-ledger.txt) and the answers to round 3
notes/<name>/               scratch for a reviewer and its subagents
homes/<name>/               the empty home folder a Codex or Grok seat starts with
joint/                      tally.md, draft.md, review-<name>.md, report.md, changes.md, signoff-<name>.md
review/                     <name>.md per reviewer, for the review of the fixes
tree/                       the snapshot, when there is one
```

The orchestration state goes in a Solo scratchpad tagged `panel` in the subject's project: the ask in the user's words, the folder, each worker (name, lab, model, process id, CLI session id), the round log, and what you verified.

## 3. Snapshot

Only when another session is building in the subject's repo.

- `git -C <repo> archive <sha> | tar -x -C tree/`. Copy `vendor/` in when the reviewers may run the project's read-only commands (`route:list`, `php -l`). A real `.env` never enters the tree: another lab reads it.
- `context/`: the schema (`pg_dump --schema-only` of the local database, or the project's equivalent), the plans and todos, and the builder's uncommitted work (`git -C <repo> diff`, untracked files listed) as a read-only view of where the code is heading.
- Tell the repo's lead session through `SendMessage` that the panel is running, and ask it to say when a commit changes what the reviewers read.
- When the subject moves, re-export between rounds; mid-round only on the user's word, since it shifts every line number under the reviewers. Write the delta to `context/`, add an entry to `UPDATES.md`, and send each idle reviewer one line. Every brief tells reviewers to read `UPDATES.md` at the start and before they finish a file.
- Every finding carries a phase tag: `unaddressed`, `planned:<where>`, `in-flight:<step>`, `decided:<where>`. A finding that restates a planned step isn't a finding.
- The subject stays the snapshot's commit to the end. Where the repo has moved on by the joint report, each finding whose cited file the later range changes says so in one line (`Touched by <range>: <file>`), without judging the change.

## 4. Workers

A seat starts clean. Left alone, a CLI loads the user's own setup before it reads its first line. Claude Code loads the user's instructions, rules, skills, plugins, hooks and MCP servers. Grok reads the same `~/.claude` and adds its memory of earlier sessions. Every CLI inherits the shell's environment, secrets included. A reviewer that starts that way works under the user's instructions, and another lab receives what the brief left out. What a seat needs to know about the project reaches it through the brief, as material to test.

So every seat starts through a reviewer tool, never a plain one. `list_agent_tools` shows them as `Codex (reviewer)`, `Grok (reviewer)` and `Claude (reviewer)`. Each runs `seat` from this folder with the CLI's name, and `seat` passes on only the variables it lists, with no shell profile:

- **Codex and Grok** take the seat's own home folder, `<run>/homes/<name>`, as the first argument and start with that empty home and no memory. The sign-in comes through `CODEX_HOME` and `GROK_HOME`, and `cargo` through `RUSTUP_HOME` and `CARGO_HOME`. In that home `gh` isn't signed in and the Herd CLI doesn't run; git, Node, PHP, Composer and Python do.
- **Claude** signs in through the real home's keychain, so it keeps that home and loads no settings instead: no skills, plugins, hooks, MCP servers or instruction files, the user's or the run folder's. Its built-in browser tools are off.

No seat runs under the user's guard hooks. When a reviewer tool is missing, ask the user to add it: its command is the path of `seat`, followed by `codex`, `grok` or `claude`.

`spawn_agent` per reviewer, with `working_dir: <run>`, `include_agent_instructions: false`, and the lab and model in the process name:

| Lab | Agent tool | extra_args |
|---|---|---|
| Codex | `Codex (reviewer)` | `<run>/homes/<name> --yolo -m gpt-6-astra -c model_reasoning_effort="xhigh"`, plus `--search` when the brief needs the web |
| Grok | `Grok (reviewer)` | `<run>/homes/<name> -m grok-4.7 --effort xhigh --always-approve` |
| Claude | `Claude (reviewer)` | `--permission-mode auto --model opus` |

The models and effort levels are examples: pass the ones the user runs for each lab. A Claude seat takes `--permission-mode auto`: with `--dangerously-skip-permissions` it stops at Claude Code's bypass warning on every start, since the settings that hold the user's answer are left out.

- Before the start line, read the worker's screen (`get_process_output`): it must sit at an empty prompt. The Codex and Grok dialogs that catch a start line, and why every line to them goes through `send_input`, are in `solo`'s `workers.md`.
- The start line is one line: the reviewer's name, the brief's path, its output path. The brief itself lives in `briefs/`.
- After every round, list what changed in the run folder outside the round's own folder and `notes/`. Every seat can write there, and a Codex seat that starts in the run folder reads an `AGENTS.md` at its root as its instructions.
- After the start line, check what each Grok seat loaded. `prompt_context.json` in its session folder must show an empty `agents_md_files` and `memory_v2_enabled: false`. A seat that loaded anything is closed, and its files are deleted before another seat reads them.
- Read each worker's usage limit on its screen before a round opens. A reviewer with little left gets a work order in its brief: its own defence first, then high, medium, low. One that stops at its limit keeps its partial work, and a Claude seat on Opus takes it over: it reads the seat's files, finishes the round, defends the seat's findings from then on and signs in its own name. The report names the seat and the round it changed hands.
- Record each CLI session id in the scratchpad. Codex: the id in `~/.codex/sessions/<y>/<m>/<d>/rollout-<time>-<id>.jsonl`, found by grepping for the start line; resume with `resume <id>` right after the home folder in extra_args. Grok: `~/.grok/sessions/<cwd, url-encoded>/<id>/`; resume with `--resume <id>`. Claude: `<config dir>/projects/<the run folder's path with `/`, `.` and `_` turned into `-`>/<id>.jsonl`; resume with `--resume <id>`. Grok keys that folder to the run folder's path, so rename it when a run folder moves. A reviewer's subagents write session files of their own that hold the same start line, so take the oldest.

## 5. Rounds

Every brief carries the ask in the user's words, the hard rules, the review gates verbatim, the output path, 'write as you go', and a fixed last line. Templates in `briefs.md`. Run `copywriter` in self-check mode on each brief before it goes out.

- **Round 1, independent.** Each reviewer alone. Nobody opens another's files until round 2 opens. Then lay the coverage tables side by side: round 1 samples, so a reviewer's silence about a file it didn't read says nothing about that file.
- **Round 2, cross-examination.** Each reviewer tries to refute the others' findings. CONFIRMED only on its own re-check; a finding it can't trace in full is UNVERIFIABLE; a refutation cites a line, source or output it read, never an assumed defence. Plus severity, what it rests on, duplicates, and what all of them missed.
- **Round 2b, coverage, when the ask covers the whole subject.** Cut what no reviewer read in full into slices with no overlap, one per reviewer, outside the area it started in. Each reads its slice in full, split across its subagents, sweeps it for dead code, and writes a ledger line per file: full, partial or not-read, with why. Check every ledger against its list. A reviewer gets its slice the moment its round 2 file is done. For a narrower ask, what nobody read goes into the round 2 brief as an assignment, or into the joint report as a gap.
- **Round 3, defence.** Each answers every challenge to its own round 1 findings, and gives verdicts on round 2's new findings and every coverage finding.
- **Round 3b, answers.** The authors of round 2's new findings and the coverage findings answer round 3's verdicts on them: they wrote round 3 at the same time, so without this round those findings reach the joint report undefended. CONCEDE, AMEND or DEFEND, nothing new, and one closing table of all the reviewer's findings with their final status.
- **Joint report.** Before step A, count the tally yourself from the verdict tables that close rounds 2, 3 and 3b: per finding its author's status and each other reviewer's verdict. A finding is agreed when its author kept it, most of the others confirmed it, one of them from another lab when there are two, and no dispute stands. Count too, per reviewer, how many of the other lab's findings it disputed or narrowed in round 2. A reviewer that disputed none is a weak check: its confirmations still count, and the check in section 6 takes the findings they carry first. Write both to `joint/tally.md`; the editor drafts from it. The pen goes across labs. Lab 1 drafts, one reviewer of each lab reviews, lab 2 revises and decides every objection, all sign. Revise and sign repeat until every reviewer signs. With one lab, split the pen across reviewers the same way. Three sign rounds without unanimity: take the blocker to the user.

Wake on `timer_fire_when_idle_all` over the round's workers, with a body that names the marker to check. Idle isn't done: check the last line of every output file before the next round opens.

## 6. Before it reaches the user

Check the signed report twice before the user sees it.

- **Mechanically.** A script, not a model, confirms that every `path:line` the report cites exists in the subject with the line inside the file. That catches a missing file, never a wrong line: a cite one statement off passes it.
- **In the subject.** Split the joint findings into batches of about five, the findings a weak check carried first, and give each batch to a fresh Opus subagent that saw none of the rounds. It gets the findings as the report states them, reads the subject at the run's commit, treats each as wrong until the source shows it holds, and returns HOLDS, HOLDS WITH CORRECTION or WRONG per finding, with the lines it read.

Read every answer. A correction to a verdict, the evidence or the severity goes back to the panel for one more sign round; a line number or a wording you fix yourself. When the subject's authors asked for the review, a finding that rests on the subject's own text alone proves little, however many reviewers agree.

The report states what the panel didn't cover, and that it's one pass: a repeated run finds what one run misses.

The final report goes to `joint/report.md`, and without its marker line into the scratchpad and where the project keeps its research. Report to the user in their language.

## 7. Fixes and re-check

Each finding the subject's lead or the user takes on becomes a Solo todo in the subject's project, its body the finding's block from `joint/report.md` verbatim, unless a plan step already carries it.

On the user's word, resume the same sessions, so the reviewers keep their context. The brief lists the commits per finding and the remedy the authors chose where a finding offered two. Each reviewer gives FIXED, PARTLY, NOT FIXED or REGRESSION per finding with its own check, then what the fixes introduce. A later round of fixes gets a re-check section appended to the same file. Code fixes also go through the user's own review loop, when they have one.

## 8. Close

Close each worker with `close_process` the moment its last file is verified. Delete `tree/` (git still holds the commit), `homes/` (a resumed seat gets a fresh one) and the copies in `context/` of what a live system holds: the schema dump, plans, todos and deltas go stale, and the next session would read them as true. Briefs, rounds, ledgers, notes and `joint/` stay.
