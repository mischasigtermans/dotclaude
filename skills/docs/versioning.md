# Versioning and releases

Semver. Tags. GitHub Releases. No mystery.

## Per repo

- Each repo carries its own version line.
- Bump version in `plugin.json` (or `composer.json`, etc.) on every release.
- Pre-1.0: bump minor for breaking changes, patch for everything else.

## Release procedure

1. Update `version` field in the plugin manifest.
2. Write the CHANGELOG entry for the new version.
3. Commit: `Release v0.3.0` (or a more specific subject if the release fits in one).
4. Tag: `git tag v0.3.0`.
5. Push: `git push && git push --tags`.
6. Create a GitHub Release for the tag. Body = the CHANGELOG section for that version, copied verbatim.

## Tag format

`vMAJOR.MINOR.PATCH`. The `v` prefix is non-negotiable; the shields.io version badge and downstream tooling expect it.

## GitHub Releases

Every tag gets a GitHub Release. This gives users:

- A canonical download for a versioned tarball.
- A target for the shields.io version badge.
- A readable summary on the Releases tab.

Skip GitHub Releases only for stub repos with no published version yet.

## Library repos (multiple plugins in one repo)

For repos like `claude-personas` that contain independent plugins:

- Repo-level tags. `v0.2.0` at the repo means 'as of this commit, the state of every plugin inside'.
- Each plugin's own `plugin.json` keeps its own version. They don't need to match. The Personas manager can be 0.3.0 while Steve is 0.1.0.
- The repo CHANGELOG covers what changed across the library this release.
- Each plugin's own CHANGELOG covers what changed in that plugin specifically.
- Most library releases touch one or two plugins. The repo tag still bumps; the plugin.jsons that didn't change keep their version.

## When to cut a release

- A new feature lands and works end to end.
- A bug fix that affects real users is on `main`.
- A breaking change is ready, and the CHANGELOG migration steps are written.

Don't cut a release to 'round out a sprint'. Tag because the code is ready, not because the calendar said so.

## What never goes in a release

- Half-finished features behind feature flags. Either ship them or don't.
- Speculative API changes. Land them when there's a real use case.
- Renamed files just to satisfy aesthetics. Plugin caches and downstream installs pay for every rename.
