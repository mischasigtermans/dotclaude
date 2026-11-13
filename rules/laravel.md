---
paths:
  - "**/*.php"
---

# Laravel

- Pint runs on the Laravel preset, nothing else. No `pint.json`, no custom rules.
- A Stop hook formats every PHP file you edited with Edit or Write. Format by hand only PHP that changed through a command or script, by path: `vendor/bin/pint <files>`.
- Never `pint --dirty`, whatever the project's Boost guidelines say. A hook denies it.
- Never `pint --blade`. The Blade formatter moves whitespace around `{{ }}` and directives, and the rendered text changes while the view still compiles: '3 years, 5 months' becomes '3 years ,5 months', and adjacent words run together.
- A Laravel project with `livewire/flux` but without `livewire/flux-pro` gets it from `flux-activate` in the project root: a zsh alias for `php artisan flux:activate` with my license. Never write the license into a file or add flux-pro to `composer.json` by hand. It moves the `flux-pro` repository to the top of `composer.json`; put the order back and run `composer update --lock`.
- At `boost:install`, leave the Laravel Cloud integration unchecked. Its `deploying-to-cloud` skill duplicates the `laravel-cloud` plugin under another name.
- Herd's RustFS 1.0.0 is the local S3, and its recursive listing stops at 2.000 objects without an error: `Storage::allFiles()` on a bigger bucket returns 2.000. Per-directory listing (`files()`, `directories()`) and `rclone --disable ListR` return everything. A production S3 lists in full, so a count that only differs locally is RustFS, not the code.
- Never run `herd secure` from a session. Without keychain access it writes the site's Nginx file and key but no `.crt`, reports success, and Nginx then refuses its config: every `.test` site goes down, and `herd unsecure` leaves the broken file. Ask me to secure a site in the Herd app. A hook denies it.
- Under `herd share`, never start a Vite dev server: it writes a broken tunnel address into `public/hot`, and the shared site loses its CSS and fonts.
- PHP on the CLI locally has `memory_limit` 4096M; `cloud command:run` on Laravel Cloud runs with 256M, whatever the instance holds. Before trusting a large command or job on Cloud, run it locally with `php -d memory_limit=256M artisan …`.
- Before inventing a pattern, look for the one my other Laravel apps already use (`rules/projects.md` says where they live).
- Larastan types a property's reads from its accessor's `Attribute` generic, so a set-only `Attribute::set()` (`Attribute<never, T>`) types every read of that property as `never` and a full `phpstan analyse` fails where a per-file run passed. A mutator alone is `Attribute::make(get: fn ($value) => $value, set: …)`.
