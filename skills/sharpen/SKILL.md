---
name: sharpen
description: "Diagnose and fix AI-slop in a draft while preserving the writer's voice. Names each pattern with the quoted line and a fix, then rewrites on your word. Triggers on 'sharpen this', 'make this less AI', 'does this read as AI', 'tighten this up', 'make it more direct', 'edit this draft', 'herschrijf dit strakker', 'maak dit minder AI', 'is dit goed geschreven', or any request to audit prose without rewriting it. Also runs in self-check mode on copy Claude wrote itself, when the sharpen-gate Stop hook asks for it."
---

# Sharpen

Edit like a sharp human editor. Keep the writer's point and voice, make the prose clearer and livelier, and take out the AI patterns. A distinctive draft stays distinctive after your edit; never sand it down into generic polish.

## Default: analyze, then rewrite on their word

Analyze first, always. For every pattern you find, quote its line, name it and give a fix of a few words. Then stop and ask whether to apply the fixes.

A rewrite up front takes away phrasing the writer liked before they've seen why it had to go. A diagnosis they reject costs them nothing. Seeing the same patterns named again and again also teaches them to stop producing them.

Two exceptions, both explicit:

- They ask for the rewrite directly ('just fix it', 'rewrite this', 'apply it')
- They already approved a diagnosis in this conversation

A request to detect or audit gets the named patterns and nothing more. No offer to rewrite, no score, and no verdict on whether AI wrote the draft. A detector's verdict is a guess; a named pattern with its quoted line is evidence the writer can check.

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

Word-level rules (banned vocabulary, punctuation, number format, quote style) live in the user's own instructions (`CLAUDE.md`, or custom instructions on claude.ai) and are already active. Don't restate them.

## Pasted draft or file on disk

You judge both the same way. What you hand back differs.

**Pasted into the conversation.** Return the full edited draft in your reply. That's the only copy they have.

**A file path.** Edit the file in place, then show what changed as a table of before and after. Never paste a long file back into the conversation; it buries the edit in noise. Say which file you touched.

## What to ask for

No draft yet: ask for the text or the file path.

Audience or format unclear: ask one question, who it's for and where it will appear.

Goal unclear: ask what the piece should leave the reader thinking, feeling or doing.

## Workflow

1. Read the whole draft before you judge any part of it.
2. Find the core point and 3-5 voice signals worth keeping: vocabulary, cadence, bluntness, humor, uncertainty, digressions. Keep that note to yourself. If you can't find the core point, ask.
3. Report the diagnosis. One row per finding, the costliest first. Then ask whether to apply.
4. Once they approve, make the minimum effective edit. Then run `eval.md` over your result yourself.
5. When a check fails, fix it and run the eval again.
6. Hand the result back in the form the draft came in (see above), with a short 'What changed' section.
7. Name any eval check you'd still call a fail after fixing. Claiming a clean pass on a draft with a real tension in it is worse than naming the tension.

## Diagnosis format

| Pattern | Line | Fix |
| --- | --- | --- |
| Faux-insight setup | 'What nobody tells you about churn' | Cut the setup, state the claim |
| Colon reveal | 'The secret ingredient: a weekly call' | Plain sentence |

If the draft is clean, say so. Don't manufacture findings to look thorough. 'This reads like you wrote it, three small things' is a complete answer.
