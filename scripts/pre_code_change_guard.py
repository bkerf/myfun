#!/usr/bin/env python3
"""Assess file growth risk before code edits."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

import check_file_size_boundaries as size_check


FEATURE_KEYWORDS = {
    "add",
    "create",
    "implement",
    "support",
    "feature",
    "new",
    "新增",
    "创建",
    "实现",
    "支持",
    "功能",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pre-change file growth guard.")
    parser.add_argument("--project-root", default=".", help="Repository root.")
    parser.add_argument("--task", required=True, help="Planned task summary.")
    parser.add_argument("--paths", nargs="*", help="Planned files to edit.")
    parser.add_argument("--include-changed", action="store_true", help="Use git changed files.")
    return parser.parse_args()


def changed_files(root: Path) -> list[str]:
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


def is_feature_task(task: str) -> bool:
    lowered = task.lower()
    return any(keyword in lowered for keyword in FEATURE_KEYWORDS)


def resolve_paths(root: Path, args: argparse.Namespace) -> list[Path]:
    raw_paths: list[str] = []
    if args.paths:
        raw_paths.extend(args.paths)
    if args.include_changed:
        raw_paths.extend(changed_files(root))

    paths: list[Path] = []
    for raw in sorted(set(raw_paths)):
        path = (root / raw).resolve()
        if (
            path.exists()
            and path.is_file()
            and not size_check.is_excluded(path, root)
            and size_check.is_source(path)
        ):
            paths.append(path)
    return paths


def main() -> int:
    args = parse_args()
    root = Path(args.project_root).resolve()
    paths = resolve_paths(root, args)
    feature_task = is_feature_task(args.task)
    required: list[str] = []
    recommended: list[str] = []

    print(f"Pre-change guard task: {args.task}")
    if not paths:
        print("No existing source files selected. Continue after discovery, then rerun with exact paths.")
        return 0

    for path in paths:
        kind = size_check.classify(path)
        limit = size_check.TARGETS[kind]
        lines = size_check.count_lines(path)
        rel = path.relative_to(root).as_posix()
        print(f"  {rel}: {lines}/{limit} lines ({kind})")
        if lines > 1200:
            required.append(f"{rel}: above 1200 lines")
        elif lines > limit and feature_task:
            required.append(f"{rel}: above target and task appears to add capability")
        elif lines > 800 or lines > limit:
            recommended.append(f"{rel}: above preferred boundary")

    if required:
        print("Decision: split_required")
        for item in required:
            print(f"  - {item}")
        return 2
    if recommended:
        print("Decision: split_recommended")
        for item in recommended:
            print(f"  - {item}")
        return 0

    print("Decision: local_edit_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
