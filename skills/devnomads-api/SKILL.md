---
name: devnomads-api
description: "Operate DevNomads / infrapod.nl infrastructure via its HTTP API, using the bundled `dn` client. Use to inspect and manage servers, sites, databases, DNS zones, proxies, containers, and email. Trigger when the user mentions 'devnomads', 'infrapod', 'reboot the server', 'repoint the proxy', 'edit the DNS zone', or 'deploy the container'. This is the infra layer, not the app, use forge/artisan/SSH for app-level work."
allowed-tools: "Bash(dn:*), Bash(~/.claude/skills/devnomads-api/dn:*)"
---

# DevNomads API

DevNomads (infrapod.nl) is a managed-hosting provider. Its API at `https://api.devnomads.nl` covers servers, sites, databases, DNS, proxies, containers, and email. The `dn` client in this skill wraps it with curl and jq.

There is no official CLI. Everything is raw HTTP. `dn` exists so you don't hand-write `curl` with bearer headers every time.

## Setup check

Resolve a token (see precedence below), then verify with a read-only call:

```
~/.claude/skills/devnomads-api/dn clusters
```

If it returns `{"message":"Unauthenticated."}`, the token is missing or stale. Ask the user for a fresh one, don't guess. Add `~/.claude/skills/devnomads-api` to PATH (or symlink `dn`) to drop the long path.

### Tokens and profiles

One client can serve several accounts, each with its own key. Token resolution order:

1. `DEVNOMADS_API_TOKEN` env var
2. `DEVNOMADS_PROFILE=<name>` with `~/.config/devnomads/<name>.token`
3. `~/.config/devnomads/token` (default)

Profile files are mode 600 and never committed. Pick the profile that matches the account you mean to hit before any write.

## Common workflows

### Inventory

```
dn services        # everything
dn servers         # all server nodes, specs, power state
dn sites           # site services (php version, profile, docroot)
dn databases       # databases and which cluster they sit on
dn clusters        # db clusters
dn proxies         # which backends each domain routes to
dn zones           # DNS zones on the account
```

Drill into one with the singular + id: `dn server <id>`, `dn site <id>`, `dn proxy <id>`.

### Read a DNS zone

```
dn zone example.com.
```

The trailing dot matters, the API wants the FQDN form. The response is PowerDNS-style `rrsets`.

### Edit a DNS zone

Patching is a PATCH to the zone with an `rrsets` array. This is destructive per-rrset (it replaces the named record set). Always `dn zone <name>` first, build the minimal `rrsets` change, and confirm with the user before sending:

```
dn raw PATCH /services/dns/zones/example.com. '{"rrsets":[{"name":"example.com.","type":"A","ttl":300,"changetype":"REPLACE","records":[{"content":"<ip>","disabled":false}]}]}'
```

### Repoint a proxy / take it down

```
dn proxy <id>          # see current backends
dn proxy:down <id>     # cuts traffic, prompts y/N
dn proxy:up <id>
```

Backend changes go through `dn raw PUT /services/proxies/<id> '{...}'`. Pull the current proxy first so you keep the fields you're not changing.

### Deploy / inspect containers

```
dn containers
dn deploy <serviceId>              # prompts y/N
dn logs <serviceId> <instanceId>
```

### Server power state

```
dn server:state <serviceId> reboot   # also stop / start, prompts y/N
```

Only servers with `may_be_state_controlled: 1` accept this.

## Escape hatch

`dn` only wraps the common paths. For anything else, hit the endpoint directly:

```
dn get /services/databases/clusters/<id>/users
dn raw POST /services/databases '{"...":"..."}'
```

The full endpoint list is the OpenAPI spec:

```
curl 'https://api.devnomads.nl/docs?api-docs.json' | jq '.paths | keys'
```

## Safety rules

1. **Read before you write.** Every PATCH/PUT replaces fields. Pull the current resource, diff your change, then send.
2. **Confirm anything that moves traffic or power.** Proxy up/down, server reboot/stop, DNS apex changes, container deploys. The guarded commands prompt, the raw ones don't, so confirm yourself on `dn raw`.
3. **Know which account and which box you're hitting.** Keys map to accounts; service IDs map to specific boxes. A reboot on the wrong service ID is real downtime.
4. **The token is a secret.** It lives under `~/.config/devnomads/`, mode 600. Never echo it, never paste it into a commit or a log.
5. **This is infra, not the app.** Code deploys, migrations, queue restarts, and artisan are forge/SSH territory. Use this skill for the boxes underneath.

## Account-specific notes

Keep per-account detail (which servers, service IDs, proxies, and which key to use) in your own project notes, not in this skill, so it stays publishable.
