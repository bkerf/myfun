#!/usr/bin/env python3
"""Validate the AI project governance baseline."""

from __future__ import annotations

import argparse
import fnmatch
from pathlib import Path


REQUIRED_FILES = [
    "AGENTS.md",
    "docs/README.md",
    "docs/architecture/README.md",
    "docs/archive/README.md",
    "docs/constraints/README.md",
    "docs/decisions/README.md",
    "docs/references/README.md",
    "docs/temporary/README.md",
    "docs/constraints/C-001-documentation-governance.md",
    "docs/constraints/C-002-ai-operating-boundaries.md",
    "docs/constraints/C-003-interface-constraints.md",
    "docs/constraints/C-004-logic-and-contracts.md",
    "docs/constraints/C-005-file-size-and-modularization.md",
    "docs/constraints/C-006-debugging-log-first.md",
    "docs/constraints/C-007-verification-strategy.md",
    "docs/constraints/C-008-requirement-documentation-sync.md",
    "docs/references/80-ai-task-router.md",
    "scripts/ai_project_doctor.py",
    "scripts/check_file_size_boundaries.py",
    "scripts/pre_code_change_guard.py",
    "scripts/verify_changed.py",
]

EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "node_modules",
    ".next",
    "dist",
    "build",
    "coverage",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

SECRET_NAME_PATTERNS = [
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "credentials.json",
    "*credential*",
    "secrets.*",
    "*secret*",
]

SECRET_ALLOW_SUFFIXES = (
    ".example",
    ".sample",
    ".template",
    ".md",
    ".txt",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check AI governance baseline files.")
    parser.add_argument("--project-root", default=".", help="Repository root.")
    return parser.parse_args()


def should_skip(path: Path, root: Path) -> bool:
    rel_parts = path.relative_to(root).parts
    return any(part in EXCLUDED_DIRS for part in rel_parts)


def is_secret_like(path: Path) -> bool:
    name = path.name.lower()
    if name.endswith(SECRET_ALLOW_SUFFIXES):
        return False
    return any(fnmatch.fnmatch(name, pattern) for pattern in SECRET_NAME_PATTERNS)


def scan_secret_like_files(root: Path) -> list[str]:
    matches: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or should_skip(path, root):
            continue
        if is_secret_like(path):
            matches.append(path.relative_to(root).as_posix())
    return matches


def main() -> int:
    args = parse_args()
    root = Path(args.project_root).resolve()
    errors: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            errors.append(f"missing required file: {rel}")

    claude = root / "CLAUDE.md"
    if claude.exists():
        text = claude.read_text(encoding="utf-8", errors="ignore")
        if "AGENTS.md" not in text:
            errors.append("CLAUDE.md exists but does not point to AGENTS.md")
        if len(text.splitlines()) > 20:
            errors.append("CLAUDE.md should be pointer-only and under 20 lines")

    docs_index = root / "docs" / "README.md"
    if docs_index.exists():
        index_text = docs_index.read_text(encoding="utf-8", errors="ignore")
        for rel in REQUIRED_FILES:
            if rel.startswith("docs/constraints/") or rel.startswith("docs/references/"):
                name = Path(rel).name
                if name not in index_text:
                    errors.append(f"docs/README.md does not index {name}")

    for rel in scan_secret_like_files(root):
        errors.append(f"secret-like file found: {rel}")

    if errors:
        print("AI project doctor failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("AI project doctor passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
