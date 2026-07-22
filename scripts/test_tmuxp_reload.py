#!/usr/bin/env python3
"""Tests for the tmuxp reload helper."""

from __future__ import annotations

import json
import os
import unittest
from contextlib import redirect_stdout
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from scripts.tmuxp_reload import (
    ReloadError,
    TmuxTarget,
    TmuxpWorkspace,
    build_reload_plan,
    build_targeted_reload_plan,
    build_tmux_command,
    build_tmuxp_load_command,
    is_no_server_error,
    parse_tmux_socket_path,
    parse_tmuxp_workspaces,
    reload_sessions,
    resolve_target,
    target_is_current_server,
    worker_command,
)


class TmuxpReloadTest(unittest.TestCase):
    def test_parse_tmux_socket_path(self) -> None:
        value = "/private/tmp/tmux-501/default,1234,0"

        self.assertEqual(parse_tmux_socket_path(value), "/private/tmp/tmux-501/default")
        self.assertIsNone(parse_tmux_socket_path("invalid"))
        self.assertIsNone(parse_tmux_socket_path(None))

    def test_resolve_target_prefers_explicit_socket(self) -> None:
        tmux_value = "/private/tmp/tmux-501/default,1234,0"

        self.assertEqual(resolve_target("reload-test", None, tmux_value), TmuxTarget(socket_name="reload-test"))
        self.assertEqual(resolve_target(None, "~/reload.sock", tmux_value).socket_path, os.path.expanduser("~/reload.sock"))
        self.assertEqual(
            resolve_target(None, None, tmux_value),
            TmuxTarget(socket_path="/private/tmp/tmux-501/default"),
        )

    def test_target_is_current_server(self) -> None:
        tmux_value = "/private/tmp/tmux-501/default,1234,0"

        self.assertTrue(target_is_current_server(TmuxTarget(socket_name="default"), tmux_value))
        self.assertTrue(
            target_is_current_server(TmuxTarget(socket_path="/private/tmp/tmux-501/default"), tmux_value)
        )
        self.assertFalse(target_is_current_server(TmuxTarget(socket_name="other"), tmux_value))

    def test_parse_tmuxp_workspaces(self) -> None:
        output = json.dumps(
            {
                "workspaces": [
                    {
                        "name": "api",
                        "path": "~/.config/tmuxp/api.yaml",
                        "session_name": "api-dev",
                    },
                    {"name": "incomplete"},
                ]
            }
        )

        self.assertEqual(
            parse_tmuxp_workspaces(output),
            [
                TmuxpWorkspace(
                    "api",
                    os.path.expanduser("~/.config/tmuxp/api.yaml"),
                    "api-dev",
                )
            ],
        )

        with self.assertRaisesRegex(ReloadError, "JSON root must be an object"):
            parse_tmuxp_workspaces("[]")

    def test_build_reload_plan_preserves_running_session_order(self) -> None:
        workspaces = [
            TmuxpWorkspace("two", "/config/two.yaml", "session-two"),
            TmuxpWorkspace("one", "/config/one.yaml", "session-one"),
        ]

        plan = build_reload_plan(["session-one", "scratch", "session-two"], workspaces)

        self.assertEqual(plan.session_names, ("session-one", "scratch", "session-two"))
        self.assertEqual(plan.observed_sessions, ("session-one", "scratch", "session-two"))
        self.assertTrue(plan.close_all)
        self.assertEqual([workspace.name for workspace in plan.workspaces], ["one", "two"])
        self.assertEqual(plan.unmanaged_sessions, ("scratch",))

    def test_build_targeted_reload_plan_selects_only_requested_session(self) -> None:
        workspaces = [
            TmuxpWorkspace("okpay", "/config/okpay.yaml", "okpay"),
            TmuxpWorkspace("api", "/config/api.yaml", "aicardapi"),
        ]

        plan = build_targeted_reload_plan(["okpay"], ["aicardapi", "okpay"], workspaces)

        self.assertEqual(plan.observed_sessions, ("aicardapi", "okpay"))
        self.assertEqual(plan.session_names, ("okpay",))
        self.assertEqual([workspace.name for workspace in plan.workspaces], ["okpay"])
        self.assertFalse(plan.close_all)

    def test_build_targeted_reload_plan_requires_running_session(self) -> None:
        workspace = TmuxpWorkspace("okpay", "/config/okpay.yaml", "okpay")

        with self.assertRaisesRegex(ReloadError, "tmux session is not running"):
            build_targeted_reload_plan(["okpay"], ["aicardapi"], [workspace])

    def test_build_reload_plan_rejects_duplicate_session_definitions(self) -> None:
        workspaces = [
            TmuxpWorkspace("one", "/config/one.yaml", "shared"),
            TmuxpWorkspace("two", "/config/two.yaml", "shared"),
        ]

        with self.assertRaisesRegex(ReloadError, "multiple tmuxp workspaces"):
            build_reload_plan(["shared"], workspaces)

    def test_build_commands_include_socket_and_all_workspaces(self) -> None:
        target = TmuxTarget(socket_name="reload-test")
        workspaces = [
            TmuxpWorkspace("one", "/config/one.yaml", "one"),
            TmuxpWorkspace("two", "/config/two.yaml", "two"),
        ]

        self.assertEqual(
            build_tmux_command(target, "kill-server"),
            ["tmux", "-L", "reload-test", "kill-server"],
        )
        self.assertEqual(
            build_tmuxp_load_command(target, workspaces),
            [
                "tmuxp",
                "load",
                "--yes",
                "-d",
                "-L",
                "reload-test",
                "/config/one.yaml",
                "/config/two.yaml",
            ],
        )

        plan = build_reload_plan(["one", "scratch", "two"], workspaces)
        self.assertEqual(
            worker_command(plan, target)[2:],
            [
                "--_worker",
                "-L",
                "reload-test",
                "--_close_all",
                "--_observed_session",
                "one",
                "--_observed_session",
                "scratch",
                "--_observed_session",
                "two",
                "--_closing_session",
                "one",
                "--_closing_session",
                "scratch",
                "--_closing_session",
                "two",
                "--_workspace",
                "/config/one.yaml",
                "--_session",
                "one",
                "--_workspace",
                "/config/two.yaml",
                "--_session",
                "two",
            ],
        )

    def test_no_server_errors_are_recognized(self) -> None:
        self.assertTrue(is_no_server_error("no server running on /tmp/tmux/default"))
        self.assertTrue(is_no_server_error("error connecting to /tmp/test (No such file or directory)"))
        self.assertFalse(is_no_server_error("error connecting to /tmp/test (Permission denied)"))
        self.assertFalse(is_no_server_error("permission denied"))

    def test_reload_aborts_before_kill_when_session_snapshot_changes(self) -> None:
        workspace = TmuxpWorkspace("one", "/config/one.yaml", "one")
        plan = build_reload_plan(["one"], [workspace])

        with (
            patch("scripts.tmuxp_reload.list_tmux_sessions", return_value=["one", "new-session"]),
            patch("scripts.tmuxp_reload.subprocess.run") as run,
            self.assertRaisesRegex(ReloadError, "session list changed after confirmation"),
        ):
            reload_sessions(plan, TmuxTarget())

        run.assert_not_called()

    def test_targeted_reload_kills_only_selected_session(self) -> None:
        workspaces = [
            TmuxpWorkspace("okpay", "/config/okpay.yaml", "okpay"),
            TmuxpWorkspace("api", "/config/api.yaml", "aicardapi"),
        ]
        plan = build_targeted_reload_plan(["okpay"], ["aicardapi", "okpay"], workspaces)
        completed = SimpleNamespace(returncode=0, stderr="")

        with (
            patch(
                "scripts.tmuxp_reload.list_tmux_sessions",
                side_effect=[["aicardapi", "okpay"], ["aicardapi", "okpay"]],
            ),
            patch("scripts.tmuxp_reload.subprocess.run", return_value=completed) as run,
            redirect_stdout(StringIO()),
        ):
            reload_sessions(plan, TmuxTarget(socket_name="test"))

        self.assertEqual(
            run.call_args_list[0].args[0],
            ["tmux", "-L", "test", "kill-session", "-t", "=okpay"],
        )
        self.assertEqual(run.call_args_list[1].args[0][0:4], ["tmuxp", "load", "--yes", "-d"])


if __name__ == "__main__":
    unittest.main()
