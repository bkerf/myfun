# C-008 Requirement Documentation Sync

## Status

Active

## Purpose

Keep implementation and durable project knowledge aligned.

## Must Update Durable Docs When Changing

- Long-lived product behavior.
- Architecture or runtime topology.
- API contract.
- Data model, schema, or field meaning.
- Permission, role, or authorization behavior.
- State machine or async job contract.
- Deployment, environment, or operational workflow.
- Security boundary.
- Shared UI workflow or form ownership rule.

## Usually No Durable Doc Update Needed

- Local bug fix with unchanged contract.
- Formatting-only change.
- Internal refactor with unchanged behavior.
- Test-only change that does not alter project policy.

## Rules

- Do not leave long-lived requirements only in chat, commit text, temporary notes, or test reports.
- New durable docs must be indexed.
- If no durable documentation impact exists, final response must say so and why.

## Completion Note

List updated docs and the synchronized behavior. If none, state "no durable documentation impact" with the reason.
