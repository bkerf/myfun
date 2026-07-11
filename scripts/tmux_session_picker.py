#!/usr/bin/env python3
"""Interactive tmux session picker.

Usage:
  tms
  tms --list
"""

from __future__ import annotations

import argparse
import curses
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    from scripts.tmux_session_core import (
        PickerAction,
        TmuxSession,
        TmuxWindow,
        UserFacingError,
        age_text,
        build_attach_command,
        build_new_session_commands,
        build_window_commands,
        default_session_name,
        list_tmux_sessions,
        list_tmux_windows,
        parse_tmux_sessions,
        parse_tmux_windows,
        print_session_tree,
        truncate,
        validate_session_name,
    )
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from scripts.tmux_session_core import (
        PickerAction,
        TmuxSession,
        TmuxWindow,
        UserFacingError,
        age_text,
        build_attach_command,
        build_new_session_commands,
        build_window_commands,
        default_session_name,
        list_tmux_sessions,
        list_tmux_windows,
        parse_tmux_sessions,
        parse_tmux_windows,
        print_session_tree,
        truncate,
        validate_session_name,
    )


@dataclass(frozen=True)
class PickerRow:
    kind: str
    session: TmuxSession | None = None
    window: TmuxWindow | None = None


def safe_curs_set(value: int) -> None:
    try:
        curses.curs_set(value)
    except curses.error:
        pass


class TmuxPicker:
    def __init__(self, stdscr: curses.window) -> None:
        self.stdscr = stdscr
        self.sessions: list[TmuxSession] = []
        self.windows: list[TmuxWindow] = []
        self.rows: list[PickerRow] = [PickerRow("new")]
        self.selected = 0
        self.scroll = 0
        self.status = ""

    def run(self) -> PickerAction | None:
        self.configure_terminal()
        self.refresh()

        while True:
            self.draw()
            key = self.stdscr.getch()

            if key in (27, ord("q"), ord("Q")):
                return None
            if key == curses.KEY_UP:
                self.move_selection(-1)
            elif key == curses.KEY_DOWN:
                self.move_selection(1)
            elif key in (curses.KEY_ENTER, 10, 13):
                action = self.enter_selection()
                if action is not None:
                    return action
            elif key in (ord("n"), ord("N")):
                action = self.new_session_action()
                if action is not None:
                    return action
            elif key in (ord("d"), ord("D"), ord("x"), ord("X"), curses.KEY_DC):
                self.delete_selection()
            elif key in (ord("r"), ord("R")):
                self.refresh()

    def configure_terminal(self) -> None:
        self.stdscr.keypad(True)
        curses.noecho()
        curses.cbreak()
        safe_curs_set(0)
        if curses.has_colors():
            curses.start_color()
            try:
                curses.use_default_colors()
            except curses.error:
                pass

    def total_rows(self) -> int:
        return len(self.rows)

    def move_selection(self, delta: int) -> None:
        self.selected = min(max(self.selected + delta, 0), self.total_rows() - 1)

    def clamp_selection(self) -> None:
        self.selected = min(max(self.selected, 0), max(0, self.total_rows() - 1))

    def refresh(self) -> None:
        try:
            self.sessions = list_tmux_sessions()
            self.windows = list_tmux_windows() if self.sessions else []
            self.rows = self.build_rows()
            self.status = f"{len(self.sessions)} session(s), {len(self.windows)} window(s)"
        except UserFacingError as exc:
            self.sessions = []
            self.windows = []
            self.rows = [PickerRow("new")]
            self.status = str(exc)
        self.clamp_selection()

    def build_rows(self) -> list[PickerRow]:
        rows = [PickerRow("new")]
        windows_by_session: dict[str, list[TmuxWindow]] = {}
        for window in self.windows:
            windows_by_session.setdefault(window.session_id, []).append(window)

        for session in self.sessions:
            rows.append(PickerRow("session", session=session))
            for window in sorted(windows_by_session.get(session.session_id, []), key=lambda item: item.index):
                rows.append(PickerRow("window", window=window))
        return rows

    def enter_selection(self) -> PickerAction | None:
        row = self.rows[self.selected]
        if row.kind == "new":
            return self.new_session_action()
        if row.kind == "window" and row.window is not None:
            return PickerAction("window", window=row.window)
        if row.kind == "session" and row.session is not None:
            return PickerAction("attach", session=row.session)
        return None

    def new_session_action(self) -> PickerAction | None:
        default_name = default_session_name(os.getcwd())
        name = self.prompt_text("New session name", default_name)
        if name is None:
            self.status = "New session cancelled"
            return None

        name = name.strip()
        error = validate_session_name(name)
        if error:
            self.status = error
            return None
        if any(session.name == name for session in self.sessions):
            self.status = f"Session already exists: {name}"
            return None
        return PickerAction("new", name=name)

    def delete_selection(self) -> None:
        row = self.rows[self.selected]
        if row.kind == "new":
            self.status = "Select a session or window before deleting"
            return

        if row.kind == "session" and row.session is not None:
            self.kill_session(row.session)
            return
        if row.kind == "window" and row.window is not None:
            self.kill_window(row.window)
            return

    def kill_session(self, session: TmuxSession) -> None:
        if not self.confirm(f"Kill session '{session.name}'? y/N"):
            self.status = "Delete cancelled"
            return

        result = subprocess.run(
            ["tmux", "kill-session", "-t", session.name],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            self.status = result.stderr.strip() or f"Failed to kill session: {session.name}"
            return

        status = f"Killed session: {session.name}"
        self.refresh()
        self.status = status

    def kill_window(self, window: TmuxWindow) -> None:
        label = f"{window.session_name}:{window.index} {window.name}"
        if not self.confirm(f"Kill window '{label}'? y/N"):
            self.status = "Delete cancelled"
            return

        result = subprocess.run(
            ["tmux", "kill-window", "-t", window.window_id],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            self.status = result.stderr.strip() or f"Failed to kill window: {label}"
            return

        status = f"Killed window: {label}"
        self.refresh()
        self.status = status

    def prompt_text(self, prompt: str, default: str) -> str | None:
        height, width = self.stdscr.getmaxyx()
        label = f"{prompt} [{default}]: "
        safe_curs_set(1)
        curses.echo()
        try:
            self.stdscr.move(height - 1, 0)
            self.stdscr.clrtoeol()
            self.addstr(height - 1, 0, label, curses.A_BOLD)
            max_length = max(1, width - len(label) - 1)
            raw = self.stdscr.getstr(height - 1, min(len(label), width - 1), max_length)
        except (KeyboardInterrupt, curses.error):
            return None
        finally:
            curses.noecho()
            safe_curs_set(0)

        value = raw.decode(errors="ignore").strip()
        return value or default

    def confirm(self, prompt: str) -> bool:
        height, _width = self.stdscr.getmaxyx()
        self.stdscr.move(height - 1, 0)
        self.stdscr.clrtoeol()
        self.addstr(height - 1, 0, prompt, curses.A_BOLD)
        key = self.stdscr.getch()
        return key in (ord("y"), ord("Y"))

    def draw(self) -> None:
        self.stdscr.erase()
        height, width = self.stdscr.getmaxyx()
        if height < 6 or width < 24:
            self.addstr(0, 0, "Terminal too small")
            self.stdscr.refresh()
            return

        self.addstr(0, 0, "tms - tmux sessions", curses.A_BOLD)
        self.addstr(1, 0, "Enter attach/switch | n new session | d delete | r refresh | q quit")
        self.addstr(3, 0, "Session")
        self.addstr(3, max(10, min(width - 43, width // 2)), "Win/Panes  State     Activity")

        visible_rows = max(1, height - 5)
        if self.selected < self.scroll:
            self.scroll = self.selected
        elif self.selected >= self.scroll + visible_rows:
            self.scroll = self.selected - visible_rows + 1

        end_row = min(self.total_rows(), self.scroll + visible_rows)
        for index in range(self.scroll, end_row):
            y = 4 + index - self.scroll
            selected = index == self.selected
            attr = curses.A_REVERSE if selected else curses.A_NORMAL
            self.addstr(y, 0, self.row_text(index, width), attr)

        self.addstr(height - 1, 0, truncate(self.status, width - 1), curses.A_DIM)
        self.stdscr.refresh()

    def row_text(self, index: int, width: int) -> str:
        row = self.rows[index]
        if row.kind == "new":
            return truncate("[+] New session", width - 1)

        if row.kind == "session" and row.session is not None:
            session = row.session
            state = "attached" if session.attached else "detached"
            suffix = f"{session.windows:>3} win    {state:<8}  {age_text(session.activity)} ago"
            name_width = max(10, width - len(suffix) - 3)
            return truncate(f"{session.name:<{name_width}} {suffix}", width - 1)

        if row.kind == "window" and row.window is not None:
            window = row.window
            marker = "*" if window.active else " "
            name = f"  {marker} {window.index}: {window.name}"
            suffix = f"{window.panes:>3} pane   window    {age_text(window.activity)} ago"
            name_width = max(10, width - len(suffix) - 3)
            return truncate(f"{name:<{name_width}} {suffix}", width - 1)

        return ""

    def addstr(self, y: int, x: int, text: str, attr: int = curses.A_NORMAL) -> None:
        height, width = self.stdscr.getmaxyx()
        if y < 0 or y >= height or x < 0 or x >= width:
            return
        try:
            self.stdscr.addstr(y, x, truncate(text, width - x - 1), attr)
        except curses.error:
            pass


def choose_interactively() -> PickerAction | None:
    return curses.wrapper(lambda stdscr: TmuxPicker(stdscr).run())


def execute_action(action: PickerAction | None) -> int:
    if action is None:
        return 0

    inside_tmux = bool(os.environ.get("TMUX"))
    if action.kind == "attach" and action.session is not None:
        command = build_attach_command(action.session, inside_tmux)
        return exec_command(command)
    if action.kind == "window" and action.window is not None:
        commands = build_window_commands(action.window, inside_tmux)
        for command in commands[:-1]:
            result = subprocess.run(command, check=False)
            if result.returncode != 0:
                return result.returncode
        return exec_command(commands[-1])
    if action.kind == "new" and action.name is not None:
        commands = build_new_session_commands(action.name, inside_tmux)
        for command in commands[:-1]:
            result = subprocess.run(command, check=False)
            if result.returncode != 0:
                return result.returncode
        return exec_command(commands[-1])

    raise UserFacingError(f"Unknown action: {action.kind}")


def exec_command(command: list[str]) -> int:
    try:
        os.execvp(command[0], command)
    except FileNotFoundError:
        print(f"Command not found: {command[0]}", file=sys.stderr)
        return 127
    except OSError as exc:
        print(f"Failed to execute {' '.join(command)}: {exc}", file=sys.stderr)
        return 1
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Interactive tmux session picker.")
    parser.add_argument("--list", action="store_true", help="Print current sessions without opening the UI.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    try:
        if args.list:
            sessions = list_tmux_sessions()
            print_session_tree(sessions, list_tmux_windows() if sessions else [])
            return 0

        if not sys.stdin.isatty() or not sys.stdout.isatty():
            raise UserFacingError("tms requires an interactive terminal; use --list for non-interactive checks")

        return execute_action(choose_interactively())
    except KeyboardInterrupt:
        return 130
    except UserFacingError as exc:
        print(f"tms: {exc}", file=sys.stderr)
        return 1
    except curses.error as exc:
        print(f"tms: terminal UI failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
