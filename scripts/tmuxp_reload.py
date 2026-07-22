#!/usr/bin/env python3
"""Safely rebuild the current tmux server from tmuxp workspaces."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


NO_SERVER_MARKERS = (
    "no server running",
)


class ReloadError(RuntimeError):
    """An error that can be shown directly to the command user."""


@dataclass(frozen=True)
class TmuxTarget:
    socket_name: str | None = None
    socket_path: str | None = None

    def tmux_options(self) -> list[str]:
        if self.socket_name:
            return ["-L", self.socket_name]
        if self.socket_path:
            return ["-S", self.socket_path]
        return []


@dataclass(frozen=True)
class TmuxpWorkspace:
    name: str
    path: str
    session_name: str


@dataclass(frozen=True)
class ReloadPlan:
    observed_sessions: tuple[str, ...]
    session_names: tuple[str, ...]
    workspaces: tuple[TmuxpWorkspace, ...]
    close_all: bool
    unmanaged_sessions: tuple[str, ...]


def parse_tmux_socket_path(tmux_value: str | None) -> str | None:
    if not tmux_value:
        return None
    parts = tmux_value.rsplit(",", 2)
    if len(parts) != 3 or not parts[0]:
        return None
    return parts[0]


def resolve_target(socket_name: str | None, socket_path: str | None, tmux_value: str | None) -> TmuxTarget:
    if socket_name and socket_path:
        raise ReloadError("-L and -S cannot be used together")
    if socket_name:
        return TmuxTarget(socket_name=socket_name)
    if socket_path:
        return TmuxTarget(socket_path=os.path.expanduser(socket_path))

    current_socket = parse_tmux_socket_path(tmux_value)
    if current_socket:
        return TmuxTarget(socket_path=current_socket)
    return TmuxTarget()


def target_is_current_server(target: TmuxTarget, tmux_value: str | None) -> bool:
    current_socket = parse_tmux_socket_path(tmux_value)
    if not current_socket:
        return False
    if target.socket_path:
        return os.path.abspath(target.socket_path) == os.path.abspath(current_socket)
    if target.socket_name:
        return Path(current_socket).name == target.socket_name
    return True


def build_tmux_command(target: TmuxTarget, *args: str) -> list[str]:
    return ["tmux", *target.tmux_options(), *args]


def build_tmuxp_load_command(target: TmuxTarget, workspaces: Sequence[TmuxpWorkspace]) -> list[str]:
    return [
        "tmuxp",
        "load",
        "--yes",
        "-d",
        *target.tmux_options(),
        *(workspace.path for workspace in workspaces),
    ]


def is_no_server_error(message: str) -> bool:
    lowered = message.lower()
    if any(marker in lowered for marker in NO_SERVER_MARKERS):
        return True
    return "error connecting to" in lowered and (
        "no such file or directory" in lowered or "connection refused" in lowered
    )


def ensure_commands() -> None:
    missing = [command for command in ("tmux", "tmuxp") if not shutil.which(command)]
    if missing:
        raise ReloadError(f"command not found: {', '.join(missing)}")


def list_tmux_sessions(target: TmuxTarget) -> list[str]:
    result = subprocess.run(
        build_tmux_command(target, "list-sessions", "-F", "#{session_name}"),
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        return [line for line in result.stdout.splitlines() if line]
    if is_no_server_error(result.stderr):
        return []
    raise ReloadError(result.stderr.strip() or "tmux list-sessions failed")


def parse_tmuxp_workspaces(output: str) -> list[TmuxpWorkspace]:
    try:
        payload = json.loads(output)
    except json.JSONDecodeError as exc:
        raise ReloadError(f"tmuxp ls returned invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ReloadError("tmuxp ls JSON root must be an object")

    raw_workspaces = payload.get("workspaces")
    if not isinstance(raw_workspaces, list):
        raise ReloadError("tmuxp ls JSON does not contain a workspace list")

    workspaces: list[TmuxpWorkspace] = []
    for item in raw_workspaces:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        path = item.get("path")
        session_name = item.get("session_name")
        if not all(isinstance(value, str) and value for value in (name, path, session_name)):
            continue
        workspaces.append(TmuxpWorkspace(name, os.path.expanduser(path), session_name))
    return workspaces


def list_tmuxp_workspaces() -> list[TmuxpWorkspace]:
    result = subprocess.run(
        ["tmuxp", "ls", "--json"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise ReloadError(result.stderr.strip() or "tmuxp ls --json failed")
    return parse_tmuxp_workspaces(result.stdout)


def build_reload_plan(session_names: Sequence[str], workspaces: Sequence[TmuxpWorkspace]) -> ReloadPlan:
    unique_sessions = tuple(dict.fromkeys(session_names))
    by_session: dict[str, list[TmuxpWorkspace]] = {}
    for workspace in workspaces:
        by_session.setdefault(workspace.session_name, []).append(workspace)

    selected: list[TmuxpWorkspace] = []
    unmanaged: list[str] = []
    for session_name in unique_sessions:
        matches = by_session.get(session_name, [])
        if not matches:
            unmanaged.append(session_name)
            continue
        if len(matches) > 1:
            paths = ", ".join(workspace.path for workspace in matches)
            raise ReloadError(f"multiple tmuxp workspaces define session '{session_name}': {paths}")
        selected.append(matches[0])

    return ReloadPlan(unique_sessions, unique_sessions, tuple(selected), True, tuple(unmanaged))


def build_targeted_reload_plan(
    selectors: Sequence[str],
    running_sessions: Sequence[str],
    workspaces: Sequence[TmuxpWorkspace],
) -> ReloadPlan:
    observed_sessions = tuple(dict.fromkeys(running_sessions))
    running = set(observed_sessions)
    selected: list[TmuxpWorkspace] = []
    selected_sessions: set[str] = set()

    for selector in dict.fromkeys(selectors):
        matches = [
            workspace
            for workspace in workspaces
            if selector in {workspace.name, workspace.session_name}
        ]
        if not matches:
            raise ReloadError(f"tmuxp workspace not found: {selector}")
        if len(matches) > 1:
            paths = ", ".join(workspace.path for workspace in matches)
            raise ReloadError(f"multiple tmuxp workspaces match '{selector}': {paths}")

        workspace = matches[0]
        if workspace.session_name not in running:
            raise ReloadError(
                f"tmux session is not running: {workspace.session_name}; "
                f"use 'tmuxp load {workspace.name}' to start it"
            )
        if workspace.session_name not in selected_sessions:
            selected.append(workspace)
            selected_sessions.add(workspace.session_name)

    return ReloadPlan(
        observed_sessions,
        tuple(workspace.session_name for workspace in selected),
        tuple(selected),
        False,
        (),
    )


def print_reload_plan(plan: ReloadPlan, target: TmuxTarget) -> None:
    target_label = target.socket_name or target.socket_path or "default"
    print(f"tmux server: {target_label}")
    print("reload mode: " + ("all sessions" if plan.close_all else "selected sessions"))
    print(f"sessions to close: {', '.join(plan.session_names)}")
    print("tmuxp sessions to reload: " + ", ".join(workspace.session_name for workspace in plan.workspaces))
    if plan.unmanaged_sessions:
        print("sessions without tmuxp config: " + ", ".join(plan.unmanaged_sessions))


def confirm_reload() -> bool:
    if not sys.stdin.isatty():
        raise ReloadError("confirmation requires a terminal; use --yes for an explicit non-interactive reload")
    answer = input("Close all listed tmux sessions and reload the tmuxp sessions? [y/N] ")
    return answer.strip().lower() in {"y", "yes"}


def reload_sessions(plan: ReloadPlan, target: TmuxTarget) -> None:
    current_sessions = set(list_tmux_sessions(target))
    observed_sessions = set(plan.observed_sessions)
    if plan.close_all and current_sessions != observed_sessions:
        added = sorted(current_sessions - observed_sessions)
        removed = sorted(observed_sessions - current_sessions)
        changes: list[str] = []
        if added:
            changes.append("added: " + ", ".join(added))
        if removed:
            changes.append("removed: " + ", ".join(removed))
        raise ReloadError("session list changed after confirmation; reload aborted (" + "; ".join(changes) + ")")
    missing_selected = sorted(set(plan.session_names) - current_sessions)
    if missing_selected:
        raise ReloadError(
            "selected sessions changed after confirmation; reload aborted (missing: "
            + ", ".join(missing_selected)
            + ")"
        )

    if plan.close_all:
        print("Closing all tmux sessions...", flush=True)
        kill_commands = [build_tmux_command(target, "kill-server")]
    else:
        print("Closing selected tmux sessions...", flush=True)
        kill_commands = [
            build_tmux_command(target, "kill-session", "-t", f"={session_name}")
            for session_name in plan.session_names
        ]

    for kill_command in kill_commands:
        kill_result = subprocess.run(
            kill_command,
            text=True,
            capture_output=True,
            check=False,
        )
        if kill_result.returncode != 0 and not (plan.close_all and is_no_server_error(kill_result.stderr)):
            raise ReloadError(kill_result.stderr.strip() or f"{' '.join(kill_command)} failed")

    print("Loading tmuxp sessions...", flush=True)
    load_result = subprocess.run(build_tmuxp_load_command(target, plan.workspaces), check=False)
    if load_result.returncode != 0:
        raise ReloadError(f"tmuxp load failed with exit code {load_result.returncode}")

    actual_sessions = set(list_tmux_sessions(target))
    expected_sessions = {workspace.session_name for workspace in plan.workspaces}
    missing_sessions = sorted(expected_sessions - actual_sessions)
    if missing_sessions:
        raise ReloadError("tmuxp reload verification failed; missing sessions: " + ", ".join(missing_sessions))
    print("Reloaded tmuxp sessions: " + ", ".join(sorted(expected_sessions)), flush=True)


def default_log_path() -> Path:
    state_home = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    return state_home / "myfun" / "tmuxp-reload.log"


def worker_command(plan: ReloadPlan, target: TmuxTarget) -> list[str]:
    command = [sys.executable, str(Path(__file__).resolve()), "--_worker"]
    if target.socket_name:
        command.extend(["-L", target.socket_name])
    if target.socket_path:
        command.extend(["-S", target.socket_path])
    if plan.close_all:
        command.append("--_close_all")
    for session_name in plan.observed_sessions:
        command.extend(["--_observed_session", session_name])
    for session_name in plan.session_names:
        command.extend(["--_closing_session", session_name])
    for workspace in plan.workspaces:
        command.extend(["--_workspace", workspace.path, "--_session", workspace.session_name])
    return command


def launch_detached_worker(plan: ReloadPlan, target: TmuxTarget, log_path: Path) -> None:
    log_path = log_path.expanduser().resolve()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(log_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    environment = os.environ.copy()
    environment.pop("TMUX", None)
    environment.pop("TMUX_PANE", None)

    with os.fdopen(descriptor, "w", encoding="utf-8") as log_file:
        try:
            worker = subprocess.Popen(
                worker_command(plan, target),
                stdin=subprocess.DEVNULL,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                start_new_session=True,
                close_fds=True,
                env=environment,
            )
        except OSError as exc:
            raise ReloadError(f"failed to start detached reload worker: {exc}") from exc

    print(f"Reload worker started (pid {worker.pid}). This tmux client will close shortly.")
    print(f"Reload log: {log_path}")


def worker_plan(args: argparse.Namespace) -> ReloadPlan:
    workspace_paths = args._workspace or []
    session_names = args._session or []
    observed_sessions = args._observed_session or []
    closing_sessions = args._closing_session or []
    if (
        not workspace_paths
        or len(workspace_paths) != len(session_names)
        or not observed_sessions
        or not closing_sessions
    ):
        raise ReloadError("invalid detached worker plan")
    workspaces = tuple(
        TmuxpWorkspace(session_name, path, session_name)
        for path, session_name in zip(workspace_paths, session_names, strict=True)
    )
    return ReloadPlan(
        tuple(observed_sessions),
        tuple(closing_sessions),
        workspaces,
        args._close_all,
        (),
    )


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="tmuxp reload",
        description="Reload selected tmuxp sessions, or every active tmuxp session when no name is given.",
    )
    target = parser.add_mutually_exclusive_group()
    target.add_argument("-L", dest="socket_name", help="Target a named tmux socket.")
    target.add_argument("-S", dest="socket_path", help="Target a tmux socket path.")
    parser.add_argument("-y", "--yes", action="store_true", help="Skip the confirmation prompt.")
    parser.add_argument("--dry-run", action="store_true", help="Show the reload plan without closing sessions.")
    parser.add_argument(
        "--allow-unmanaged",
        action="store_true",
        help="Also close sessions that have no matching tmuxp workspace; they will not be restored.",
    )
    parser.add_argument("--log-file", type=Path, help="Detached worker log path.")
    parser.add_argument("--_worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--_workspace", action="append", help=argparse.SUPPRESS)
    parser.add_argument("--_session", action="append", help=argparse.SUPPRESS)
    parser.add_argument("--_observed_session", action="append", help=argparse.SUPPRESS)
    parser.add_argument("--_closing_session", action="append", help=argparse.SUPPRESS)
    parser.add_argument("--_close_all", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("sessions", nargs="*", metavar="SESSION", help="tmuxp workspace or session name to reload.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        ensure_commands()
        target = resolve_target(args.socket_name, args.socket_path, os.environ.get("TMUX"))

        if args._worker:
            time.sleep(0.35)
            reload_sessions(worker_plan(args), target)
            return 0

        session_names = list_tmux_sessions(target)
        if not session_names:
            raise ReloadError("no tmux sessions are running on the selected server")

        workspaces = list_tmuxp_workspaces()
        if args.sessions:
            if args.allow_unmanaged:
                raise ReloadError("--allow-unmanaged is only valid when reloading all sessions")
            plan = build_targeted_reload_plan(args.sessions, session_names, workspaces)
        else:
            plan = build_reload_plan(session_names, workspaces)
            if not plan.workspaces:
                raise ReloadError("none of the running sessions has a matching tmuxp workspace")
            if plan.unmanaged_sessions and not args.allow_unmanaged:
                names = ", ".join(plan.unmanaged_sessions)
                raise ReloadError(
                    f"refusing to close sessions without tmuxp configs: {names}; "
                    "use --allow-unmanaged only if losing them is intentional"
                )

        print_reload_plan(plan, target)
        if args.dry_run:
            return 0
        if not args.yes and not confirm_reload():
            print("Reload cancelled.")
            return 0

        if target_is_current_server(target, os.environ.get("TMUX")):
            launch_detached_worker(plan, target, args.log_file or default_log_path())
            return 0

        reload_sessions(plan, target)
        return 0
    except ReloadError as exc:
        print(f"tmuxp reload: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nReload cancelled.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
