---
name: finish
description: The round a finished piece of work makes before it's committed: simplify, persona review twice, docs, format, tests, a look at the UI, then a report. Use when a change is done, before any commit, or when Mischa says 'finish', 'rond af', 'klaar om te committen', 'afronden'.
---

# Finish

Run every step that applies, in order. A step that doesn't apply is skipped silently; a step that fails stops the round and is reported.

## 1. Scope

`git status` and `git diff --stat`. The round covers the files this session changed, nothing else: other sessions share the tree. List them before starting.

## 2. Simplify

Run the `laravel:laravel-simplifier` agent (plugin `laravel@laravel`) on those files (PHP, Laravel, Blade). It cuts comments that say nothing, residue of what was removed, orphans and speculation.

## 3. Persona review, twice

Non-trivial Laravel work: ask taylor-otwell through parley, with the diff itself in the question (`git diff -- <paths>`), never a summary of it. Fix what holds up, then a fresh taylor pass on the fixed diff. Rust goes to david-tolnay, Python to raymond-hettinger. See `rules/second-opinions.md`.

## 4. Docs

If the repo has a `sync-docs` skill, run it scoped to the diff. Docs are rewritten to the end state, never annotated with what changed.

## 5. Format

The formatter on the changed PHP files only: `vendor/bin/pint a.php b.php`. Never `--dirty`, never `--blade`. The Stop hook already formats what the session edited; this step catches files changed through Bash.

## 6. Tests

The tests that cover the changed files first, then the repo's full suite with the command from its `CLAUDE.md`. In the foundry that's `vendor/bin/pest --compact` and then `bin/imprints check` for the quiet imprints. One suite at a time per database; never kill another session's run.

## 7. Look

A view, a component or CSS changed: build the assets, then look at every changed page, light and dark (`bin/shoot` in a Steddle imprint, or a screenshot through Playwright). Read the screenshots. If you can't see the page, say so.

## 8. Report

One line per changed file, the suites with their counts, what you saw, and what's left. Commit only where Mischa gave his word for this repo: by pathspec, `git commit -- <paths>`, no trailer, never on a red or unrun suite. Pushing always waits for his word.
