# Commit messages

Short subject. Imperative mood. No period. 50 characters where possible, 72 hard max.

## Examples

```
Fix race in waitForMessage; rename-as-claim pattern
```

```
Add ParleyContext.getProjectId() with memoization
```

```
parley_peers: render plugin-typed peers as <plugin>@<marketplace>
```

## Subject prefixes

For library repos with multiple plugins (e.g. `claude-personas`), prefix the subject with the component scope:

```
manager: scan installed plugins for persona kind
personas/steve-jobs: drop bundled-language from README
```

Prefix-less commits at the repo root touch multiple components or the repo itself.

For standalone repos, prefix with the affected subsystem when it sharpens the diff signal:

```
router: defer resolvePeerConfig into headless branch
queue: collapse three readMessage loops into one generator
```

Skip prefixes for one-line trivial commits ('Fix typo in README').

## Body

Optional. Use when the subject can't carry the why. Wrap at 72 columns.

The body explains:
- Why this change, not what. The diff already shows what.
- Any non-obvious trade-off.
- Issue references at the end if applicable.

## What never goes in a commit message

- 'WIP', 'fixup', 'asdf'. Squash before pushing.
- Long lists of files changed. The diff is the diff.
- 'Made some changes', 'Updates', 'Fixes'. Be specific or don't commit yet.
- Co-author tags for AI-assisted work.
- Emojis at the start (no '✨ feat: ...').
