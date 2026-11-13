# Common Workflows

Every command and flag here is checked against Forge CLI 2.0.0. `forge list` for the full set, `forge <command> --help` for a command's arguments and flags.

### Deploy and watch

```
forge deploy <site>
forge deploy:logs <site>
```

`deploy:logs` shows the most recent deployment output. Look there first when a deploy fails.

### Tail application logs

```
forge site:logs <site> --follow
```

Stops on Ctrl-C. To keep tailing while you work, run it as a background process; with Solo in use, that is a Solo process (`solo`).

### Web server, PHP, database and background-process logs

```
forge nginx:logs            # error log; `forge nginx:logs access` for the access log
forge php:logs              # `forge php:logs 8.4` for one version
forge database:logs
forge background-process:logs <id>
```

`nginx:logs`, `php:logs` and `database:logs` print the latest entries and exit; they have no follow flag. `background-process:logs` takes `--follow` (`-f`), as `site:logs` does.

### Pull, edit, push `.env`

```
forge env:pull <site> .env.production
# edit locally
forge env:push <site> .env.production
```

`env:push` OVERWRITES the remote `.env`. Always `env:pull` first, diff against the local copy, and confirm with the user before pushing. Never push an `.env` you didn't just pull; the remote may have drifted.

### Run an artisan command remotely

```
forge command <site> --command="php artisan migrate --force"
forge command <site> --command="php artisan cache:clear"
```

Runs as the site user, in the site root. Useful for migrations, cache clears, queue restarts. Use it for artisan only. The output and status it prints can belong to an older command, so read remote state over ssh (SKILL.md, rule 5).

### Tinker on prod

```
forge tinker <site>
```

Interactive. Suggest it only when the user explicitly asks, and never start it as part of an automated flow.

### SSH

```
forge ssh
forge ssh <server-name>
```

Interactive. `forge ssh <server-name>` also switches the active server to that one. Use `ssh:test` to verify key auth without opening a shell:

```
forge ssh:test
```

If it fails, `forge ssh:configure` walks the user through key setup (interactive; don't run it yourself).

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
