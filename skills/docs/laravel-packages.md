# Laravel packages

Stub. Expand when the first Laravel package gets the documentation treatment.

## What's already settled

- Writing style and README skeleton come from the universal docs.
- CHANGELOG format and rules: same as everywhere.
- Versioning is semver, with GitHub Releases per tag.
- No marketplace-style install. Packagist + `composer require <vendor>/<package>` is the install line.

## Anchors to fill in later

- `composer.json` required fields and constraints.
- Packagist registration and metadata.
- Laravel version compatibility matrix in README.
- Service provider registration block (manual vs auto-discovery).
- Publishing config and migrations: install steps and what to expect.
- Test command convention (pest, phpunit).
- Compatibility with Laravel Boost when relevant.
- Reference packages that nail this: spatie/laravel-permission, spatie/laravel-data, spatie/laravel-medialibrary.

## What probably stays different from Claude plugin conventions

- README is allowed to be longer for Laravel packages, especially when there's a substantial usage section. Spatie's pattern is acceptable up to ~150 lines before splitting into docs.
- Badges: add `packagist version`, `packagist downloads`, `tests` (if CI runs). The two-badge rule is Claude-plugin-specific.
- Install command is `composer require vendor/package`, not a marketplace handle.
