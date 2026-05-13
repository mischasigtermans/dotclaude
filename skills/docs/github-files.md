# .github/ map

Optional. Add when there's a real chance external contributors will arrive, or when a repo has matured past the experiment stage.

## SECURITY.md

One paragraph. Where and how to report vulnerabilities.

```markdown
# Security

Report security issues by email to mischa@sigtermans.me. Don't open public
issues for vulnerabilities. Expect a response within a few days.
```

Add this once a repo is public and people might find an issue. Cheap insurance.

## CONTRIBUTING.md

One page. The minimum a contributor needs to ship a PR:

- Local setup steps that actually work today.
- How to run the tests.
- Commit message convention (point at the house style or restate briefly).
- PR style: one logical change per PR, descriptive title, link to the issue when relevant.

Don't write a CONTRIBUTING that you wouldn't read.

## ISSUE_TEMPLATE/

Add only when issues start arriving with insufficient info. Don't pre-empt.

When you do add templates:

- `bug.md`: title format, repro steps, what you expected, what happened, version.
- `feature.md`: problem statement first, proposed solution second, prior art if relevant.

## What never goes in .github/

- PR templates with mandatory checklists. They add friction without changing PR quality.
- Generic 'be respectful' code of conduct boilerplate copy-pasted from contributor-covenant. Either write one that means something or skip it.
- FUNDING.yml unless you actively want sponsorship for that repo.
- Generic dependabot configs that nobody reviews.
