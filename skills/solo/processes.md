# Processes

## Process management over Bash backgrounding

If a command outlives one tool call (dev server, watcher, log tail, queue worker), put it in Solo, not in `Bash(run_in_background: true)`.

- `spawn_process` / `start_process`: start it
- `wait_for_bound_port`: block until the server listens on its port
- `get_process_output`: read recent output
- `search_output` with a regex: find specific lines without dumping the whole buffer
- `clear_output` before a fresh run so old logs don't confuse you
- `restart_process` / `stop_process` / `close_process`: lifecycle
- `get_process_ports` / `services_list`: what's listening where

Solo keeps the process visible in the user's IDE between sessions. Bash backgrounding doesn't.

**Output hygiene:** never read the full buffer when a `search_output` regex would do. The user has to scroll past everything you read.

## Project stacks (solo.yml)

Repos define their dev stack in a `solo.yml` at the repo root; Solo syncs it into its DB. This is the source of truth for what runs in a project.

- Reference processes by name: ids are volatile. Typical flow: `get_project_status` → find the process by name → act on it.
- Each command runs from its `working_dir`, so a command that re-`cd`s into it (`cd web && npm run dev`) lands one level too deep and fails.
- Editing `solo.yml` mid-session needs re-trust: the process keeps running the old stored command until the change is approved in the Solo UI. You can't force this from MCP.
- Debug a failing service by tailing its output (`get_process_output` / `search_output`), not by restarting blindly. Slow starters (an `npm install` before `npm run dev`) look dead before they're up.
- Before spawning any background server, check whether a Solo process already covers it.
- Process names say the role, with the tool in parentheses only when the role alone doesn't: `Platform API`, `Assets (Vite)`, `Queue (Horizon)`, `Logs (Pail)`, `Scheduler`, `Tunnel (Herd)`. Never a port in the name; `get_process_ports` has it. `rename_process` updates `solo.yml` without a restart.

Projects with wiring that goes beyond `solo.yml` (custom container orchestration, health-check ordering) document it in their own `.claude/skills/` skill. Check for one before improvising.
