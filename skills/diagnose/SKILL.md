---
name: diagnose
description: "Find the cause of a failure before changing code, then fix it test-first. Use for a bug, a failing or flaky test, wrong or slow behaviour whose cause isn't known, or a fix that didn't hold. Triggers on 'debug', 'diagnose', 'waarom faalt', 'zoek de oorzaak', 'why does this fail', 'it still fails'. A change whose cause is already known needs no skill."
---

# Diagnose

Find why it fails before you change anything. A fix without its cause passes until it doesn't.

**Done:** the chain from trigger to symptom is stated without a gap, every link with `file:line` or a command's output, and the fix is verified or the diagnosis is handed over.

## 1. Reproduce

Find the smallest command that shows the failure, and run it. When the error tracker holds an issue for it (Nightwatch, Sentry), read that first: its stack trace and first-seen time are evidence. Can't reproduce it: say so, and say what you'd need.

## 2. Rule out the environment

Before reading code: a stale build or stale assets, the wrong database or env, a worker still running old code, another session's uncommitted edit in the same tree.

## 3. Trace back from the symptom

Start where it shows and walk back to where it starts. One hypothesis at a time. Before you test one, name the observation that would refute it, then make that observation. Changing several things to see what helps hides which one mattered.

## 4. The gate

No fix until the chain is complete. 'Somehow X leads to Y' is a gap. Only the user decides to act on a best guess.

## 5. When it doesn't converge

Three hypotheses refuted, or two fixes that didn't hold: stop changing code. Write down what each attempt ruled out and look for the assumption they share. When every fix would be a workaround, the design is the problem: say that and stop.

## 6. Fix

- The failing test first, where existing tests already cover that behaviour. Say in one line what it catches and what it misses.
- One change. Then the reproduction from step 1 again, and a look at the callers of what you changed.
- A test that fails because the fix reverses intended behaviour isn't a wrong test. That's the user's decision.

## 7. The signal that was missing

When the deciding fact took digging because no log, metric or error showed it, propose the one that would have: a log field, a metric, an assertion. A proposal only.

## 8. Report

- **Problem:** what failed, and for whom.
- **Cause:** the chain, with `file:line`.
- **Fix:** what changed and how it was verified, or 'diagnosis only'.
- **Prevention:** the test added and the signal proposed.
- **Confidence:** high, medium or low, and what would raise it.

Then `finish`, whose lesson step asks what would stop a repeat.
