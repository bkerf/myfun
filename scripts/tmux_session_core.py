#!/usr/bin/env python3
"""Core tmux session/window helpers for tms."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime


SESSION_FORMAT = (
    "#{session_id}\t#{session_name}\t#{session_windows}\t"
    "#{session_attached}\t#{session_created}\t#{session_activity}"
)

WINDOW_FORMAT = (
    "#{session_id}\t#{session_name}\t#{window_id}\t#{window_index}\t"
    "#{window_name}\t#{window_active}\t#{window_panes}\t#{window_activity}"
)


class UserFacingError(RuntimeError):
    """An error that can be shown directly to the command user."""


@dataclass(frozen=True)
class TmuxSession:
    session_id: str
    name: str
    windows: int
    attached: bool
    created: int
    activity: int


@dataclass(frozen=True)
class TmuxWindow:
    session_id: str
    session_name: str
    window_id: str
    index: int
    name: str
    active: bool
    panes: int
    activity: int


@dataclass(frozen=True)
class PickerAction:
    kind: str
    session: TmuxSession | None = None
    window: TmuxWindow | None = None
    name: str | None = None


def parse_tmux_sessions(output: str) -> list[TmuxSession]:
    sessions: list[TmuxSession] = []

    for line in output.splitlines():
        parts = line.split("\t")
        if len(parts) != 6:
            continue

        session_id, name, windows_raw, attached_raw, created_raw, activity_raw = parts
        try:
            windows = int(windows_raw)
            attached = int(attached_raw) > 0
            created = int(created_raw)
            activity = int(activity_raw)
        except ValueError:
            continue

        sessions.append(TmuxSession(session_id, name, windows, attached, created, activity))

    return sessions


def parse_tmux_windows(output: str) -> list[TmuxWindow]:
    windows: list[TmuxWindow] = []

    for line in output.splitlines():
        parts = line.split("\t")
        if len(parts) != 8:
            continue

        session_id, session_name, window_id, index_raw, name, active_raw, panes_raw, activity_raw = parts
        try:
            index = int(index_raw)
            active = int(active_raw) > 0
            panes = int(panes_raw)
            activity = int(activity_raw)
        except ValueError:
            continue

        windows.append(TmuxWindow(session_id, session_name, window_id, index, name, active, panes, activity))

    return windows


def list_tmux_sessions() -> list[TmuxSession]:
    ensure_tmux()
    result = subprocess.run(
        ["tmux", "list-sessions", "-F", SESSION_FORMAT],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        return parse_tmux_sessions(result.stdout)

    stderr = result.stderr.strip()
    if "no server running" in stderr.lower():
        return []
    raise UserFacingError(stderr or "tmux list-sessions failed")


def list_tmux_windows() -> list[TmuxWindow]:
    ensure_tmux()
    result = subprocess.run(
        ["tmux", "list-windows", "-a", "-F", WINDOW_FORMAT],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        return parse_tmux_windows(result.stdout)

    stderr = result.stderr.strip()
    if "no server running" in stderr.lower():
        return []
    raise UserFacingError(stderr or "tmux list-windows failed")


def ensure_tmux() -> None:
    if not shutil.which("tmux"):
        raise UserFacingError("tmux is not installed or is not on PATH")


def build_attach_command(session: TmuxSession, inside_tmux: bool) -> list[str]:
    if inside_tmux:
        return ["tmux", "switch-client", "-t", session.name]
    return ["tmux", "attach-session", "-t", session.name]


def build_new_session_commands(name: str, inside_tmux: bool) -> list[list[str]]:
    if inside_tmux:
        return [
            ["tmux", "new-session", "-d", "-s", name],
            ["tmux", "switch-client", "-t", name],
        ]
    return [["tmux", "new-session", "-s", name]]


def build_window_commands(window: TmuxWindow, inside_tmux: bool) -> list[list[str]]:
    enter_command = ["tmux", "switch-client", "-t", window.session_name]
    if not inside_tmux:
        enter_command = ["tmux", "attach-session", "-t", window.session_name]
    return [
        ["tmux", "select-window", "-t", window.window_id],
        enter_command,
    ]


def default_session_name(cwd: str, timestamp: int | None = None) -> str:
    stamp = datetime.fromtimestamp(timestamp if timestamp is not None else time.time()).strftime("%Y%m%d-%H%M%S")
    directory = os.path.basename(os.path.abspath(cwd))
    safe_directory = re.sub(r"[^A-Za-z0-9_.-]+", "-", directory).strip("._-")
    prefix = safe_directory or "session"
    return f"{prefix}-{stamp}"


def validate_session_name(name: str) -> str | None:
    if not name:
        return "session name cannot be empty"
    if "\n" in name or "\t" in name:
        return "session name cannot contain tabs or newlines"
    if ":" in name:
        return "session name cannot contain ':'"
    return None


def truncate(text: str, width: int) -> str:
    if width <= 0:
        return ""
    if len(text) <= width:
        return text
    if width == 1:
        return "."
    return text[: width - 1] + "."


def age_text(timestamp: int, now: int | None = None) -> str:
    seconds = max(0, int(now if now is not None else time.time()) - timestamp)
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    if hours < 48:
        return f"{hours}h"
    return f"{hours // 24}d"


def print_session_tree(sessions: list[TmuxSession], windows: list[TmuxWindow]) -> None:
    if not sessions:
        print("No tmux sessions.")
        return

    windows_by_session: dict[str, list[TmuxWindow]] = {}
    for window in windows:
        windows_by_session.setdefault(window.session_id, []).append(window)

    for session in sessions:
        state = "attached" if session.attached else "detached"
        print(f"{session.name} ({session.windows} windows, {state}, {age_text(session.activity)} ago)")
        for window in sorted(windows_by_session.get(session.session_id, []), key=lambda item: item.index):
            marker = "*" if window.active else " "
            print(f"  {marker} {window.index}: {window.name} ({window.panes} panes, {age_text(window.activity)} ago)")
