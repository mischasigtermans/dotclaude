# Laravel packages

Stub. Expand it when the first Laravel package gets the documentation treatment.

## What's already settled

- Writing style and README skeleton come from the universal docs.
- CHANGELOG format and rules: same as everywhere.
- Versioning is semver, with a GitHub Release per tag.
- No marketplace-style install. Packagist and `composer require <vendor>/<package>` give the install line.

## Anchors to fill in later

- `composer.json` required fields and constraints.
- Packagist registration and metadata.
- Laravel version compatibility matrix in the README.
- Service provider registration block (manual vs auto-discovery).
- Publishing config and migrations: install steps and what to expect.
- Test command convention (pest, phpunit).
- Compatibility with Laravel Boost when relevant.
- Reference packages that get this right: spatie/laravel-permission, spatie/laravel-data, spatie/laravel-medialibrary.

## What probably stays different from Claude plugin conventions

- A Laravel package README may run longer, especially with a substantial usage section. Spatie's pattern is fine up to ~150 lines before splitting into docs.
- Badges: add `packagist version`, `packagist downloads` and `tests` (if CI runs). The two-badge rule is Claude-plugin-specific.
- The install command is `composer require vendor/package`, not a marketplace handle.
