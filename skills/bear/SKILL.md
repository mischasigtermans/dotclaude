---
name: bear
description: "Formatting and tagging rules for Bear notes. Use when creating, editing, or migrating Bear notes, choosing tags, escaping inline hashtags in body content, or moving notes in from Apple Notes. Covers the tag taxonomy (ventures, personal, meetings, tooling, reading, ideas) and when to create a new tag. Triggers on 'add this to Bear', 'make a note', 'maak een notitie', 'tag this note', 'which tag', 'migrate my Apple Notes'."
---

# Bear

Standard formatting when adding, editing, or migrating Bear notes.

## Tag placement

Tags go on line 3, directly under the H1 title. Single line, space-separated, all tags on one line. Blank line between H1 and tags. Blank line between tags and body.

```
# Title

#tag1 #tag2/sub

Body...
```

Never place tags at the bottom of a note. If an existing note has tags at the bottom, move them to the canonical position.

## Writing style

Newly authored or edited content in Bear must follow the writing style rules in `~/.claude/CLAUDE.md` (active voice, no em dashes, no banned vocabulary, European number format, single quotes for speech, British punctuation).

This applies to:

- Notes created fresh in Bear
- Edits to existing Bear notes that touch prose
- New Bear notes derived from external sources where Claude wrote any framing or summary

This does NOT apply to:

- Content migrated verbatim from another source (see Migration rule below)

## Migration rule

When migrating notes from another source (e.g. Apple Notes) into Bear:

- Preserve content verbatim. Do not rewrite, restructure, or 'improve' prose. The user's prose is the user's prose.
- Only the structural shell changes: tag placement, H1 title at top, blank lines around the tag row.
- If a source note has no H1, derive one from the note title in the source app.
- If existing content violates the writing style rules, leave it alone during migration. Voice cleanup is a separate, explicit pass the user must request.

## Choosing a tag

Read `taxonomy.md` for the tag tree, what each top-level tag means, and the rules for creating a new one. Run `bearcli tags` first to see the live set.

## Hashtag escaping in body content

Bear treats any `#word` in body text as a tag. When migrating or pasting content that contains inline hashtags (promo posts with `#hardstyle`, shell scripts with `#!/bin/bash`, code comments, social media threads), escape the `#` to `\#` so it renders visually but doesn't pollute the tag taxonomy.

Exempt: lines that are actually markdown headings (`# `, `## `, `### `), meaning any `#` followed by a space). Those stay unescaped.

The canonical tag row directly under the H1 is the only place real `#tags` belong. Everywhere else in the body, escape.
