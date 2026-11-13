# RTK

A hook rewrites shell commands through `rtk` to reduce token output.

- rtk condenses most read commands: `ls`, `cat`, `wc`, `tree`, `find`, `grep`, `diff`, `git status` and `git diff`, and the reports of `phpstan`, `prettier --check` and `eslint`. A line such as `(1 filtered)` or `[+1 hidden: rtk recall <hash>]` marks what it left out, and `rtk recall <hash>` prints it.
- When output decides something, or looks unexpectedly empty, run the command through `rtk proxy <cmd>`. For phpstan, prettier and eslint trust the exit code or JSON output, since their text is rewritten even inside scripts.
