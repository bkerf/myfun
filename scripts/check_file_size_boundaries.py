#!/usr/bin/env python3
"""Check changed source files against baseline size boundaries."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    ".next",
    "dist",
    "build",
    "coverage",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

GENERATED_NAMES = {
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
}

TARGETS = {
    "leaf_ui_component": 250,
    "page_or_workspace_component": 500,
    "frontend_route_or_api_handler": 250,
    "frontend_helper_adapter_payload": 300,
    "backend_route_file": 500,
    "backend_service": 600,
    "repository_or_data_access": 800,
    "provider_client": 600,
    "script": 500,
    "test_file": 700,
    "e2e_runner_entry": 300,
    "e2e_case_file": 700,
    "generic_source": 500,
}

SOURCE_SUFFIXES = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".swift",
    ".cs",
    ".php",
    ".rb",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check source file size boundaries.")
    parser.add_argument("--project-root", default=".", help="Repository root.")
    parser.add_argument("--paths", nargs="*", help="Specific paths to check.")
    parser.add_argument("--changed-only", action="store_true", help="Check git changed files.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero on boundary violations.")
    return parser.parse_args()


def git_changed(root: Path) -> list[str]:
    if not shutil.which("git"):
        return []
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    files: list[str] = []
    for line in result.stdout.splitlines():
        value = line[3:].strip()
        if " -> " in value:
            value = value.split(" -> ", 1)[1].strip()
        if value:
            files.append(value.replace("\\", "/"))
    return sorted(set(files))


def is_excluded(path: Path, root: Path) -> bool:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return True
    if path.name in GENERATED_NAMES:
        return True
    return any(part in EXCLUDED_DIRS for part in rel.parts)


def is_source(path: Path) -> bool:
    return path.suffix.lower() in SOURCE_SUFFIXES


def classify(path: Path) -> str:
    parts = {part.lower() for part in path.parts}
    name = path.name.lower()
    stem = path.stem.lower()

    if "e2e" in parts or "e2e" in name:
        if "runner" in name or name.startswith("run_") or stem in {"run", "runner"}:
            return "e2e_runner_entry"
        return "e2e_case_file"
    if "test" in parts or "tests" in parts or ".test." in name or ".spec." in name:
        return "test_file"
    if "scripts" in parts or "tools" in parts:
        return "script"
    if "repository" in name or "repositories" in parts or "data" in parts:
        return "repository_or_data_access"
    if "provider" in name or "client" in name or "integrations" in parts:
        return "provider_client"
    if "service" in name or "services" in parts:
        return "backend_service"
    if name in {"route.ts", "route.js", "routes.py"} or "routes" in parts:
        return "backend_route_file"
    if "api" in parts and path.suffix.lower() in {".ts", ".tsx", ".js", ".jsx"}:
        return "frontend_route_or_api_handler"
    if {"helpers", "lib", "adapters", "payloads", "utils", "hooks"} & parts:
        return "frontend_helper_adapter_payload"
    if path.suffix.lower() in {".tsx", ".jsx"}:
        if "pages" in parts or "app" in parts or "workspace" in name or "page" in name:
            return "page_or_workspace_component"
        return "leaf_ui_component"
    return "generic_source"


def count_lines(path: Path) -> int:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            return sum(1 for _ in handle)
    except OSError:
        return 0


def resolve_paths(root: Path, args: argparse.Namespace) -> list[Path]:
    raw_paths: list[str] = []
    if args.paths:
        raw_paths.extend(args.paths)
    if args.changed_only:
        raw_paths.extend(git_changed(root))
    if not raw_paths and not args.changed_only:
        raw_paths = [str(path.relative_to(root)) for path in root.rglob("*") if path.is_file()]

    paths: list[Path] = []
    for raw in sorted(set(raw_paths)):
        path = (root / raw).resolve()
        if path.exists() and path.is_file() and not is_excluded(path, root) and is_source(path):
            paths.append(path)
    return paths


def main() -> int:
    args = parse_args()
    root = Path(args.project_root).resolve()
    paths = resolve_paths(root, args)
    violations: list[str] = []

    if not paths:
        print("No source files selected for size boundary check.")
        return 0

    print("File size boundary check:")
    for path in paths:
        kind = classify(path)
        limit = TARGETS[kind]
        lines = count_lines(path)
        rel = path.relative_to(root).as_posix()
        status = "OK" if lines <= limit else "FAIL"
        print(f"  {status} {rel}: {lines}/{limit} lines ({kind})")
        if lines > limit:
            violations.append(f"{rel}: {lines}/{limit} lines ({kind})")

    if violations and args.strict:
        print("File size boundary violations:")
        for violation in violations:
            print(f"  - {violation}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
