# README structure

Within 30 seconds of opening a README, the reader decides whether the thing solves their problem. In 60 more seconds, they install and try it. Everything else in it is for later.

## Universal skeleton

```markdown
# <Name>

<One-line tagline. Plain words. No hype.>

<2-3 sentences. What this is, what problem it solves, who it's for. Mention
hard dependencies here if they're not optional.>

## Installation

<Install command, one block. Minimal.>

### Requires

- Bullet list. Versions where they matter.

## Quick start

<Smallest working example. 3-10 lines.>

<One paragraph: what just happened, what to look at next.>

## Features

<4-8 bullets, one line each. Concrete capabilities, not promises.>

## Documentation

<If docs/ exists, link to each doc file. If not, drop this section.>

## Related

<Optional. Only when a real link adds value.>

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## Credits

- [Mischa Sigtermans](https://mischa.sigtermans.me)
- <inspirations or prior art, real attributions only>

## License

<License name>. See [LICENSE](LICENSE).
```

## Length budget

Aim for ~80 lines. If the README exceeds 100, move reference material into a `docs/` directory and link to it.

## docs/ directory

Use when reference material would bloat the README:

- `docs/commands.md`: slash commands and tools reference
- `docs/configuration.md`: config files, paths, environment
- `docs/architecture.md`: how it works internally
- `docs/authoring.md`: how to extend or write related plugins

Don't invent file names for the sake of structure. Add a doc file once there's content for it.

## Badges

Two badges directly under the title, and no others.

```markdown
[![Version](https://img.shields.io/github/v/release/mischasigtermans/<repo>?label=version)](https://github.com/mischasigtermans/<repo>/releases)
[![License](https://img.shields.io/github/license/mischasigtermans/<repo>)](LICENSE)
```

No downloads (Claude marketplaces don't expose them), no build status, no Discord, no X.

A Claude Code plugin's version badge reads `plugin.json` instead; `claude-plugins.md` has its line.

## What never goes in a README

- Benchmark tables, accuracy scores, consistency claims.
- Manifesto-style philosophy sections.
- 'Why I built this' personal narrative.
- Marketing language: 'transform', 'powerful', 'intuitive', 'next-generation'.
- AI-tells: 'I'd be happy to', 'let me know if'.
- See-also dumps that aren't real recommendations.
- Roadmap promises. If it's not shipped, don't list it.

## Order of work when rewriting a README

1. Read the current README. Note what works.
2. Read the codebase enough to know what the plugin actually does today, not what the README claims.
3. Draft the tagline and the 2-3 sentence intro first. Get them right before anything else.
4. Then installation and quick start. Run the commands to confirm they work.
5. Features list last. By now you know what belongs there.
