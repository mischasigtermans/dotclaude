---
name: devnomads
description: "Operate DevNomads / infrapod.nl infrastructure with the official `dncli` CLI: servers, sites, databases, DNS zones and records, proxies, containers, email, buckets and TLS certificates. Trigger when the user mentions 'devnomads', 'infrapod', 'dncli', 'reboot the server', 'repoint the proxy', 'edit the DNS zone', 'move the zone from TransIP', 'deploy the container' or 'issue a certificate'. This is the infra layer, not the app: use forge, artisan or SSH for app-level work."
allowed-tools: "Bash(dncli:*)"
---

# DevNomads

DevNomads (infrapod.nl) is a managed-hosting provider. `dncli` (PyPI: `devnomads-cli`) covers its whole API, one command group per product.

## Setup check

```sh
dncli version
dncli services list
```

Not installed: `uv tool install devnomads-cli`. No key: Mischa runs `dncli configure` himself (it prompts). The key lives in `~/.config/dncli/credentials`, mode 600. Never read it, echo it or pass it on the command line.

## Output

Piped output is JSON, a terminal gets a table. Pipe to `jq` for anything you parse; `-c entity,started_at` projects columns. Commands take a service id or a unique entity name (`dncli domains show example.com`); a numeric value is always an id.

## Common workflows

```sh
dncli services list                         # everything on the account
dncli servers list
dncli servers show <id>                     # same for sites, databases, proxies, containers, emails
```

**DNS.** `set` replaces the whole record set (PowerDNS REPLACE), `delete` removes it. List first, change the minimum, confirm with Mischa:

```sh
dncli dns records list example.com
dncli dns records set example.com www A 192.0.2.1 --ttl 3600
dncli dns records delete example.com www A
```

**Zone from another provider.** Reads the source, never writes there. The zone must already exist at DevNomads.

```sh
dncli dns transfer --from transip --zone example.com --dry-run
dncli dns transfer --from transip --zone example.com
```

**Proxies, power, containers.** All of these ask for confirmation; never pass `--yes` without Mischa's word.

```sh
dncli proxies down <id>      # cuts traffic
dncli proxies up <id>
dncli servers state <id> reboot
dncli containers deploy <id>
```

**Certificates.** DNS-01 through the DevNomads zone, written to `~/.config/dncli/certs/<domain>/`:

```sh
dncli certs issue example.com -d www.example.com --wildcard
```

Explore anything else with `dncli <group> --help`. `--debug` logs the HTTP exchange.

## Safety rules

1. **Read before you write.** `show` or `list` the resource, then change only what the ask covers.
2. **Confirm anything that moves traffic or power:** proxy up/down, server state, apex DNS, container deploys.
3. **Know which service you're hitting.** A reboot on the wrong service id is real downtime.
4. **This is infra, not the app.** Code deploys, migrations, queue restarts and artisan are Forge or SSH territory.

Per-account detail (which servers, service ids, proxies) lives in project notes, not in this skill, so it stays publishable.
