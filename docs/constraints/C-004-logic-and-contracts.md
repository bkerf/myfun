# C-004 Logic and Contracts

## Status

Active

## Scope

Use this file for durable backend, API, domain logic, state machine, permission, authorization, data model, job, provider, and integration rules.

## Rules

- Business rules must live in services, domain modules, repositories, adapters, or helpers that can be tested without UI automation.
- API contracts must define request shape, response shape, error behavior, authorization behavior, and pagination or filtering semantics when relevant.
- State machines must define allowed transitions, terminal states, retry behavior, and failure behavior.
- Permission checks must be enforced server-side. UI guards are convenience, not authority.
- Provider or third-party mappings must be centralized and tested.
- Do not hide errors with default values that mask invalid state.
- Do not add backward compatibility paths unless explicitly required.

## Verification

For logic changes, prefer:

- Unit tests for pure helpers.
- Service tests for business rules.
- API or contract tests for route behavior.
- Migration or schema validation for data model changes.
- E2E only when explicitly requested or required by project policy.

## Documentation Sync

Update durable architecture or constraint docs when API contracts, states, permissions, schema, provider behavior, job contracts, or domain workflows change.
