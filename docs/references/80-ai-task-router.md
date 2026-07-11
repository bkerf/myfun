# AI Task Router

## Status

Active

## Purpose

Select the smallest relevant read set, edit scope, verification set, and documentation sync scope for each task.

## Default Read Set

Always start with:

1. `AGENTS.md`
2. `docs/README.md`
3. `docs/constraints/C-001-documentation-governance.md`
4. `docs/constraints/C-002-ai-operating-boundaries.md`
5. `docs/references/80-ai-task-router.md`

Then read task-specific files below.

## Task Types

### Interface or Frontend Change

Read:

- `docs/constraints/C-003-interface-constraints.md`
- Relevant architecture or feature docs

Verify:

- Lint
- Type-check
- Focused component/unit tests
- `pyenv exec python scripts/check_file_size_boundaries.py --project-root . --changed-only --strict`
- E2E only when explicitly requested or required by project policy

Docs:

- Update durable docs only if long-lived UI flow, form contract, visible state, or shared component ownership changes.

### Logic, API, Service, or Data Change

Read:

- `docs/constraints/C-004-logic-and-contracts.md`
- Relevant architecture or API docs

Verify:

- Unit, service, API, contract, or schema tests matching the changed layer
- `pyenv exec python scripts/check_file_size_boundaries.py --project-root . --changed-only --strict`

Docs:

- Update durable docs when API contract, state, permission, schema, provider, or domain workflow changes.

### Bug Fix or Debugging

Read:

- `docs/constraints/C-006-debugging-log-first.md`
- Interface or logic constraints depending on affected layer

Verify:

- Focused regression test or the smallest command that covers the failing path
- `pyenv exec python scripts/check_file_size_boundaries.py --project-root . --changed-only --strict`

Docs:

- Usually no durable doc update unless the fix changes long-lived behavior or contract.

### File Structure or Refactor

Read:

- `docs/constraints/C-005-file-size-and-modularization.md`

Verify:

- Static checks and focused tests for moved behavior

Docs:

- Update architecture docs only if module ownership or public boundaries change.

### Documentation-Only Change

Read:

- `docs/constraints/C-001-documentation-governance.md`
- `docs/constraints/C-008-requirement-documentation-sync.md`
- Related docs being changed

Verify:

- Search for stale references.
- Inspect diff.
- No code tests required unless docs claim implementation behavior that must be checked.

Docs:

- Update indexes for new durable docs.

### Deployment, Runtime, or Operations Change

Read:

- `docs/constraints/C-002-ai-operating-boundaries.md`
- Relevant architecture and operations references

Verify:

- Dry-run, preflight, config validation, or non-production smoke test first

Docs:

- Update operations, deployment, environment, and rollback docs when behavior changes.
