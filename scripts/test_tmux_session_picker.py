#!/usr/bin/env python3
"""Tests for the tmux session picker helpers."""

from __future__ import annotations

import os
import unittest

from scripts.tmux_session_picker import (
    TmuxSession,
    TmuxWindow,
    build_attach_command,
    build_new_session_commands,
    build_window_commands,
    default_session_name,
    parse_tmux_sessions,
    parse_tmux_windows,
)


class TmuxSessionPickerTest(unittest.TestCase):
    def test_parse_tmux_sessions_reads_machine_format(self) -> None:
        output = (
            "$1\twork\t3\t1\t1783200000\t1783200300\n"
            "$2\tlogs\t1\t0\t1783190000\t1783190300\n"
        )

        self.assertEqual(
            parse_tmux_sessions(output),
            [
                TmuxSession("$1", "work", 3, True, 1783200000, 1783200300),
                TmuxSession("$2", "logs", 1, False, 1783190000, 1783190300),
            ],
        )

    def test_parse_tmux_sessions_skips_malformed_lines(self) -> None:
        output = "not-enough-fields\n$3\tapi\tbad\t0\t1783190000\t1783190300\n"

        self.assertEqual(parse_tmux_sessions(output), [])

    def test_parse_tmux_windows_reads_machine_format(self) -> None:
        output = (
            "$1\tnode-99\t@1\t1\tLab-\t0\t2\t1783200100\n"
            "$1\tnode-99\t@3\t3\tMyFun开发\t1\t1\t1783200300\n"
        )

        self.assertEqual(
            parse_tmux_windows(output),
            [
                TmuxWindow("$1", "node-99", "@1", 1, "Lab-", False, 2, 1783200100),
                TmuxWindow("$1", "node-99", "@3", 3, "MyFun开发", True, 1, 1783200300),
            ],
        )

    def test_build_attach_command_switches_inside_tmux(self) -> None:
        session = TmuxSession("$1", "work", 3, True, 1783200000, 1783200300)

        self.assertEqual(build_attach_command(session, inside_tmux=False), ["tmux", "attach-session", "-t", "work"])
        self.assertEqual(build_attach_command(session, inside_tmux=True), ["tmux", "switch-client", "-t", "work"])

    def test_build_new_session_commands_attach_or_switch(self) -> None:
        self.assertEqual(
            build_new_session_commands("scratch", inside_tmux=False),
            [["tmux", "new-session", "-s", "scratch"]],
        )
        self.assertEqual(
            build_new_session_commands("scratch", inside_tmux=True),
            [
                ["tmux", "new-session", "-d", "-s", "scratch"],
                ["tmux", "switch-client", "-t", "scratch"],
            ],
        )

    def test_build_window_commands_selects_window_before_entering_session(self) -> None:
        window = TmuxWindow("$1", "node-99", "@3", 3, "MyFun开发", True, 1, 1783200300)

        self.assertEqual(
            build_window_commands(window, inside_tmux=False),
            [
                ["tmux", "select-window", "-t", "@3"],
                ["tmux", "attach-session", "-t", "node-99"],
            ],
        )
        self.assertEqual(
            build_window_commands(window, inside_tmux=True),
            [
                ["tmux", "select-window", "-t", "@3"],
                ["tmux", "switch-client", "-t", "node-99"],
            ],
        )

    def test_default_session_name_uses_directory_and_timestamp(self) -> None:
        self.assertEqual(
            default_session_name("/Users/ok/github/myfun", 1783211700),
            "myfun-20260704-173500",
        )

    def test_default_session_name_falls_back_for_unsafe_directory(self) -> None:
        self.assertEqual(
            default_session_name(os.sep, 1783211700),
            "session-20260704-173500",
        )


if __name__ == "__main__":
    unittest.main()
