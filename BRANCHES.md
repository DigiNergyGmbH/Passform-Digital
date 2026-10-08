# Branch Model

This repository holds Odoo modules for Passform Digital and its clients. Each
client gets its own pair of branches; client branches are never merged into
each other.

## Branches

| Branch | Purpose |
| --- | --- |
| `main` | Scaffolding and documentation only (branch model, layout, tooling). No client modules. |
| `<client>/staging` | Acceptance / staging environment for one client. |
| `<client>/prod` | Production environment for one client. |
| `vendor/<name>` | Frozen snapshot of an external upstream repository. Never deployed on its own. |

A `core` branch is introduced only when a module is genuinely shared by more
than one client; the branch ruleset already covers the name, so it is protected
the moment it is created.

`<client>` is a lowercase slug without spaces or separators (client *Ezberger*
becomes `ezberger`, client *Passform Digital* becomes `passform`).

Environment segments are `staging` and `prod`. A third environment is added as
a further segment only when the client actually operates one.

### Why two levels

Git cannot hold a branch `ezberger` and a branch `ezberger/staging` at the same
time — one ref would have to be both a file and a directory. Client branches
therefore always carry an environment segment, and there is never a bare client
branch.

## Creating a client

Branch from `main` — never from another client's branch, which would inherit
that client's modules and history.

```bash
git fetch origin
git checkout -b <client>/staging origin/main
git push -u origin <client>/staging

git checkout -b <client>/prod origin/<client>/staging
git push -u origin <client>/prod
```

## Promotion

The only promotion path is `staging` -> `prod`, via pull request:

```bash
git checkout <client>/prod
git merge --ff-only <client>/staging   # or open a PR for review
git push origin <client>/prod
git tag <client>-prod-YYYY.MM.DD
git push origin <client>-prod-YYYY.MM.DD
```

Every production deployment gets a tag, so any release can be restored by
checking out its tag.

## Hotfixes

```bash
git checkout -b <client>/hotfix-<topic> origin/<client>/prod
# fix, commit, open a PR against <client>/prod
git checkout <client>/staging
git merge <client>/prod      # keep staging from drifting behind prod
```

Merging `prod` back into `staging` after a hotfix is the only case where
production code flows downwards.

## Shared modules

If a module ever has to serve more than one client, create a `core` branch from
`main`, put the module there, and merge it upwards into each affected client
branch:

```bash
git checkout <client>/staging
git merge core
```

Each client branch is free to stay behind `core` when it must not receive a
change yet. Until a module is genuinely shared, `core` does not exist.

## Module layout

Modules sit at the repository root, one directory per Odoo module:

```
<module_name>/
```

The branch name already identifies the client, so repeating the client in the
path is unnecessary. Point the instance's `addons_path` at the checkout
directory itself. A module directory is never renamed once the module is
installed — Odoo records the module name in the database, and renaming the
directory breaks that record.

## Deployment: one checkout per instance

An Odoo instance scans `addons_path` and builds its module list from the
directories it finds. If two directories on that path contain a module with the
same name, Odoo reports a duplicate and which copy wins is not predictable, so
edits can silently fail to apply.

Therefore exactly one checkout is ever placed on an instance's `addons_path`:
the client branch, which already contains the vendored upstream modules. The
`vendor/*` branch is a reference for diffing only and is never checked out on a
server, and never placed on `addons_path`. Because both branches reference the
same objects, this costs no additional disk space or bandwidth.

Deploy by checking out the branch on the server and updating it with a pull,
so the repository remains the single source of truth:

```bash
git -C /path/to/addons fetch origin
git -C /path/to/addons checkout <client>/<env>
git -C /path/to/addons pull --ff-only
```

## Vendored external addons

Modules written outside this repository are vendored into it, never left as a
loose clone, so an upstream repository disappearing or being rewritten cannot
lose work that is running in production.

- `vendor/<name>` — frozen, byte-identical snapshot of the upstream default
  branch. Never modified; it is the reference for what upstream looked like.
- The client branch carries the same tree plus a merge commit, so upstream
  history is preserved and every later change stays diffable:

```bash
git fetch akshara
git diff origin/vendor/<name> <client>/staging   # what we changed since import
git log --oneline origin/vendor/<name>..<client>/staging
```

Current imports:

| Branch | Upstream | Imported commit |
| --- | --- | --- |
| `vendor/erzberger-addons` | `AksharaBiju2025/erzberger_addons` | `0200a6c` |
| `ezberger/staging` | same upstream, merged with full history | `2c44de3` |

Upstream tracks compiled `.pyc` files and three `.docx` documents; they were
imported verbatim so the snapshot stays exact. Upstream module directories are
spelled `erzberger_*` while the branch slug is `ezberger`; the spelling is kept
as-is for the reason given above.

Refreshing an import when upstream has moved on:

```bash
git fetch akshara
git checkout <client>/staging
git merge akshara/main                                   # review, then commit
git push origin <client>/staging
git push origin akshara/main:refs/heads/vendor/<name>    # re-freeze the snapshot
```

## Tracking upstream changes

The snapshot branch is the single source of truth for "which upstream commit do
we have". Detecting that upstream moved is a comparison against it:

```bash
bash scripts/check-upstream.sh                       # akshara main vendor/erzberger-addons
```

| exit code | meaning |
| --- | --- |
| `0` | upstream unchanged — snapshot equals upstream default branch |
| `1` | upstream moved — new commits and changed files are listed |
| `2` | could not check (not a repo, remote missing, fetch failed) |

`BASE=<ref>` compares against an arbitrary ref instead of the snapshot, which is
useful for reviewing a proposed update before accepting it.

Two ways to run it:

- **On a server**, from cron, so a stale clone is noticed without anyone
  remembering to look:

  ```cron
  0 6 * * * cd /path/to/addons && bash scripts/check-upstream.sh >> /var/log/odoo/upstream-check.log 2>&1
  ```

  Exit code `1` can be wired into whatever alerting already exists.

- **In CI**, `.github/workflows/watch-upstream.yml` runs daily and opens an
  issue titled *Upstream erzberger_addons has new commits* containing the new
  commits and changed files. It needs no secrets.

Adding another upstream means adding its remote and repeating the pattern with
its own `vendor/<name>` branch; the script takes the remote, branch and vendor
branch as arguments, so one script covers every import.

## Protected branches

The branch rulesets `refs/heads/*/prod` and `refs/heads/*/staging` block force
pushes and deletions and require a pull request before merging. `main`,
`core` and `vendor/*` are protected the same way. Repository administrators are
listed as bypass actors, so an emergency push stays possible without weakening
the rule for everyone else.

## Local development

Multiple client branches can be checked out side by side from a single clone:

```bash
git worktree add ../passform-<client>-staging <client>/staging
git worktree add ../passform-<client>-prod    <client>/prod
```

Point the Odoo instance's `addons_path` at the worktree that is being tested.

## Continuous deployment

A single workflow derives the client and environment from the branch name:

```yaml
on:
  push:
    branches: ['*/staging', '*/prod']
```

The two-level branch name is then split into its client and environment
segments, which select the target host and database from a per-client
configuration map.
