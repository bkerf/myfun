# Managed Documentation Index

## Purpose

This directory is the durable documentation system for myfun.

## Authority Order

1. `AGENTS.md`
2. `CLAUDE.md`
3. `docs/README.md`
4. `docs/constraints/C-001-documentation-governance.md`
5. Category indexes and topic documents under `docs/`

## Categories

| Directory | Purpose |
|---|---|
| `docs/constraints/` | Durable rules, safety boundaries, validation policy, and AI operating constraints |
| `docs/architecture/` | System structure, API contracts, data models, runtime architecture |
| `docs/references/` | Workflows, commands, troubleshooting guides, task routing |
| `docs/decisions/` | Durable design decisions and tradeoffs |
| `docs/temporary/` | Short-lived drafts and intermediate notes |
| `docs/archive/` | Replaced historical material kept for traceability |

## Default Read Set

Read `AGENTS.md`, this index, the base constraints, and `docs/references/80-ai-task-router.md`. Then read only the task-relevant documents selected by the router.

## Document Index

| Document | Purpose | Default |
|---|---|---|
| `constraints/C-001-documentation-governance.md` | Documentation authority, categories, and indexing rules | Base |
| `constraints/C-002-ai-operating-boundaries.md` | AI safety, secrets, production, approvals, destructive actions | Base |
| `constraints/C-003-interface-constraints.md` | UI, UX, forms, accessibility, frontend behavior | Task |
| `constraints/C-004-logic-and-contracts.md` | API contracts, domain logic, state, permissions, data integrity | Task |
| `constraints/C-005-file-size-and-modularization.md` | File size, module boundaries, code organization | Base before code edits |
| `constraints/C-006-debugging-log-first.md` | Debugging workflow and evidence requirements | Task |
| `constraints/C-007-verification-strategy.md` | Minimal validation and E2E escalation rules | Base before verification |
| `constraints/C-008-requirement-documentation-sync.md` | When durable docs must be updated | Task |
| `references/80-ai-task-router.md` | Task routing to read sets and validation sets | Base |
| `references/git-helper-commands.md` | Git helper command behavior, performance rules, and troubleshooting notes | Task |

## Category Indexes

| Document | Purpose |
|---|---|
| `architecture/README.md` | Architecture document index |
| `constraints/README.md` | Constraint document index |
| `references/README.md` | Reference document index |
| `decisions/README.md` | Decision record index |
| `temporary/README.md` | Temporary material index |
| `archive/README.md` | Archived material index |

## Rules

- New durable documents must be added to this index.
- New category documents should also be indexed in their category README when present.
- Do not store secrets or production credentials in documentation.
- Do not use temporary notes as long-lived requirements.
