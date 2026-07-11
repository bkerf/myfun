# C-006 Debugging Log First

## Status

Active

## Scope

Use this file when diagnosing bugs, logs, crashes, flaky behavior, integration failures, production-like incidents, or unexpected user-visible behavior.

## Workflow

1. Reproduce or identify the failing path.
2. Read relevant logs, error messages, stack traces, network responses, or database/API evidence.
3. Locate the root cause before editing.
4. Patch the smallest responsible layer.
5. Add or update the smallest adequate regression test.
6. Verify the failing path no longer fails.

## Rules

- Do not fix symptoms without identifying the responsible layer.
- Do not hide exceptions with broad catches or default fallback values.
- Do not leave debug prints, console logs, temporary probes, or ad hoc tracing in final code.
- If logs are insufficient, add durable structured logging only where it improves future diagnosis.
- For production-like issues, do not expose secrets or sensitive data while collecting evidence.

## Final Note

Summarize the root cause, patch location, and verification evidence.
