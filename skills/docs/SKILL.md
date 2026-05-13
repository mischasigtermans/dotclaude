---
name: docs
description: Activate when writing, reviewing, or restructuring documentation in any of Mischa's repos. Covers READMEs, CHANGELOGs, .github files, commit messages, versioning, and ecosystem-specific conventions for Claude Code plugins, Laravel packages, and apps. Use when the user asks to write or update a README, draft a CHANGELOG entry, tag a release, set up repo boilerplate, or align a repo with the house style.
---

# Documentation Standard

Mischa's writing voice is defined in `~/.claude/CLAUDE.md` under 'How you write'. That voice applies to everything you produce. The files in this directory codify the structural rules: what shape a README takes, how a CHANGELOG reads, how versions and tags work, how repo boilerplate is laid out.

## How to use this skill

1. **Always apply** the voice rules from `~/.claude/CLAUDE.md` under 'How you write', plus `readme.md` here for structure. Universal rules.
2. **Detect the ecosystem** by looking at the repo:
   - `.claude-plugin/plugin.json` or `.claude-plugin/marketplace.json` exists → read `claude-plugins.md`
   - `composer.json` exists → read `laravel-packages.md`
   - No package manifest, looks like a deployed app → read `apps.md`
3. **Load on demand**:
   - Writing a CHANGELOG entry → `changelog.md`
   - Tagging a release or planning versions → `versioning.md`
   - Setting up SECURITY, CONTRIBUTING, or issue templates → `github-files.md`
   - Writing commit messages → `commits.md`

## When invoked

State the plan in one line, then do the work. The rules are the rules; don't ask permission section by section.

If a rule here conflicts with what's in an existing repo, the rule wins. Existing drift is a backlog item, not a precedent.

If the user wants a different approach for a specific case, they'll say so. Until then, follow this skill.

## When this skill is wrong

This file is the source of truth. If a convention here proves bad in practice, edit the relevant file in this directory. Don't paper over it in individual repos.
