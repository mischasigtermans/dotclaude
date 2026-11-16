---
name: finish
description: "The round a finished piece of work makes before it's committed: simplify, persona review twice, a lesson, docs, copy, format, tests, a look at the UI, then a report. Use when a change is done, before any commit, or when the user says 'finish', 'rond af', 'klaar om te committen', 'afronden'."
---

# Finish

Run every step that applies, in order. Skip a step that doesn't apply without comment. A step that fails stops the round; report it.

## 1. Scope

Run `git status` and `git diff --stat`. The round covers only the files this session changed, because other sessions share the tree. List those files before you start.

## 2. Simplify

PHP, Laravel or Blade changed and the `laravel@laravel` plugin is installed: run its `laravel:laravel-simplifier` agent on those files. It cuts comments that say nothing, residue of removed code, orphans and speculation.

## 3. Persona review, twice

Non-trivial work and both the `personas` and `parley` plugins from by-mischa are available: ask the persona for the language through parley, with the diff itself in the question (`git diff -- <paths>`), never a summary of it. Laravel goes to taylor-otwell, Rust to david-tolnay, Python to raymond-hettinger. Fix the findings that hold up, then ask the same persona for a fresh pass on the fixed diff.

## 4. Lesson

Did this work correct a wrong belief: an approach that failed, a defect the review caught, a doc or an assumption that turned out false? If not, skip. If so, ask whether a session working from the current tree would repeat it without a record. When it would, take the first form that holds:

1. **One way.** Two ways to do the same thing made the mistake possible: report the duplication as work for its owner.
2. **A check.** A test, a lint rule or a hook that fails on the mistake's shape. Keep it only once it passed on the tree and failed on the defect in a throwaway copy.
3. **A scoped rule.** One condition in the rule or guideline that loads for the files it concerns.
4. **An always-loaded line.** Last, since every later session pays for it.

One lesson, one form. When a check or a rule already states it, write nothing and name the file that holds it.

## 5. Docs

If the repo has a `.ai/sync-docs.md`, call the Skill tool with `sync-docs`, scoped to the diff. Rewrite docs to the end state; never annotate them with what changed.

## 6. Copy

The diff changes words a reader sees (a view, a lang or content file, a mail, a post, the prose of a doc): call the Skill tool with `copywriter` and run its sharpen mode in self-check, scoped to the diff. Skip it when the copy gate already sent this copy through the skill this session.

## 7. Format

Run the repo's formatter on the changed files only, never in a whole-tree or dirty-files mode, because other sessions share the tree. For PHP that's `vendor/bin/pint a.php b.php`, never `--dirty` or `--blade`.

## 8. Tests

Run the relevant tests and the repo's required checks from its `CLAUDE.md`. For prose-only work, validate the artifact and its links or examples. One suite at a time per database; never kill another session's run.

## 9. Look

A view, a component or CSS changed: build the assets, then look at every changed page, light and dark, with the repo's own screenshot command if it has one, or Playwright. Read the screenshots. If you can't see the page, say so.

## 10. Report

One line per changed file, the suites with their counts, what you saw, the lesson and the form it took or that none qualified, and what's left. Commit on the user's word, or where the user's own instructions say a finished step is committed without asking. Commit by explicit paths, with a message per `commits.md` in `repo-docs`, and never with failing or outstanding required checks. Pushing always waits for the user's word.
