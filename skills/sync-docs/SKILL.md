---
name: sync-docs
description: 'Find and fix drift between the code and what the project says about it: guidelines, skills, docblocks, route and tool prose, mails, site copy, docs, legal pages and setup files. Reads the project''s surfaces and areas from `.ai/sync-docs.md`, fans out read-only agents per area (or one named area) for file:line evidence, then runs edit-scoped fix rounds once the user says go. Triggers: "sync docs", "sync docs for the site", "audit the docs".'
---

# Sync docs: find and fix drift

A sweep so a fresh session, an agent and a visitor read only what's true today. It hunts drift, meaning a claim that stopped matching the code, and residue that narrates how something changed. Every claim resolves to a file, a migration, a route, a config key, a test or a dated measurement.

## The project's half

The method is the same in every project. What differs lives in the project, in `.ai/sync-docs.md`. Read it first, whole. Its sections:

- **Work log**: where findings and the fix plan are kept, and where work that needs building goes.
- **Surfaces**: what counts as a doc here, where it lives, which files are generated, and what is not a doc.
- **Areas**: one row per area, the docs it owns and the truth it is checked against.
- **Ground truth**: what to read before fanning out.
- **Rounds**: what a round ends with beyond this method: regenerating generated files, a build, the formatter and the test command.
- **Checks**: the project's own checks, on top of the residue checklist.

Without a `.ai/sync-docs.md`, infer the relevant surfaces from the project layout and state the scope. If maintaining this workflow is authorized, draft the project map; a read-only audit reports the proposed map without writing it.

## Where the work lives

Findings and the fix plan go where the Work log section says: one entry per pass, one section per fix round. In a Solo scratchpad that is `mcp__solo__scratchpad_write` for a new pass, `scratchpad_append_section` to add a round and `scratchpad_read` to resume one.

## What every project holds the same

- A file the Surfaces section marks as generated is never edited by hand. A finding in one is filed against its source.
- Code vendored from another repo is read, never edited there. A finding in it is filed against that repo.
- `.ai/sync-docs.md` is a doc like any other, audited by the area that owns the setup files.

## Method: audit, then act

Separate investigation from edits so findings stay reviewable. A requested audit stays read-only. If the user already authorized fixes, including a finish round, apply mechanical doc corrections after the investigation without asking again. Product, legal or scope decisions remain with the user.

1. **Ground truth first.** Read what `.ai/sync-docs.md` lists under Ground truth, and `git log --oneline -30`: recent commits are where drift concentrates.
2. **Fan out one read-only agent per area**, or only the area the user named. Give each its row from Areas, the Surfaces table, this file, the residue checklist and the project's Checks. Judgement is the job, so run them on the session's own model, not the subagent default. Each returns `file:line | category | evidence | proposed action`, ranked.
3. **Verify the fan-out stayed read-only.** `git status --short` before and after must match.
4. **Synthesize into the work log**: one 'Findings' section per area; one flat 'Decisions for the user' list for anything that isn't a mechanical fix (operative text, a claim that might be a product decision, a feature a doc promises and the code lacks); one 'Bugs and dead code' list for what the sweep tripped over.
5. **Respect the requested mode.** For an audit, report and stop. For authorized fixes, continue with mechanical corrections and report any decisions that block the rest.
6. **Fix authorized work in edit-scoped rounds**, one round per concern (one guideline or rule file, docblocks in one directory, tool prose, mail copy, site copy, one docs topic), never a round that touches both a guideline and code comments. A round ends with the checklist re-run against the files it touched, then whatever the Rounds section adds for that kind of file.
7. **Verify before reporting done.** Re-grep the changed files for residue. Confirm every count against the source (`grep -c`, a route list, a migration, a query). If code changed, run the formatter from Rounds on the changed files only, never a whole-tree or dirty-files mode, since other sessions share the tree, then the test command.

## Write the end state

Every rewrite reads as if the current state was always true. Never narrate the change.

- Banned in prose: `now`, `no longer`, `previously`, `used to`, `instead of`, `the old`, `before` where it means an earlier build. A line that teaches the reader something used to exist gets rewritten to describe only what exists.
- A reason survives the rewrite; the story of how it was learned doesn't. Keep a measurement as a dated fact about the data, and drop the narration of the build that produced it.
- A dated measurement isn't drift. 'Measured on 2026-08-20: 24.079 rows' stays true. It is a finding only when undated, when what it measured is gone, or when the code contradicts the conclusion drawn from it.
- A migration's docblock may describe its conversion: what the table held, what it holds after, and why. Only a false sentence in one is a finding.
- History lives in git, the work log and the project's journal where it keeps one, never in a guideline, a docblock, a tool description or site copy.

## Residue checklist

- Transition language, see above.
- Stale counts. Every undated number stated as current ('four tools', 'nine tables', '16 articles') is re-derived from source, not trusted.
- Dead pointers. Every path, class, method, command, route, config key, env var, tool, prompt, resource URI or `{@see}` a doc cites still exists under that name, and every link in site copy, docs and mails resolves.
- Comments detached from their code: a docblock above the wrong member, two stacked docblocks, a sentence split from its antecedent by a later insertion.
- Work log, brief or session references left in prose after a rewrite.
- A comment that restates the code, narrates or decorates. A comment carries what the code cannot: a reason, a trap, a constraint, a dated measurement.
- The user's writing rules: banned words, dashes, separators, number format.

## Checks in every project

- **The same fact typed more than once.** A status list, a tool list, a limit or a lifetime stated in code, copy, docs, tool instructions and legal pages. Two statements that disagree are a finding; so is a copy that didn't need to exist because a class constant, a config key or a content file already holds the fact. The project's Checks name its facts.
- **Overclaims.** A sentence that promises more than the code keeps, such as enforceability, a review nobody did, 'nothing can be deleted' or 'every call is logged'. Check each against the code. The project's Checks name the phrases it's prone to.
- **The code isn't always the fixed side.** For each mismatch the auditor says which side should yield and why. Where the code should, it goes under bugs; where the doc should, it's a doc finding.
- **Silence is a finding.** Something that exists and no doc mentions is listed, never filled in with what a doc might say.

## Flag, don't silently fix

A drift sweep surfaces real bugs and dead code along the way. Don't fix them mid-sweep: note them in 'Bugs and dead code'. Fix only the doc mismatch itself.

## What not to do

- Treat a read-only audit as permission to edit, or ask again for fixes the user already authorized.
- Hand-edit a generated file, or edit what the Surfaces section marks as never edited in a round.
- Run one round across both a guideline and code comments.
- Cut a fact to make a comment shorter. A reason, a constraint or a dated measurement stays; prose around it goes.
- Assert a count or a claim without re-deriving it from the source.
- Commit or push. That's the user's call.
