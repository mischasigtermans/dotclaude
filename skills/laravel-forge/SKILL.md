---
name: laravel-forge
description: "Operate existing Laravel Forge servers and sites through the Forge CLI: deploys, logs, environment files and service commands. Use for Forge operations; provisioning requires its API."
allowed-tools: 'Bash(forge:*)'
---

# Laravel Forge CLI

A deploy and ops tool for existing servers and sites. It can't provision new ones. Site, SSL, firewall, cron and SSH-key CRUD are API-only.

## Setup check

Before any other command, verify auth and the active server:

```
forge server:current
```

If this fails with an auth error, the user needs to run `forge login` (interactive) or export `FORGE_API_TOKEN`. Don't run `forge login` yourself; it's interactive.

Server-scoped commands need an organization and a server selected. If a command reports `You have not selected an organization`, pick one:

```
forge organization:list
forge organization:switch <organization>
```

If the active server is wrong, or no server is selected, switch. With no server selected, `server:current` and every server-scoped command fail with the unhelpful `The resource you are looking for could not be found.` rather than naming the real problem. `server:list` still works, so use that to confirm auth is fine before assuming something worse:

```
forge server:list
forge server:switch <name>
```

## Resolving the site

Most site-scoped commands take an optional `[site]`, the site name `forge site:list` shows (the site's domain). If the user doesn't name one, run `forge site:list` and pick by name. Don't guess.

## Workflows

Read `workflows.md` for deploys, log tailing, env pull/push, remote artisan, Tinker, SSH, service status and restarts, database shell, and background processes.

## Safety rules

1. **Never run `env:push` without a fresh `env:pull` and a diff.** Remote drift will silently overwrite production secrets.
2. **Never restart a service in production without explicit user confirmation.** Even short downtime is user-visible.
3. **Never run destructive artisan commands via `forge command` without confirmation.** This includes `migrate:fresh`, `migrate:rollback`, `db:wipe`, `cache:clear` on a hot cache, `queue:flush`.
4. **Never start interactive sessions (`tinker`, `ssh`, `database:shell`, `login`, `ssh:configure`) on the user's behalf.** Suggest the command and let them run it.
5. **Read remote state over `ssh <site-user>@<server-ip> '<cmd>'`, never through `forge command`.** `forge command` queues the command, then prints the output and status of the first entry in the site's command history, which it fetches without a sort order, so what it prints can belong to an older command. The IP is in `forge server:list`; `ssh` with a command is non-interactive and fine to run.
6. **Confirm the active server before any write.** `forge server:current` first if there is any doubt about which server a command will hit.

## When to escape to the API

If the user asks to create/delete a site, manage SSL certs, open a firewall port, add a scheduled job, manage SSH keys, or set up redirects, the CLI can't do it. Tell the user, and don't improvise with `curl`. Provisioning belongs in the Forge dashboard or the Forge API.

## Reference

- Full command list: `forge list`
- Per-command flags: `forge <command> --help`
- Docs: https://forge.laravel.com/docs/cli
