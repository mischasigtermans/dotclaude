# .github/ map

Optional. Add these files when external contributors are likely to arrive, or when a repo has matured past the experiment stage.

## SECURITY.md

One paragraph: where and how to report vulnerabilities.

```markdown
# Security

Report security issues by email to mischa@sigtermans.me. Don't open public
issues for vulnerabilities. Expect a response within a few days.
```

Add this once a repo is public and people might find an issue. It costs one paragraph.

## CONTRIBUTING.md

One page with the minimum a contributor needs to ship a PR:

- Local setup steps that work today.
- How to run the tests.
- Commit message convention (point at the house style or restate it briefly).
- PR style: one logical change per PR, descriptive title, link to the issue when relevant.

Don't write a CONTRIBUTING that you wouldn't read.

## ISSUE_TEMPLATE/

Add templates only once issues start arriving without enough information, not before.

When you add them:

- `bug.md`: title format, repro steps, what you expected, what happened, version.
- `feature.md`: problem statement first, proposed solution second, prior art if relevant.

## What never goes in .github/

- PR templates with mandatory checklists. They add friction without improving PRs.
- A generic 'be respectful' code of conduct copy-pasted from contributor-covenant. Write one that means something or skip it.
- FUNDING.yml, unless you actively want sponsorship for that repo.
- Generic dependabot configs that nobody reviews.
