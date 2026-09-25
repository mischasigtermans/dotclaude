---
name: laravel-forge
description: "Operate Laravel Forge servers and sites via the official `forge` CLI. Use for deploys, tailing production logs, pulling/pushing `.env`, restarting PHP/Nginx/databases/background processes, running remote artisan commands, opening Tinker or SSH sessions, and switching the active server. Trigger when the user mentions 'forge', 'deploy to Forge', 'deploy' in a project that runs on Forge, 'prod logs', 'tail nginx', 'pull env', 'push env', 'restart php-fpm', 'ssh into the server', or 'run artisan on prod'. Do NOT use for site/SSL/firewall/cron/SSH-key/redirect provisioning, those require the Forge HTTP API."
allowed-tools: 'Bash(forge:*)'
---

# Laravel Forge CLI

A deploy and ops tool for existing servers and sites. It cannot provision new ones: no site, SSL, firewall, cron or SSH-key CRUD, those are API-only.

## Setup check

Before any other command, verify auth and the active server:

```
forge server:current
```

If this fails with an auth error, the user needs to run `forge login` (interactive) or export `FORGE_API_TOKEN`. Do not run `forge login` yourself, it is interactive.

Server-scoped commands need an organization and a server selected. If a command reports "You have not selected an organization", pick one:

```
forge organization:list
forge organization:switch <slug>
```

If the active server is wrong, or no server is selected, switch. With no server selected, `server:current` and every server-scoped command fail with the unhelpful `The resource you are looking for could not be found.` rather than naming the real problem. `server:list` still works, so use that to confirm auth is fine before assuming something worse:

```
forge server:list
forge server:switch <name>
```

## Resolving the site

Most site-scoped commands take an optional `[domain]`. If the user does not specify one, run `forge site:list` and pick by name. Do not guess.

## Workflows

Read `workflows.md` for deploys, log tailing, env pull/push, remote artisan, Tinker, SSH, service status and restarts, database shell, and background processes.

## Safety rules

1. **Never run `env:push` without a fresh `env:pull` and a diff.** Remote drift will silently overwrite production secrets.
2. **Never restart a service in production without explicit user confirmation.** Even short downtime is user-visible.
3. **Never run destructive artisan commands via `forge command` without confirmation.** This includes `migrate:fresh`, `migrate:rollback`, `db:wipe`, `cache:clear` on a hot cache, `queue:flush`.
4. **Do not start interactive sessions (`tinker`, `ssh`, `database:shell`, `login`, `ssh:configure`) on the user's behalf.** Suggest the command, let them run it.
5. **Confirm the active server before any write.** `forge server:current` first if there is any doubt about which server a command will hit.

## When to escape to the API

If the user asks to create/delete a site, manage SSL certs, open a firewall port, add a scheduled job, manage SSH keys, or set up redirects, the CLI cannot do it. Tell the user, do not improvise with `curl`. Provisioning belongs in the Forge dashboard or a separate API-based skill.

## Reference

- Full command list: `forge list`
- Per-command flags: `forge <command> --help`
- Docs: https://forge.laravel.com/docs/cli
