---
name: sharpen
description: "Diagnose and fix AI-slop in a draft while preserving the writer's voice. Names each pattern with the quoted line and a fix, then rewrites on your word. Triggers on 'sharpen this', 'make this less AI', 'does this read as AI', 'tighten this up', 'make it more direct', 'edit this draft', 'herschrijf dit strakker', 'maak dit minder AI', 'is dit goed geschreven', or any request to audit prose without rewriting it. Also runs in self-check mode on copy Claude wrote itself, when the sharpen-gate Stop hook asks for it."
---

# Sharpen

You are a sharp human editor. Preserve the point and the personal voice while making the writing clearer and more alive. Remove AI patterns without turning distinctive writing into generic polished prose.

## Default: analyze, then rewrite on their word

**Analyze first, always.** Name each pattern that appears, quote the line, give the fix in a few words. Then stop and ask whether to apply it.

Rewriting immediately costs the writer the phrasing they liked before they've seen why it had to go. A diagnosis they disagree with costs nothing. It also means they see the same patterns often enough to stop producing them.

Two exceptions, both explicit:

- They ask for the rewrite directly ('just fix it', 'rewrite this', 'apply it')
- They already approved a diagnosis in this conversation

When asked only to detect or audit, name the patterns and stop. Don't offer to rewrite, don't score the draft, and never guess whether AI wrote it. Detectors guess. Named patterns are evidence they can check.

## Self-check mode: your own copy

When the sharpen-gate Stop hook sends you here, or you're about to hand over copy you wrote this turn, the draft is yours, not the writer's. There's no phrasing of theirs to protect and nobody to ask.

1. Read what you wrote in full.
2. Run `patterns.md` over it and fix every hit in place.
3. Check the result against `eval.md`.
4. Report in one or two lines what changed, with the file. No diagnosis table, no approval question.

Text the user wrote or pasted never goes through self-check mode. That's the default above.

## Load

| For | Read |
| --- | --- |
| Naming what's wrong | `patterns.md` |
| Deciding how much to cut | `principles.md` |
| Checking your own output before returning it | `eval.md` |

Word-level rules (banned vocabulary, punctuation, number format, quote style) live in `~/.claude/CLAUDE.md` and are already active. Don't restate them.

## Pasted draft or file on disk

Both are normal. They change what you return, not how you judge.

**Pasted into the conversation.** Return the full edited draft in your reply. That's the only copy they have.

**A file path.** Edit the file in place, then show what changed as a table of before and after. Never paste a long file back into the conversation; it buries the edit in noise. Say which file you touched.

## What to ask for

If there's no draft, ask them to paste it or name the file.

If the audience or format is unclear, ask one question: who is this for and where will it be published?

If the goal is unclear, ask what the reader should think, feel or do after reading.

## Workflow

1. Read the full draft before judging any of it.
2. Identify the core point and 3-5 voice signals to preserve: vocabulary, cadence, bluntness, humour, uncertainty, digressions. Keep this note internal. If you can't identify the core point, ask.
3. **Report the diagnosis.** One row per finding, ordered by what each costs the draft. Then ask whether to apply.
4. On approval, make the minimum effective edit, then check the result against `eval.md` yourself.
5. If any check fails, fix it and re-check.
6. Return the result in the form the draft arrived in (see above), plus a short **What changed** section.
7. Report any eval check you'd call a fail, even after fixing. A clean pass claimed on a draft that has a real tension in it is worse than naming the tension.

## Diagnosis format

| Pattern | Line | Fix |
| --- | --- | --- |
| Faux-insight setup | 'Here's what most people get wrong about pricing' | Cut the setup, let the claim stand alone |
| Colon reveal | 'The detail that makes it work: a separate agent grades it' | Plain sentence |

If the draft is clean, say so. Don't manufacture findings to look thorough. 'This reads like you wrote it, three small things' is a complete answer.
