---
name: team-update
description: Write a "Shipped" team update for a project from what actually landed in a window (since Friday, this week, since a date). Use when Mischa says 'team update', 'shipped update', 'stuur het team een update', 'what did we ship', 'schrijf een update voor <project>', or wants a casual product-progress ping for the team. One message per product. Grounds every claim in real commits and merged PRs, never a memory of what was planned.
---

# Team Update

A team update is a short, casual, benefit-first message about what shipped. Not a repo CHANGELOG (that's the `repo-docs` skill), not marketing copy. The reader is a teammate who wants to know what changed and why it matters, fast.

Mischa's writing voice in `~/.claude/CLAUDE.md` under 'How you write' applies to every word. This skill adds the shape and, more importantly, the discipline: **the message reports what the commits say, not what you remember being planned.**

## The one rule that matters most

**Every claim traces to a commit or a merged PR in the window. Nothing else goes in.**

The failure mode is announcing work as fresh when it shipped weeks ago, or claiming a thing is "live" when the branch that does it is still open. Both destroy trust in the update. So:

- **Date-check the headline feature.** Before you write "we shipped X", find the commit that shipped X and confirm it lands inside the window. A feature the user describes from memory may have merged two weeks ago. If it did, it is not this update's news, no matter how central it feels. Say so and leave it out.
- **"Live" needs proof.** Only write that something is live/deployed if a deploy or a merge-to-production actually happened. A merged feature branch is "shipped"; a cutover that's still sequenced is "next up", not "done". When unsure, check (deploy logs, the production branch, a running process) or downgrade the claim.
- **A user-supplied draft is a voice sample, not a fact source.** If Mischa pastes an example, match its tone and shape, then rebuild the content from the commits. Verify its specifics against history before reusing any of them.

If you can't point to the source for a line, cut the line. A shorter true update beats a fuller one that guesses.

## Gather the material

Work out the window first. "Since Friday" → last Friday's date. "This week" → Monday. A named date → that date. Convert to an absolute `YYYY-MM-DD` before querying.

Then pull what landed, from the repo you're in and any sibling repos/submodules that are part of the same product:

```
git log --since=<date> --pretty="%ad %s" --date=short
git log --since=<date> -1 --format="%b" <hash>   # bodies for the load-bearing commits
gh pr list --state merged --search "merged:>=<date>" --json number,title
gh pr list --state open --json number,title        # feeds the "In review" section
```

For monorepos, run it in each component (an API, a web app and a marketing site each carry their own history). For Linear-tracked work, `mcp__linear__list_issues` with a `completedAt`/`updatedAt` filter cross-checks what actually closed. Read commit bodies for the handful of headline items. The subject line rarely carries the user-facing benefit.

Group by outcome, not by commit. Three commits that together ship one capability are one bullet.

## Structure

Follow the shape of Mischa's canonical example (in `examples.md`), not a rigid template:

- **Header:** `Shipped this weekend 🚀` (or "today" / "this week" to match the window). The single 🚀 is wanted here and overrides the no-emoji rule in CLAUDE.md for this header only. No other emoji.
- **Lead with the headline.** The biggest thing first, in a short paragraph that says what it does for the reader before how it's built. "Search now finds notes by meaning, not just keywords" before "pgvector on Postgres".
- **Then the rest, grouped.** Each group is a short paragraph or a tight run of sentences: shared infrastructure, a robustness pass, bugs squashed. Name the concrete symptom for a fix ("Streaming errors now surface in the chat instead of showing a finished response with nothing in it"), never "various fixes".
- **Bonus, if there is one.** A second-order win worth calling out ("any tool that connects over MCP gets this for free").
- **In review:** what's built but not merged. Pulls from open PRs.
- **Next up:** what's genuinely next, stated as fact, not a teaser. Only things actually queued.

Benefit before mechanism throughout. Numbers over adjectives ("4.812 notes re-indexed, all green" beats "everything re-indexed"). No hype vocabulary: the banned list in CLAUDE.md applies here too.

## One message per product

If the window spans several products (two products both moved), write one message each, not a combined one. Teammates read the product they work on. Shared work (a package both adopted) is mentioned in both, framed for each.

## Deliver

Hand back clean copy, ready to paste, in English unless the team works in another language. Label each message by product. After the drafts, note in one line anything you deliberately left out and why (usually: shipped outside the window, or couldn't verify). That note is for Mischa, not the team.
