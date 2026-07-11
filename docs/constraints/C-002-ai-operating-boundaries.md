# C-002 AI Operating Boundaries

## Status

Active

## Directly Allowed

- Read project source files and durable documentation relevant to the task.
- Modify files directly related to the user request.
- Add or update tests that match the behavior change.
- Update durable docs when long-lived behavior changes.

## Requires Explicit User Approval

- Production deployment or production configuration changes.
- Production data modification or migration.
- Destructive file operations.
- Force push or history rewrite.
- Credential rotation, key generation, or secret material handling.

## Prohibited

- Do not read or output `.env`, `.env.*`, private keys, certificates, credential files, or secret files.
- Do not log or expose production secrets, tokens, private customer data, or payment-sensitive data.
- Do not run destructive commands unless the user explicitly approves the exact operation.
- Do not automatically commit or push.
- Do not create compatibility layers unless the user explicitly asks for backward compatibility.

## Baseline Check

Run the generated doctor after initialization and after documentation boundary changes:

```bash
pyenv exec python scripts/ai_project_doctor.py --project-root .
```

The doctor scans for required governance files, pointer-only `CLAUDE.md`, indexed constraint docs, and root or nested secret-like files outside dependency/build/cache directories.

## Local Test Data

Local development and QA data may be inspected when needed for debugging or verification, unless project-specific docs classify it as sensitive. Production data remains restricted.
