# CHANGELOG format

Based on [Keep a Changelog](https://keepachangelog.com), tightened to Mischa's voice.

## Skeleton

```markdown
# Changelog

## [0.3.0] - 2026-05-12

<Optional one-paragraph release summary. Use when the release tells a story
worth narrating. Skip on routine bug-fix releases.>

**Breaking**
- <change> + impact + workaround when relevant

**Added**
- <new capability> with the public surface that exposes it

**Changed**
- <change to existing behavior or internals>

**Fixed**
- <bug fix> + the scenario it covered

**Migration**
<When applicable. Concrete steps to upgrade. Name files and paths.>

## [0.2.0] - 2026-05-09

- Initial release.
```

## Rules

- Versions follow [semver](https://semver.org). Pre-1.0, bump minor for breaking changes.
- Dates in `YYYY-MM-DD`.
- Most recent release at the top.
- Section order: Breaking, Added, Changed, Fixed, Migration. Drop sections that don't apply.
- One bullet per change. Split a bullet that holds unrelated changes.
- Each bullet states a fact, such as 'Removed `parley_attach`. Live routing is automatic now.' Never a pitch such as 'We've simplified routing!'

## Voice for CHANGELOG entries

Write for yourself six months from now, skimming for the line that explains the breakage in front of you. Cut every line that doesn't help that search.

No self-praise, no promotion, no apology.

## When the release deserves a summary paragraph

Use it when:
- A breaking change reshapes how the plugin is used.
- A feature lands that changes the plugin's positioning.
- A migration requires care or carries trade-offs worth explaining.

Skip it when:
- The release fixes a bug. The bug bullet is enough.
- The release ships a small feature with no broader implication.
- You're tempted to write filler.

## Library repo CHANGELOGs

A library repo (e.g. `claude-personas`) keeps two layers:

- A repo-level `CHANGELOG.md` at the root lists what changed across the library this release: new personas added, plugins removed, structural changes. Usually short.
- A per-plugin `CHANGELOG.md` inside each plugin directory lists what changed in that plugin. Most releases update only one or two.
