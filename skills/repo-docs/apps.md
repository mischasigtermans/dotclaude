# Apps

Stub. Covers deployed applications, which don't ship to a registry.

An app README has its own audience: the next developer to join the codebase, often your future self.

## What's already settled

- Writing style and structural rules come from the universal docs.
- The README is shorter than a package README. No 'features' section, no 'install for users'.
- No CHANGELOG required. Apps version implicitly through deploys.
- No marketplace and no Packagist. The repo and its audience are internal.

## Anchors to fill in later

- A README aimed at onboarding, not adoption.
- Local development setup: Herd for Laravel, Sail or Docker for containerized stacks.
- Environment variables: which ones matter, which defaults are safe, where the example file lives.
- Deployment surface: Forge for Laravel apps, whatever fits for others.
- Test command and CI expectations.
- An architecture diagram or short prose when the codebase is non-trivial.
- Links to the auth and permission model, the main domain entities and the integration points.

## What an app README replaces

- 'Local development' replaces 'Installation'.
- 'Running the app' replaces 'Quick start'.
- 'Features' goes, or becomes a 'What this codebase does' section of 3-5 bullets about the domain.

## What never goes in an app README

- Marketing copy. The audience is the next engineer.
- Customer-facing positioning. That belongs on the public site.
- Public release notes. Internal deploy notes go in the team's chat or release tool.
