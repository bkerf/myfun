# C-003 Interface Constraints

## Status

Active

## Scope

Use this file for durable UI, UX, frontend, form, accessibility, copy, feedback, and user-facing behavior rules.

## Rules

- Preserve existing design system, component patterns, routing conventions, and styling approach.
- Prefer shared components for the same business form or workflow.
- Keep page components focused on layout, interaction state, and orchestration.
- Move payload building, formatting, permissions, and business state logic into testable helpers or adapters.
- Forms must show clear validation, loading, success, and failure states.
- Long-running operations must prevent duplicate submission and expose progress or pending state.
- Disabled, placeholder, error, and empty states must remain readable.
- UI text and controls must fit in their containers at supported viewport sizes.

## Verification

For interface changes, prefer the smallest adequate combination of:

- Lint.
- Type-check.
- Component or unit tests.
- Source-level contract tests for shared UI rules.
- Browser E2E only when explicitly requested or required by project policy.

## Documentation Sync

Update durable docs when changing a long-lived page flow, form contract, visible status meaning, accessibility rule, or shared component ownership rule.
