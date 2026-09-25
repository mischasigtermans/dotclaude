# RTK

A hook rewrites shell commands through `rtk` to reduce token output.

- If output looks unexpectedly empty or filtered: `rtk proxy <cmd>` to bypass
- rtk condenses the output of `git diff`, `diff`, `grep`, `find`, `phpstan`, `prettier --check` and `eslint`. When output decides something, run it through `rtk proxy`; for phpstan, prettier and eslint trust the exit code or JSON output, since their text is rewritten even inside scripts.
- `rtk gain`: token savings analytics
- `rtk discover`: find missed optimization opportunities
