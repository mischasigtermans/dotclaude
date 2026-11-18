# Write: product pages

You write product pages the way Apple's marketing team does. The product is the hero. Every section sells one idea. Every clever line sits on a hard fact.

The method in four lines:
- The headline makes them feel it.
- The subhead tells them what it is, in one plain sentence.
- The body proves it with a number or a mechanism.
- The footnote keeps it honest.

Existing copy doesn't start here. It goes through `sharpen.md` first, which uses this file for its page check.

## Before writing

If a product context file exists (`.agents/product-marketing.md`, `.claude/product-marketing.md`, `product-marketing-context.md`), read it first. Ask only for what it doesn't cover.

You need four things:
1. **What's new.** The one thing this product or release does that the last version, or the old way, didn't. If nobody can name it, stop and ask. The page is built around it.
2. **Who's reading and what they know.** Existing users read a launch page differently than strangers. Fluent readers can take feature names without explanation.
3. **The proof inventory.** Specs, measured results, comparisons with the previous version or the status quo, materials, mechanisms, prices. Copy is built from this list, so write the list before any copy.
4. **Page type and language.** Product page, launch page, feature page, comparison, or a single section.

If the user wants a draft now, draft it and mark gaps as `[WIP: ...]`. Never fill a gap with an invented number.

## Step 1: Build the message stack

Rank the proof inventory into 3 to 6 messages, biggest first. Each message becomes one section (a panel). Apple opens product pages by stacking the biggest messages at the top, one line each, so a reader who scrolls no further still gets the story.

One panel, one idea. If a panel's headline needs 'and', split the panel.

The biggest message gets the most room. Equal space for every feature reads as a spec dump.

## Step 2: Write each panel in layers

| Layer | Job | Rules |
|---|---|---|
| Eyebrow (optional) | Name the feature | 1 to 3 words. The feature's proper name |
| Headline | Make them feel it | 2 to 8 words. Devices allowed here and nowhere else |
| Subhead | State the claim | One full sentence a skimmer can read alone |
| Body | Prove it | 1 to 3 sentences. At least one number or mechanism |
| Footnote | Keep it honest | Every number or comparison gets a marker and its test conditions |

Hardware example (fictional headphones):
- Eyebrow: Noise cancellation
- Headline: Mute the commute.
- Subhead: Hush One cancels twice as much noise as the previous generation, so a full train sounds like an empty room.¹
- Body: Six outward microphones measure the noise around you 48.000 times a second. The onboard chip plays the opposite wave before the sound reaches your ear.
- Footnote: ¹ [WIP: test conditions, date, comparison model]

Software example (fictional booking platform):
- Eyebrow: Contracts
- Headline: Signed before soundcheck.
- Subhead: An accepted offer becomes a signed contract in the same thread, with every term already filled in.
- Body: Send the offer. The promoter accepts. The contract fills in from the booking data and goes out for signature. Agencies close a booking in 2 days instead of 9.²
- Footnote: ² [WIP: source of the 2 vs 9 figure]

## Step 3: The headline toolkit

These are the devices Apple's pages repeat. Pick at most one per headline.

| Device | How it works | Apple | Applied |
|---|---|---|---|
| Keyword repetition | Reduce the section to one word and repeat it | 'Your photo. Your font. Your widgets. Your iPhone.' | 'Your roster. Your rates. Your rider.' |
| Paired opposites | Two true facts pulling in opposite directions | 'Much more detail. In much less light.' | 'More range. Less weight.' |
| Double meaning | One phrase carries the benefit and a second reading | 'A huge Plus' (battery life, and the name iPhone 14 Plus) | 'Booked solid.' |
| Rhyme | Sound makes it stick | 'Fast that lasts.' | 'Mute the commute.' |
| Idiom twist | Swap one word in a familiar phrase | 'Rebuilt from the sound up.' | 'Love at first fit.' |
| Coined word | A made-up word that decodes instantly. Once per page, max | 'A camera in a class by itselfie.' | |
| Self-superlative | Beat your own previous version | 'Our longest battery life ever.' | 'Our fastest sync yet.' |
| Plain fact | No device. The fact carries it | 'Crash Detection calls for help when you can't.' | 'Payouts land the next morning.' |

Rules:
- **True-underneath test.** Strip the wordplay. A specific claim must remain, and the subhead must state it. A pun with nothing under it is decoration.
- **One-read test.** If the headline needs a second read to decode, cut it.
- **Ration.** Devices in half the headlines at most. The rest are plain facts. A page where every line performs reads as a gimmick, and these days as AI.
- **Serious stays straight.** Health, safety, privacy, money and legal topics get plain headlines. No puns on crash detection or data loss.
- **Swap test.** If a competitor could run the headline unchanged, rewrite it. Apple's lines name their own feature or their own number.
- Write 3 candidates per headline, keep one, fix its weakest word, lock it.

Fragments and paired opposites are the two headline exceptions to `patterns.md`. They stop at the headline. Body copy follows every pattern.

## Step 4: Body copy

- **Feature, advantage, benefit, in one chain**, ending on what it does for the reader. Apple's flash copy names the nine LEDs and their adaptive pattern, then lands on 'so your subject always appears in the best light.'
- **Numbers over adjectives.** 'Up to 26 hours of video playback' beats 'all-day battery'. Every 'up to' gets a footnote.
- **Mechanism when there's no number.** Say how it works in one sentence a smart outsider follows.
- **Compare with yourself or the old way.** Previous generation, the spreadsheet, the email thread. Don't name competitors.
- **The reader is the subject.** More 'you' and 'your' than the product name. One analysis of the iPhone 14 page counted 41 against 20.
- **Objections become features.** Durability, battery, privacy, environment, price. Answer each where it comes up, with a fact.
- **Short sentences, plain words.** Starting with 'And' or 'But' is fine. Most important point first in every paragraph.
- **Name what's worth owning.** A capitalised feature name (Crash Detection, Dynamic Island) makes a feature memorable and ownable. Three named features per page at most. Name everything and nothing sticks.
- **Let the visual talk.** If the image already says it, cut the line. Whitespace is part of the copy.

## Step 5: Page architecture

1. **Hero.** Product name, a tagline of 2 to 5 words, one line with price or availability, two CTAs (buy or start, and learn more).
2. **Highlights.** The message stack, one line each. A skimmer's complete story.
3. **Panels.** One per message, in rank order. The top message gets the most room.
4. **Comparison.** Against the previous version or the old way. A table with numbers.
5. **Objections.** Privacy, durability, support, environment, price. Short panels with facts.
6. **Specs and FAQ.**
7. **Close.** The lineup or the buy CTA. End on the offer, not on a slogan.

**Skimmer test:** read only the headlines and subheads, top to bottom. They must tell the whole story on their own.

## Voice

- Confident, warm, plain. Never loud: no exclamation marks, no capitals for emphasis.
- One moment of play per page: a coined word, a conversational aside, a stretched vowel.
- Headlines in sentence case. Statement headlines end with a period. Pick one rule per page and hold it.
- Write each language natively. Wordplay does not translate. Rebuild every device in the target language and keep the numbers and footnotes identical.

## Product-page traps

`patterns.md` is the full list. These are the ones product pages fall into most:

- **Generic SaaS words:** unlock, effortless, revolutionary, cutting-edge, best-in-class, world-class, game-changer, all-in-one, next level, 'X, reimagined', 'the future of X'. Replace each with the fact it stands in for.
- **Fragment drumbeats in body copy.** Fragments belong in headlines. Body copy is sentences.
- **Negation lists:** 'No setup. No contracts. No hassle.' Say what happens instead. One real absence ('No card required') next to the CTA is fine.
- **Slogan closers:** 'Because you deserve better.' End on the offer.

## Honesty

- Every number and comparison gets a footnote with conditions. Collect them at the bottom.
- 'Our fastest' needs a previous version to beat. 'The fastest' needs a benchmark and a source.
- When you decline a claim, name the evidence that would unlock it.

## Checks before delivering

1. Skimmer test passes.
2. Every headline passes true-underneath, one-read and swap.
3. Devices in half the headlines at most. One coined word per page at most.
4. Every number has a footnote.
5. `eval.md` passes on the body copy.
6. Read it aloud. Mark any line that sounds like a press release.

## Output

```
MODE: write
MESSAGE STACK
1. ...
HERO
Name / Tagline / Price line / CTA 1 / CTA 2
HIGHLIGHTS
...
PANEL 1: [eyebrow]
Headline
Subhead
Body
Alternatives: 2 headlines, one-line rationale each
...
FOOTNOTES
OPEN [WIP] ITEMS
```

## Sources

Built from analyses of Apple product pages (Enchanting Marketing and Widewail, both 'Write like Apple') and the honesty rules in coreyhaines31/marketingskills `copywriting` (MIT), adjusted where Apple's style conflicts with them.
