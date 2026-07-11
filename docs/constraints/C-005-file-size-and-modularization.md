# C-005 File Size and Modularization

## Status

Active

## Purpose

Prevent AI-assisted changes from growing large files, mixing responsibilities, or hiding business logic in UI and E2E code.

## Default Targets

| File Type | Target Limit |
|---|---:|
| Leaf UI component | 250 lines |
| Page or workspace component | 500 lines |
| Frontend route or API handler | 250 lines |
| Frontend helper, adapter, payload builder | 300 lines |
| Backend route file | 500 lines |
| Backend service | 600 lines |
| Repository or data-access file | 800 lines |
| Provider client | 600 lines |
| Script | 500 lines |
| Test file | 700 lines |
| E2E runner entry | 300 lines |
| E2E case file | 700 lines |

## Rules

- Before code edits, inspect target file size and responsibility.
- Do not add new business responsibility to files already above their target limit.
- For files above 800 lines, decide whether the change should first move into a smaller module.
- For files above 1200 lines, only allow local bug fixes, deletion, mechanical extraction, or minimal export wiring.
- New features must have a clear module owner.
- Core business logic must not exist only in UI components or E2E scripts.

## Suggested Pre-Change Check

Before code edits, run the deterministic pre-change guard with the planned files:

```bash
pyenv exec python scripts/pre_code_change_guard.py --project-root . --task "<task>" --paths <planned files>
```

If exact files are not known yet, run:

```bash
pyenv exec python scripts/pre_code_change_guard.py --project-root . --task "<task>" --include-changed
```

After code edits, run the changed-file size gate:

```bash
pyenv exec python scripts/check_file_size_boundaries.py --project-root . --changed-only --strict
```

Project-specific size targets may be added later, but do not remove this baseline gate without replacing it with a stricter project-specific checker.

## Completion Note

After code changes, state whether files above 800 lines were touched and whether any new business responsibility was added to an oversized file.
