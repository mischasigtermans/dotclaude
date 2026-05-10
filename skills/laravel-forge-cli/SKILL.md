---
name: laravel-forge-cli
description: "Operate Laravel Forge servers and sites via the official `forge` CLI. Use for deploys, tailing production logs, pulling/pushing `.env`, restarting PHP/Nginx/databases/daemons, running remote artisan commands, opening Tinker or SSH sessions, and switching the active server. Trigger when the user mentions 'forge', 'deploy', 'prod logs', 'tail nginx', 'pull env', 'push env', 'restart php-fpm', 'ssh into the server', or 'run artisan on prod'. Do NOT use for site/SSL/firewall/cron/SSH-key/redirect provisioning, those require the Forge HTTP API."
allowed-tools: 'Bash(forge:*)'
---

# Laravel Forge CLI

The `forge` CLI is a deploy and ops tool. It can run things on existing servers and sites. It cannot provision new ones (no site/SSL/firewall/cron/SSH-key CRUD, those are API-only).

## Setup check

Before any other command, verify auth and the active server:

```
forge server:current
```

If this fails with an auth error, the user needs to run `forge login` (interactive) or export `FORGE_API_TOKEN`. Do not run `forge login` yourself, it is interactive.

If the active server is wrong, switch:

```
forge server:list
forge server:switch <name>
```

## Resolving the site

Most site-scoped commands take an optional `[domain]`. If the user does not specify one, run `forge site:list` and pick by name. Do not guess.

## Common workflows

### Deploy and watch

```
forge deploy <domain>
forge deploy:logs
```

`deploy:logs` shows the most recent deployment output. If the deploy failed, this is the first place to look.

### Tail application logs

```
forge site:logs <domain> --follow
```

Stops on Ctrl-C. For background tailing, run with `run_in_background: true`.

### Tail web server / PHP / database / daemon logs

```
forge nginx:logs
forge php:logs
forge database:logs
forge daemon:logs <id>
```

All accept `--follow`.

### Pull, edit, push `.env`

```
forge env:pull <domain> .env.production
# edit locally
forge env:push <domain> .env.production
```

`env:push` OVERWRITES the remote `.env`. Always `env:pull` first, diff against the local copy, and confirm with the user before pushing. Never push an `.env` that was not just pulled, the remote may have drifted.

### Run an artisan / shell command remotely

```
forge command <domain> --command="php artisan migrate --force"
forge command <domain> --command="php artisan cache:clear"
```

Runs as the site user, in the site root. Useful for migrations, cache clears, queue restarts.

### Tinker on prod

```
forge tinker <domain>
```

Interactive. Only suggest this when the user explicitly asks, do not start it as part of an automated flow.

### SSH

```
forge ssh
forge ssh <server-name>
```

Interactive. Use `ssh:test` to verify key auth without opening a shell:

```
forge ssh:test
```

If it fails, `forge ssh:configure` walks the user through key setup (interactive, do not run it yourself).

### Service status and restarts

```
forge nginx:status
forge php:status        # default PHP
forge php:status 8.4    # specific version
forge database:status
forge daemon:status <id>
```

```
forge nginx:restart
forge php:restart 8.4
forge database:restart
forge daemon:restart <id>
```

Restarts cause brief downtime (PHP/Nginx) or query interruption (database). Confirm with the user before restarting any service in production.

### Database shell

```
forge database:shell <db-name> --user=<user>
```

Interactive psql/mysql session.

### Daemons

```
forge daemon:list
forge daemon:status <id>
forge daemon:logs <id>
forge daemon:restart <id>
```

CRUD on daemons (create/delete) is API-only, not in the CLI.

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
