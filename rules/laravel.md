---
paths:
  - "**/*.php"
---

# Laravel

- Pint runs on the Laravel preset, nothing else. No `pint.json`, no custom rules.
- A Stop hook formats every PHP file you edited with Edit or Write. Format by hand only PHP that changed through a command or script, by path: `vendor/bin/pint <files>`.
- Never `pint --dirty`, whatever the project's Boost guidelines say: it formats files other sessions changed in the same working tree. A hook denies it.
- Never `pint --blade`. The Blade formatter moves whitespace around `{{ }}` and directives, and the rendered text changes while the view still compiles: '3 years, 5 months' becomes '3 years ,5 months', and adjacent words run together.
- A Laravel project with `livewire/flux` but without `livewire/flux-pro` gets it from `flux-activate` in the project root: a zsh alias for `php artisan flux:activate` with my license. Never write the license into a file or add flux-pro to `composer.json` by hand. It moves the `flux-pro` repository to the top of `composer.json`; put the order back and run `composer update --lock`.
- At `boost:install`, leave the Laravel Cloud integration unchecked. Its `deploying-to-cloud` skill duplicates the `laravel-cloud` plugin under another name.
