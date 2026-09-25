---
name: cloud-database
description: "Copy a Laravel Cloud database between environments (prod to staging, prod to local) with mysqldump, avoiding the two traps: the wrong schemas[] listing and orphan tables that break the next migrate. Triggers on 'copy the database down', 'kopieer de database van prod', 'sync prod data to staging', 'refresh staging from production'. Everything else on Cloud belongs to the laravel-cloud plugin."
---

# Cloud database copy

## Copying a Database Between Environments

Cloud MySQL clusters are publicly reachable and `database-cluster:list` returns their hostname, username and password in plain text. So a direct `mysqldump | mysql` pipe works from a local machine, and it is far faster than a GUI client like TablePlus, which executes statements one at a time.

```sh
cloud database-cluster:list --json -n
```

Read `connection.hostname`, `connection.username`, `connection.password` per cluster.

### Two traps that will bite you

**1. The `schemas[]` array in the cluster listing is wrong.** It repeats the same global schema list under *every* cluster, so a production cluster appears to contain a `staging` schema and vice versa. Never pick the target schema from it. Ask the server instead:

```sh
MYSQL_PWD='<pass>' mysql -h <host> -u <user> -N -e "SHOW DATABASES;"
```

Each cluster normally has exactly one real application schema.

**2. Nothing in the tooling stops you copying the wrong direction.** Before writing a single byte, positively identify both ends with a row-count fingerprint:

```sh
MYSQL_PWD='<pass>' mysql -h <host> -u <user> <schema> -N \
  -e "SELECT 'users',COUNT(*) FROM users UNION ALL SELECT 'events',COUNT(*) FROM events;"
```

Confirm the source matches known production magnitudes and the target is the one you expect. Raw `COUNT(*)` includes soft-deleted rows, so it will exceed any count you took through Eloquent. That gap is expected and is not evidence you are on the wrong database.

### Pre-flight

```sh
MYSQL_PWD='<pass>' mysql -h <host> -u <user> -N -e "
SELECT ROUND(SUM(data_length+index_length)/1024/1024/1024,2) FROM information_schema.tables WHERE table_schema='<schema>';
SELECT COUNT(*) FROM information_schema.triggers WHERE trigger_schema='<schema>';"
```

Check the source size fits the **target** cluster's `config.storage` (staging clusters are often much smaller than production). If triggers, routines or views exist, add `--routines --triggers` and expect `DEFINER` clauses to need stripping.

### The copy

Each end needs a different password, so give each side of the pipe its own subshell and its own `MYSQL_PWD`. Never put passwords in argv.

```sh
( MYSQL_PWD='<source-pass>' mysqldump \
    -h <source-host> -u <source-user> \
    --single-transaction --quick --no-tablespaces \
    --set-gtid-purged=OFF --column-statistics=0 \
    --default-character-set=utf8mb4 \
    <source-schema> ) \
| ( MYSQL_PWD='<target-pass>' mysql \
    -h <target-host> -u <target-user> \
    --default-character-set=utf8mb4 <target-schema> )
```

- Omitting `--databases` means no `CREATE DATABASE`/`USE` is emitted, so the dump loads into whatever target schema you name. This is what lets a `production` schema land in a `staging` schema.
- `--single-transaction` gives a consistent read without locking the source.
- `--no-tablespaces` avoids needing the `PROCESS` privilege, which managed users lack.
- `--set-gtid-purged=OFF` keeps GTID statements out of the stream.
- Default `--add-drop-table` replaces existing target tables, so a target that already ran migrations is fine.
- Run it backgrounded with `set -o pipefail` and watch progress by polling `SUM(data_length)` on the target.

### Afterwards: drop the orphan tables before migrating

This is the trap that actually breaks the next deploy, and it is not obvious.

`mysqldump` only drops and recreates the tables it *contains*. Any table that exists solely in the target, typically one created by a branch migration the source has not deployed yet, **survives the import untouched**. Meanwhile the `migrations` table *is* overwritten with the source's copy, which has no record of that migration.

The result is a contradiction: the table exists, but the ledger says it never ran. The next `migrate` tries to create it and dies with `SQLSTATE[42S01] ... Table 'x' already exists`.

The early warning is a table-count mismatch. If the target reports more tables than the source right after the import, stop and resolve it before deploying.

```sh
# list both, then diff
... -e "SELECT table_name FROM information_schema.tables
        WHERE table_schema='<schema>' AND table_type='BASE TABLE' ORDER BY table_name;"

comm -13 /tmp/source_tables.txt /tmp/target_tables.txt   # target-only = orphans
```

Then classify every orphan before touching it. Only drop the ones a migration owns:

```sh
grep -rln "<table_name>" database/migrations/
```

- **Migration-managed** → drop it, then re-run `migrate`. The migration recreates it cleanly, and its old rows referenced the dataset you just replaced, so they were dangling anyway.
- **No migration** (manual backup tables, ad-hoc scratch tables) → leave it and tell the user. You did not create it, nothing tries to recreate it, and it blocks nothing.

```sh
SET FOREIGN_KEY_CHECKS=0;
DROP TABLE IF EXISTS <orphan_a>, <orphan_b>;
SET FOREIGN_KEY_CHECKS=1;
```

Then `php artisan migrate --force` and confirm with `migrate:status --pending`.

### Afterwards: third-party identifiers now point at production

A production copy carries every external system's identifiers with it: Stripe customers, Connect accounts, checkout sessions, payment intents, and the equivalents for any other integration. The lower environment's credentials point at a sandbox account where none of those IDs exist, so the first code path that resolves one fails with something like `No such customer`.

Find them before they surface as a runtime error:

```sh
... -e "SELECT table_name,column_name FROM information_schema.columns
        WHERE table_schema='<schema>'
          AND (column_name LIKE '%stripe%' OR column_name LIKE '%_external_id')
        ORDER BY table_name;"
```

Then count which are actually populated, and decide per column rather than wholesale. For Cashier specifically, the useful distinction is:

- **Subscription *state* lives in the local `subscriptions` table.** `$billable->subscribed()` is a database query, so feature gating driven by subscription status keeps working with imported data and no Stripe access at all.
- **Only the remote *identifiers* are invalid.** Nulling the billable model's `stripe_id` puts the record into a state Cashier already models (a customer that was never set up), instead of one it cannot model (a customer belonging to another account).

So nulling `stripe_id` on the billable table, while leaving `subscriptions` untouched, keeps the environment realistic for testing and removes the errors. Leave display-only leftovers such as `pm_type` and `pm_last_four` alone; they render a card label and touch no API.

Never resolve this by pointing the lower environment at live credentials. That makes the error disappear by giving a full production data copy the ability to mutate real customers, which is the opposite of what a sandbox is for.

### Afterwards: everything else

- **Migration state is overwritten.** The target inherits the source's `migrations` table, so any migration the target's branch had already run becomes pending again and will re-run on its next deploy. Usually what you want; never a surprise.
- **Verify by comparing row counts per table, not by sampling.** Build the `UNION ALL` query with a `while read` loop rather than `GROUP_CONCAT`, which silently truncates at `group_concat_max_len` and yields an empty result that a `diff` will happily call identical. Guard the comparison with a table-count assertion so an empty result reports as failure instead of success. Note zsh does not word-split unquoted expansions, so iterate with `while IFS= read -r`.
- Expect small diffs on hot tables (log and telemetry tables the source writes to continuously). Confirm the drift is on the *source* by counting it twice, seconds apart, before treating it as a copy failure.
- Clusters with a non-zero `config.suspend_seconds` sleep when idle. The first connection wakes them, so an initial timeout is not necessarily a failure.
- Copying production into a lower environment brings real customer data with it. Confirm that environment's outbound is sealed (scheduler off, mail driver neutered, third-party keys pointed at sandboxes) *before* the data lands, not after.

