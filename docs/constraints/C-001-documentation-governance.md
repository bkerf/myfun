# C-001 Documentation Governance

## Status

Active

## Rules

- `AGENTS.md` is the single maintained AI collaboration entrypoint.
- `CLAUDE.md` is pointer-only and must not duplicate rules.
- Durable documentation must live under `docs/`.
- New durable documents must be indexed in `docs/README.md` and the nearest category index.
- Temporary notes, chat summaries, and one-off reports are not durable requirements.

## Categories

| Category | Use For |
|---|---|
| `docs/constraints/` | Durable rules, boundaries, validation policy |
| `docs/architecture/` | Architecture, APIs, data models, state machines |
| `docs/references/` | Workflows, commands, troubleshooting, task routing |
| `docs/decisions/` | Durable design decisions and tradeoffs |
| `docs/temporary/` | Short-lived drafts |
| `docs/archive/` | Replaced historical material |

## Prohibited

- Do not maintain duplicate rule sets in multiple entrypoint files.
- Do not hide long-lived requirements in temporary notes.
- Do not create unindexed durable docs.
