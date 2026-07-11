# C-007 Verification Strategy

## Status

Active

## Purpose

Choose the smallest validation that can catch the risk introduced by the change.

## Default Order

1. Static checks for changed language or framework.
2. Unit tests for pure logic.
3. Component tests for UI behavior.
4. API or service tests for contract behavior.
5. Integration tests for cross-boundary behavior.
6. Browser E2E only when explicitly requested or required by project policy.

## Rules

- Do not run broad verification when a focused command covers the risk.
- Do not skip verification for behavior changes unless blocked; report the blocker.
- Do not use E2E as a substitute for unit, service, or contract tests.
- Do not use mocks for core business flows when the task explicitly requires real integration validation.
- Generated `scripts/verify_changed.py` detects common project scripts before running them. Adapt it to the project stack once stable commands are known.

## Default Command

```bash
pyenv exec python scripts/verify_changed.py --project-root .
```

## Completion Note

State the exact commands run and whether they passed. If verification was not run, state why.
