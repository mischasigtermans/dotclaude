# Tag Taxonomy

Top-level tags and what they mean. Update this file when the taxonomy changes.


Top-level tags and their meanings (Mischa-specific; update this section when the taxonomy changes).

### `#ventures/<name>`: portfolio projects

One child tag per venture, e.g. `#ventures/acme`, `#ventures/northstar`. Run `bearcli tags` to see the live set before tagging.

Use a venture tag when the note is operationally about that venture (meeting notes, plans, decisions, tasks, drafts, promo material, customer comms). Use `#ideas` when the note is a raw concept not yet committed.

### `#ideas`: raw concepts not yet committed to a venture

Single flat tag. Promote to `#ventures/<name>` when the idea becomes a real project (specs, customers, money flowing, or you've otherwise decided to build it).

### `#personal/<sub>`: personal writing, reflections

One child per topic, e.g. `#personal/health` (wellbeing and inner work), `#personal/traits` (self-observed patterns), `#personal/other` (everything else personal: household, family, logistics). Cross-tag is fine and expected; a venture-adjacent personal reflection gets both tags.

### `#meetings`: cross-venture meeting notes

Only use when the meeting doesn't fit one specific venture. If it's a venture board meeting, tag that `#ventures/<name>` (optionally also `#meetings`). For ambient weekly check-ins, generic 1:1s, etc., `#meetings` alone is fine.

### `#tooling/<topic>`: AI/dev tooling

One child per topic, e.g. `#tooling/prompts`, `#tooling/pipelines`, `#tooling/social`. Tooling is *how* Mischa builds, not *what* he's building. A venture feature spec goes under that venture's tag, not tooling.

### `#reading/<medium>`: consumed content

One child per medium, e.g. `#reading/books`.

### `#people/<group>`: reserved

Top-level slot for contacts and per-person meeting notes (board, investors, team, partners). Available when needed.

### `#archive`: explicitly retired

Never auto-apply. Mischa decides what is archived.

## Creating new tags

The taxonomy is intentionally Mischa-shaped, not exhaustive. Rules for adding:

- **New top-level tag**: ask the user first. Top-level shape changes the whole tree.
- **New child under an approved parent** (especially `#ventures/<name>`): create without asking when (a) a new venture has its own dedicated Apple Notes folder, repo, or website, (b) the note count is plausibly >= 3, or (c) Mischa has referenced it by name as a venture in conversation. Mention the new tag in the response so it's visible.
- **One-off content** that doesn't match anything: use `#personal/other` or `#ideas` rather than inventing a tag.
- **When uncertain between two existing tags**: pick the more specific one. A note about a person's work on a venture gets both the `#ventures/<name>` and the relevant personal tag, not just one.

If a venture child tag turns out to be wrong (single note, never expanded, project abandoned), rename it to `#ideas` or merge with `bear_rename_tag`.

