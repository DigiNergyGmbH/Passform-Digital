# Branch Model

This repository holds Odoo modules for Passform Digital and its clients. Each
client gets its own pair of branches; client branches are never merged into
each other.

## Branches

| Branch | Purpose |
| --- | --- |
| `main` | Scaffolding and documentation only (branch model, layout, tooling). No client modules. |
| `core` | Modules shared by more than one client, kept client-agnostic. |
| `<client>/staging` | Acceptance / staging environment for one client. |
| `<client>/prod` | Production environment for one client. |

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

Branch from `core` (or `main` when `core` is empty) — never from another
client's branch, which would inherit that client's modules and history.

```bash
git fetch origin
git checkout -b <client>/staging origin/core
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

Changes meant for several clients land on `core` first, then are merged
upwards into each affected client branch:

```bash
git checkout <client>/staging
git merge core
```

Each client branch is free to stay behind `core` when it must not receive a
change yet.

## Module layout

```
custom_module/diginergy/<client_slug>/<module_name>/
custom_module/diginergy/core/<module_name>/        # shared modules
```

Keeping client modules in a per-client directory means a branch mostly selects
which modules are present and at which version.

## Protected branches

The branch rulesets `refs/heads/*/prod` and `refs/heads/*/staging` block force
pushes and deletions and require a pull request before merging. `main` and
`core` are protected the same way.

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
