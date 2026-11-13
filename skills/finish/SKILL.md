---
name: finish
description: "The round a finished piece of work makes before it's committed: simplify, persona review twice, docs, format, tests, a look at the UI, then a report. Use when a change is done, before any commit, or when the user says 'finish', 'rond af', 'klaar om te committen', 'afronden'."
---

# Finish

Run every step that applies, in order. Skip a step that doesn't apply without comment. A step that fails stops the round; report it.

## 1. Scope

Run `git status` and `git diff --stat`. The round covers only the files this session changed, because other sessions share the tree. List those files before you start.

## 2. Simplify

PHP, Laravel or Blade changed and the `laravel@laravel` plugin is installed: run its `laravel:laravel-simplifier` agent on those files. It cuts comments that say nothing, residue of removed code, orphans and speculation.

## 3. Persona review, twice

Non-trivial work and both the `personas` and `parley` plugins from by-mischa are available: ask the persona for the language through parley, with the diff itself in the question (`git diff -- <paths>`), never a summary of it. Laravel goes to taylor-otwell, Rust to david-tolnay, Python to raymond-hettinger. Fix the findings that hold up, then ask the same persona for a fresh pass on the fixed diff.

## 4. Docs

If the repo has a `.ai/sync-docs.md`, call the Skill tool with `sync-docs`, scoped to the diff. Rewrite docs to the end state; never annotate them with what changed.

## 5. Format

Run the repo's formatter on the changed files only, never in a whole-tree or dirty-files mode, because other sessions share the tree. For PHP that's `vendor/bin/pint a.php b.php`, never `--dirty` or `--blade`.

## 6. Tests

Run the relevant tests and the repo's required checks from its `CLAUDE.md`. For prose-only work, validate the artifact and its links or examples. One suite at a time per database; never kill another session's run.

## 7. Look

A view, a component or CSS changed: build the assets, then look at every changed page, light and dark, with the repo's own screenshot command if it has one, or Playwright. Read the screenshots. If you can't see the page, say so.

## 8. Report

One line per changed file, the suites with their counts, what you saw, and what's left. Commit on the user's word, or where the user's own instructions say a finished step is committed without asking. Commit by explicit paths, with a message per `commits.md` in `repo-docs`, and never with failing or outstanding required checks. Pushing always waits for the user's word.
