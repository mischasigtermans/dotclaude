---
name: repo-docs
description: "Activate when writing, reviewing, or restructuring documentation in any of Mischa's repos. Covers READMEs, CHANGELOGs, .github files, commit messages, versioning, and ecosystem-specific conventions for Claude Code plugins, Laravel packages, and apps. Triggers on 'write a README', 'update the readme', 'draft a changelog entry', 'write a commit message', 'tag a release', 'set up repo boilerplate', 'align this repo with the house style'."
---

# Documentation Standard

The examples in these files carry the author's own values: his name, the `by-mischa` marketplace, his security address, and his badge and credit URLs. In someone else's repo, substitute the repo owner's.

The user's own writing rules apply to everything you produce. The files in this directory hold the structural rules: what shape a README takes, how a CHANGELOG reads, how versions and tags work, how repo boilerplate is laid out.

## How to use this skill

1. Always apply the user's own writing rules, and `readme.md` here for structure. These two are the universal rules.
2. Detect the ecosystem from the repo:
   - `.claude-plugin/plugin.json` or `.claude-plugin/marketplace.json` exists → read `claude-plugins.md`
   - `composer.json` exists → read `laravel-packages.md`
   - No package manifest, looks like a deployed app → read `apps.md`
3. Load the rest on demand:
   - Writing a CHANGELOG entry → `changelog.md`
   - Tagging a release or planning versions → `versioning.md`
   - Setting up SECURITY, CONTRIBUTING, or issue templates → `github-files.md`
   - Writing commit messages → `commits.md`

## When invoked

State the plan in one line, then do the work. Don't ask permission section by section.

Explicit project conventions take precedence. Use this house style where the project leaves the choice open, and report conflicting conventions before you change them.

Follow this skill until the user asks for a different approach in a specific case.

## When this skill is wrong

This directory is the source of truth. If a convention here proves bad in practice, edit the relevant file here. Don't paper over it in individual repos.
