# Apps

Stub. For projects like Onoma and Stagent that are deployed applications, not distributed packages.

Apps don't ship to a registry. Their README serves a different audience: future developers (often your future self) joining the codebase.

## What's already settled

- Writing style and structural rules come from the universal docs.
- README is shorter than a package README. No 'features' section, no 'install for users'.
- No CHANGELOG required. Apps version implicitly through deploys.
- No marketplace, no Packagist. Internal repo, internal audience.

## Anchors to fill in later

- README aimed at onboarding, not adoption.
- Local development setup: Herd for Laravel, Sail or Docker for containerized stacks.
- Environment variables: what matters, what defaults are safe, where the example file lives.
- Deployment surface (Forge for Laravel apps; whatever for others).
- Test command and CI expectations.
- Architecture diagram or short prose when the codebase is non-trivial.
- Links to the auth/permission model, the main domain entities, the integration points.

## What an app README replaces

Instead of 'Installation' → 'Local development'.
Instead of 'Quick start' → 'Running the app'.
Instead of 'Features' → either drop it, or a 'What this codebase does' section that's 3-5 bullets about the domain.

## What never goes in an app README

- Marketing copy. The audience is the next engineer.
- Customer-facing positioning. That belongs on the public site.
- Public release notes. Internal deploy notes go in the team's chat or release tool.
