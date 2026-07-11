# Repository Guidelines

## Project Structure & Module Organization

This repository is a personal shell environment toolkit. Core files live in [`env/`](/Users/ok/github/myfun/env): [`env.sh`](/Users/ok/github/myfun/env/env.sh) is the entrypoint and loads logging, variables, PATH updates, tool initialization, functions, aliases, and other optional settings. Keep related behavior in the matching file, for example PATH changes in [`env_path.sh`](/Users/ok/github/myfun/env/env_path.sh) and command helpers in [`env_functions.sh`](/Users/ok/github/myfun/env/env_functions.sh). Reference material lives in [`docs/`](/Users/ok/github/myfun/docs), and [`openclaw-run`](/Users/ok/github/myfun/openclaw-run) is a standalone helper script for OpenClaw setup and launch.

## Build, Test, and Development Commands

There is no build system for the env scripts; validation is shell-based.

- `source /Users/ok/github/myfun/env/env.sh`: load the environment in an interactive shell.
- `zsh -lc 'source /Users/ok/github/myfun/env/env.sh'`: verify the full initialization exits cleanly.
- `rg -n "NAME" env docs`: trace variables, functions, or path references before changing them.
- `./openclaw-run`: update, build, and relink the local OpenClaw toolchain.

## Coding Style & Naming Conventions

Follow [`docs/CODE_CONVENTIONS.md`](/Users/ok/github/myfun/docs/CODE_CONVENTIONS.md). Shell files use lowercase snake_case names such as `env_aliases.sh`; environment variables use uppercase snake_case; functions use lowercase snake_case. Prefer double-quoted expansions like `"$HOME"` and command substitution with `$(...)`. Shell indentation should stay consistent at 2 spaces. For Python helpers, follow PEP 8, 4-space indentation, and a max line length of 120.

## Testing Guidelines

This repository currently relies on manual verification rather than an automated test suite. After editing env files, run `zsh -lc 'source .../env.sh'` and test the affected commands directly. When removing old paths, confirm them with `[ -e /path ]` or `command -v tool` before deletion. Include brief verification notes in your PR or commit summary.

## Commit & Pull Request Guidelines

Recent history favors focused commits and mostly uses Conventional Commit prefixes, often with Chinese subjects, for example `refactor: 精简 AI 命令别名并补充 pnpm 懒加载`. Prefer `feat:`, `fix:`, `refactor:`, and `docs:`. PRs should explain why the environment changed, list touched files under `env/`, and include the exact verification command you ran. Add screenshots only when changing user-facing docs or terminal UX.

## Security & Configuration Tips

Do not introduce new secrets, tokens, or machine-specific absolute paths unless unavoidable. Prefer `$HOME`-based paths and guard optional local tooling with `command -v` or `[ -e ... ]` checks so the setup remains safe on new machines.
