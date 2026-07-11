#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_ROOT="$ROOT_DIR/.tmp/git-delete-branch-test-$$"
REMOTE_DIR="$TEST_ROOT/remote.git"
WORK_DIR="$TEST_ROOT/work"
STUB_BIN="$TEST_ROOT/bin"
REAL_GIT="$(command -v git)"

export PATH="$ROOT_DIR:$PATH"

mkdir -p "$STUB_BIN"

cat > "$STUB_BIN/git" <<'STUB'
#!/usr/bin/env bash
if [ "$1" = "ls-remote" ]; then
  printf "test git wrapper: git ls-remote is forbidden here\n" >&2
  exit 99
fi

exec "$GIT_DELETE_BRANCH_TEST_REAL_GIT" "$@"
STUB
chmod +x "$STUB_BIN/git"

git init --bare "$REMOTE_DIR" >/dev/null
git init -b main "$WORK_DIR" >/dev/null 2>&1 || {
  git init "$WORK_DIR" >/dev/null
  git -C "$WORK_DIR" checkout -b main >/dev/null
}
git -C "$WORK_DIR" config user.email "git-delete-branch-test@example.com"
git -C "$WORK_DIR" config user.name "Git Delete Branch Test"
git -C "$WORK_DIR" remote add origin "$REMOTE_DIR"

printf "base\n" > "$WORK_DIR/README.md"
git -C "$WORK_DIR" add README.md
git -C "$WORK_DIR" commit -m "chore: initial commit" >/dev/null
git -C "$WORK_DIR" push -u origin main >/dev/null

git -C "$WORK_DIR" checkout -b delete-me >/dev/null
printf "delete\n" > "$WORK_DIR/delete.txt"
git -C "$WORK_DIR" add delete.txt
git -C "$WORK_DIR" commit -m "test: add delete branch fixture" >/dev/null
git -C "$WORK_DIR" push -u origin delete-me >/dev/null
git -C "$WORK_DIR" checkout main >/dev/null

git -C "$WORK_DIR" delete-branch delete-me

test -z "$(git -C "$WORK_DIR" branch --list delete-me)"
if git -C "$REMOTE_DIR" rev-parse --verify refs/heads/delete-me >/dev/null 2>&1; then
  exit 1
fi

if git -C "$WORK_DIR" delete-branch main >/dev/null 2>&1; then
  exit 1
fi
git -C "$WORK_DIR" show-ref --verify refs/heads/main >/dev/null
if git -C "$WORK_DIR" delete-branch origin/main >/dev/null 2>&1; then
  exit 1
fi
git -C "$WORK_DIR" show-ref --verify refs/heads/main >/dev/null
git -C "$REMOTE_DIR" rev-parse --verify refs/heads/main >/dev/null

git -C "$WORK_DIR" checkout -b feature/dev >/dev/null
printf "current\n" > "$WORK_DIR/current.txt"
git -C "$WORK_DIR" add current.txt
git -C "$WORK_DIR" commit -m "test: add current branch fixture" >/dev/null
git -C "$WORK_DIR" push -u origin feature/dev >/dev/null

printf "\r" | PATH="$STUB_BIN:$PATH" GIT_DELETE_BRANCH_TEST_REAL_GIT="$REAL_GIT" GIT_DELETE_BRANCH_FORCE_TUI=1 \
  git -C "$WORK_DIR" delete-branch

test -n "$(git -C "$WORK_DIR" branch --list feature/dev)"
if git -C "$REMOTE_DIR" rev-parse --verify refs/heads/feature/dev >/dev/null 2>&1; then
  exit 1
fi
git -C "$WORK_DIR" checkout main >/dev/null

git -C "$WORK_DIR" checkout -b keep-choice >/dev/null
printf "keep\n" > "$WORK_DIR/keep.txt"
git -C "$WORK_DIR" add keep.txt
git -C "$WORK_DIR" commit -m "test: add keep branch fixture" >/dev/null
git -C "$WORK_DIR" push -u origin keep-choice >/dev/null
git -C "$WORK_DIR" checkout main >/dev/null

git -C "$WORK_DIR" checkout -b prompt-delete >/dev/null
printf "prompt\n" > "$WORK_DIR/prompt.txt"
git -C "$WORK_DIR" add prompt.txt
git -C "$WORK_DIR" commit -m "test: add prompt delete fixture" >/dev/null
git -C "$WORK_DIR" push -u origin prompt-delete >/dev/null
git -C "$WORK_DIR" checkout main >/dev/null

printf "\033[B\033[B\r" | PATH="$STUB_BIN:$PATH" GIT_DELETE_BRANCH_TEST_REAL_GIT="$REAL_GIT" GIT_DELETE_BRANCH_FORCE_TUI=1 \
  git -C "$WORK_DIR" delete-branch

test -z "$(git -C "$WORK_DIR" branch --list prompt-delete)"
if git -C "$REMOTE_DIR" rev-parse --verify refs/heads/prompt-delete >/dev/null 2>&1; then
  exit 1
fi
test -n "$(git -C "$WORK_DIR" branch --list keep-choice)"
git -C "$REMOTE_DIR" rev-parse --verify refs/heads/keep-choice >/dev/null
