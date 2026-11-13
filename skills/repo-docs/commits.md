# Commit messages

Write a short subject in the imperative mood, with no period. 50 characters where possible, 72 hard max.

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

Leave the prefix off a commit at the repo root that touches several components or the repo itself.

For standalone repos, prefix with the affected subsystem when it tells the reader where the diff lands:

```
router: defer resolvePeerConfig into headless branch
queue: collapse three readMessage loops into one generator
```

Skip prefixes for one-line trivial commits ('Fix typo in README').

## Body

Optional. Add one when the subject can't carry the why. Wrap at 72 columns.

The body explains:
- Why the change was made. The diff already shows what changed.
- Any non-obvious trade-off.
- Issue references at the end, if any.

## What never goes in a commit message

- 'WIP', 'fixup', 'asdf'. Squash before pushing.
- Long lists of changed files. The diff is the diff.
- 'Made some changes', 'Updates', 'Fixes'. Be specific or don't commit yet.
- Co-author tags for AI-assisted work.
- Emojis at the start (no '✨ feat: ...').
