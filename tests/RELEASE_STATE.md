# Release-decision foundation

`scripts/distribution/release-state.py` is an unwired Python standard-library module, not a workflow
or command-line entry point. It has no Git, filesystem, or network side effects.
Run its synthetic tests with `python3 -m unittest discover -s tests`.

Preparation validates normalized decimal version/build scalars for changed
projects. New projects retain valid initial values. Equal values request a bump
only for writable consumers; manual versions must increase both version and
build. Unchanged projects are skipped. Read-only contributors author their own
bumps. An adapter must distinguish a genuinely new project from missing or
invalid metadata and compare against the current base, not the historical fork.

Baseline selection accepts one release namespace and caller-supplied reachable,
peeled commit identities. It selects the highest reachable version, including a
tag at the selected merge for retry handling. Ambiguous highest-version aliases
fail closed. The caller must obtain reachability from Git, not contributor input.

`scripts/distribution/release-git.py` now provides read-only local Git integration: full commit IDs,
bounded literal metadata parsing from blobs, regular-file checks, historical
change attribution, current-base comparison, and peeled-tag ancestry checks.
Load the decision/Git modules and shared `release_yaml.py` from the same trusted
revision, never from PR-supplied code. Install the pinned
`scripts/distribution/requirements-release.txt` in a virtual environment first.
The parser uses SafeLoader node composition, rejects duplicate keys and aliases,
and reads only supported XcodeGen settings paths. It does not resolve includes,
templates, setting groups or xcconfig inheritance. Callers supply change scopes.
Synthetic local repositories test the adapter without network access.

`release-check.py` now exposes `inspect` and `remote-head` commands for workflows.
The latter checks an exact branch/pull ref against an immutable expected commit;
missing refs and Git failures fail closed. `workflows/release-prep.yml` is an
opt-in single-project example: configure PROJECT_DIR and SCRIPTS_ROOT in the
trusted base definition. It loads helpers from the base checkout (including the
base-pinned submodule), validates fork PRs without mutation, and permits ordinary
fast-forward preparation pushes only for same-repository PRs. Install the template
only after the base-pinned helper revision contains these files; never use head
copies as a fallback. A contributor must provide both higher values on a fork.

Local bare-remote tests execute the actual template preparation shell, covering
bumps, retries, fork validation, missing heads, malformed versions and concurrent
push rejection. Head checks are not a transaction across Git and GitHub: branch
deletion/recreation or administrative rewrites can still race. Status is bound to
the exact SHA, and strict up-to-date branch checks remain required.

API adapters, immutable-tag reconciliation and hosted freshness verification remain follow-up work.
This module does not enforce branch protection, certify compilation, or alter
the existing tagging workflow and its legacy moving-tag behavior. A disposable
hosted trial must verify bot-push CI, fork statuses and required-check enforcement
before making this template a required merge gate. No hosted trial is claimed.
