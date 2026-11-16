---
name: copywriter
description: "Write new product copy or sharpen existing text. Write mode builds product, launch and feature pages in Apple's style. Sharpen mode diagnoses and fixes AI-slop in any draft while keeping the writer's voice. Triggers on 'sharpen', 'sharpen this', 'make this less AI', 'does this read as AI', 'tighten this up', 'make it more direct', 'edit this draft', 'herschrijf dit strakker', 'maak dit minder AI', 'is dit goed geschreven', 'what do you think of this copy', 'review this text', 'wat vind je van deze tekst', 'wat denk jij ervan' about pasted copy, 'write copy for', 'product page', 'landing page copy', 'hero copy', 'tagline', 'headline for', 'schrijf de copy', 'productpagina'. Also runs in self-check mode on copy Claude wrote itself, when the sharpen-gate Stop hook asks for it."
---

# Copywriter

Two jobs in one skill. Write builds a product page from facts. Sharpen edits text that already exists. Pick the mode first, then load only the files that mode needs.

## Pick the mode

| What you got | Mode | Read |
| --- | --- | --- |
| A brief, a feature list or 'write the page for X' | Write | `write.md` |
| The word 'sharpen', or any existing draft: a post, an email, docs, a page | Sharpen | `sharpen.md` |
| Pasted copy with a request for an opinion ('what do you think', 'wat denk jij ervan') | Sharpen, diagnosis only | `sharpen.md` |
| An existing product page or section | Sharpen, plus the page check | `sharpen.md`, then `write.md` |
| 'Fix this headline', 'tighten this paragraph' | Point edit | `sharpen.md` |
| The sharpen-gate Stop hook sent you here, or you're about to hand over copy you wrote this turn | Self-check | `sharpen.md` |

State the mode in one line before you start.

Rules for picking:

- 'Sharpen' always means sharpen mode. Keep the writer's point, voice and structure. Never turn a blog post or an email into an Apple page.
- Write mode is for product pages only: product, launch, feature, comparison, hero, tagline. Other new prose needs no mode; write it, and self-check runs afterwards.
- Text the user wrote or pasted never goes through self-check. It gets the diagnosis first.
- When the request fits two modes and the choice changes the output, ask once.

## Files

| File | Holds | Used by |
| --- | --- | --- |
| `write.md` | Message stack, panel layers, headline toolkit, page architecture, page check | Write, page check |
| `sharpen.md` | Diagnose, then rewrite on their word. Self-check mode | Sharpen, point edit, self-check |
| `patterns.md` | The AI patterns, each with a fix | All modes |
| `principles.md` | How much to cut | Sharpen |
| `eval.md` | Checks to run on your own output | All modes |

## Rules for every mode

- **Never invent.** No made-up specs, numbers, customers, quotes or sources. Mark the gap `[NEED: ...]` or ask.
- **Word-level rules** (banned vocabulary, dashes, number and currency format, quote style) live in the user's own instructions and are already active. Don't restate them.
- **Headlines on product pages get two exceptions** to `patterns.md`: fragments, and a pair of two true facts ('More range. Less weight.'). They're defined at the top of `patterns.md` and hold in every mode, self-check included. Body copy gets no exceptions.
- **Run `eval.md`** over anything you return.
