# CHANGELOG format

Derived from [Keep a Changelog](https://keepachangelog.com), tightened to Mischa's voice.

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
- One bullet per change. Multiple unrelated bullets in one entry? Split them.
- Each bullet states a fact. 'Removed `parley_attach`. Live routing is automatic now.' Not 'We've simplified routing!'

## Voice for CHANGELOG entries

Write the entry as if you're updating yourself in six months. You'll skim it looking for the line that explains the breakage you just ran into. Each line earns its place.

Don't praise yourself. Don't promote. Don't apologise.

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

In a library repo (e.g. `claude-personas`), there are two layers:

- **Repo-level CHANGELOG.md** at the root. Lists what changed across the library this release: new personas added, plugins removed, structural changes. Usually short.
- **Per-plugin CHANGELOG.md** inside each plugin directory. Lists what changed in that plugin specifically. Most releases only update one or two.
