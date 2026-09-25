# Common Workflows

Every command here is verified against the installed CLI. `forge list` for the full set.


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

### Tail web server / PHP / database / background-process logs

```
forge nginx:logs
forge php:logs
forge database:logs
forge background-process:logs <id>
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

Runs as the site user, in the site root. Useful for migrations, cache clears, queue restarts. It reports success or failure but does not echo the command's stdout, so to read remote state (a deployed commit, a file's contents) use a non-interactive `ssh <site-user>@<server-ip> "<cmd>"` instead.

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
forge background-process:status <id>
```

```
forge nginx:restart
forge php:restart 8.4
forge database:restart
forge background-process:restart <id>
```

Restarts cause brief downtime (PHP/Nginx) or query interruption (database). Confirm with the user before restarting any service in production.

### Database shell

```
forge database:shell <db-name> --user=<user>
```

Interactive psql/mysql session.

### Background processes

```
forge background-process:list
forge background-process:status <id>
forge background-process:logs <id>
forge background-process:restart <id>
```

CRUD on background processes (create/delete) is API-only, not in the CLI.

