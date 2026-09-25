# Examples

The voice and shape to match. The discipline behind them is in `SKILL.md`.

## Canonical example (feature-led)

This is the reference for tone and structure. Note: benefit-first lead, one 🚀, concrete numbers, a "Bonus" second-order win, then "In review" and "Next up".

```
Shipped today 🚀

Search now finds notes by meaning, not just keywords. Until today, searching 'Q3 concerns' wouldn't find a note that says 'third-quarter worries'. Now it does. Semantic search runs in the backend itself (pgvector on Postgres), so everything in a workspace is searchable by what it means. Live on staging and production, all existing content re-indexed (4.812 notes on staging, all green).

Bonus: this doesn't just make search smarter. Any tool that connects to the app over MCP (Claude, Cursor, you name it) gets the same semantic search for free.

The inbox got smarter too. Moving an item to another folder no longer silently marks it done, and the folder picker shows a new folder straight away instead of after a reload. The UI half lands with the next web release.

Two bugs squashed along the way: a middleware bug that made embedding calls fail with a misleading error (a duplicated header, fun one to find), and PowerPoint uploads now work.

In review: the cleanup that moves the last product-specific code out of the shared agent runtime. After that, the runtime is fully product-agnostic.

Next up: deleting the old keyword index now that semantic search is live, and the web release for the inbox changes.
```

## Example: infrastructure-led update (platform migration)

Headline is a migration, not a feature. Note how "live" is scoped precisely: staging is on the new platform, the production cutover is "next up", and a known blocker is stated plainly rather than hidden.

```
Shipped this weekend 🚀

We're moving the app onto Laravel Cloud. This is the big one. Staging runs on Cloud now, with managed queues, managed search, R2 for storage and Nightwatch for monitoring. The production cutover and retiring the old servers are the next sequenced steps, so nothing's pulled out from under anyone yet.

Health checks got rebuilt for the new stack. The old Horizon check is gone, replaced by a schedule heartbeat that proves cron fires across instances, plus a search check.

Under the hood, the AI-orchestration layer moved into a shared package, so two products stop maintaining their own copy of it. Same code, one place to fix it.

Observability swap: Sentry and Telescope are out, Nightwatch is in. One tool instead of two.

Also shipped: per-account usage caps, and two build fixes. The asset build now fails loudly when a sub-build breaks instead of passing silently, and Redis falls back to the default connection instead of hardcoded values.

Known issue before cutover: search on staging throws a key-scope error. Fixing that first.

Next up: the production switch, retiring the old servers, then dropping Horizon entirely.
```
