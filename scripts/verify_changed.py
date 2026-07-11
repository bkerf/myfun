#!/usr/bin/env python3
"""Run minimal verification for changed files."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    ".next",
    "dist",
    "build",
    "coverage",
    "__pycache__",
}

PY_SYNTAX_CHECK = (
    "import pathlib, sys; "
    "[compile(pathlib.Path(path).read_text(encoding='utf-8'), path, 'exec') "
    "for path in sys.argv[1:]]"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run minimal verification for changed files.")
    parser.add_argument("--project-root", default=".", help="Repository root.")
    parser.add_argument("--list", action="store_true", help="Only print selected commands.")
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


def is_excluded(path: str) -> bool:
    parts = Path(path).parts
    return any(part in EXCLUDED_DIRS for part in parts)


def load_package_scripts(root: Path) -> dict[str, str]:
    package_json = root / "package.json"
    if not package_json.exists():
        return {}
    try:
        data = json.loads(package_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    scripts = data.get("scripts")
    return scripts if isinstance(scripts, dict) else {}


def package_manager(root: Path) -> str:
    if (root / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (root / "yarn.lock").exists():
        return "yarn"
    return "npm"


def run_script_command(manager: str, script: str) -> list[str]:
    if manager == "yarn":
        return ["yarn", script]
    return [manager, "run", script]


def select_commands(root: Path, files: list[str]) -> tuple[list[list[str]], list[str]]:
    commands: list[list[str]] = []
    notes: list[str] = []
    active_files = [path for path in files if not is_excluded(path)]

    scripts = load_package_scripts(root)
    manager = package_manager(root)
    js_changed = any(path.endswith((".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs")) for path in active_files)
    if js_changed:
        for script in ("lint", "type-check", "typecheck", "test"):
            if script in scripts:
                command = run_script_command(manager, script)
                if shutil.which(command[0]):
                    commands.append(command)
                else:
                    notes.append(f"skip {script}: command not found: {command[0]}")
        if not any(command[0] in {"npm", "pnpm", "yarn"} for command in commands):
            notes.append("no runnable JavaScript verification script found in package.json")

    py_files = [
        path for path in active_files
        if path.endswith(".py") and (root / path).exists()
    ]
    if py_files:
        commands.append([sys.executable, "-B", "-c", PY_SYNTAX_CHECK, *py_files])

    docs_changed = any(
        path.startswith("docs/") or path in {"AGENTS.md", "CLAUDE.md"}
        for path in active_files
    )
    if docs_changed or not commands:
        commands.append([sys.executable, "scripts/ai_project_doctor.py", "--project-root", "."])

    commands.append([sys.executable, "scripts/check_file_size_boundaries.py", "--project-root", ".", "--changed-only", "--strict"])
    return commands, notes


def main() -> int:
    args = parse_args()
    root = Path(args.project_root).resolve()
    files = git_changed(root)
    commands, notes = select_commands(root, files)

    print("Changed files:")
    for path in files:
        print(f"  - {path}")
    print("Selected verification:")
    for command in commands:
        print("  " + " ".join(command))
    if notes:
        print("Notes:")
        for note in notes:
            print(f"  - {note}")

    if args.list:
        return 0

    for command in commands:
        result = subprocess.run(command, cwd=root, check=False)
        if result.returncode != 0:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
